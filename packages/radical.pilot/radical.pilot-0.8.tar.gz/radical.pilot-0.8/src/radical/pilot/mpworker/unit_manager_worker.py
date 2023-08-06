#pylint: disable=C0301, C0103, W0212

"""
.. module:: radical.pilot.mpworker.unit_manager_worker
   :platform: Unix
   :synopsis: Implements a multiprocessing worker backend for
              the UnitManager class.

.. moduleauthor:: Ole Weidner <ole.weidner@rutgers.edu>
"""

__copyright__ = "Copyright 2013-2014, http://radical.rutgers.edu"
__license__ = "MIT"

import os
import time
import Queue
import weakref
import threading

from multiprocessing import Pool

from radical.pilot.states import *

from radical.utils import which
from radical.pilot.utils.logger import logger

from radical.pilot.mpworker.filetransfer import transfer_input_func


# ----------------------------------------------------------------------------
#
class UnitManagerWorker(threading.Thread):
    """UnitManagerWorker is a threading worker that handles backend
       interaction for the UnitManager class.
    """

    # ------------------------------------------------------------------------
    #
    def __init__(self, unit_manager_uid, unit_manager_data, db_connection):

        # Multithreading stuff
        threading.Thread.__init__(self)
        self.daemon = True

        # Stop event can be set to terminate the main loop
        self._stop = threading.Event()
        self._stop.clear()

        # Initialized is set, once the run loop has pulled status
        # at least once. Other functions use it as a guard.
        self._initialized = threading.Event()
        self._initialized.clear()

        # The transfer worker pool is a multiprocessing pool that executes
        # concurrent file transfer requests.
        self._worker_pool = Pool(2)

        # The shard_data_manager handles data exchange between the worker
        # process and the API objects. The communication is unidirectional:
        # workers WRITE to _shared_data and API methods READ from _shared_data.
        # The strucuture of _shared_data is as follows:
        #
        # { unit1_uid: MongoDB document (dict),
        #   unit2_uid: MongoDB document (dict),
        #   ...
        # }
        #
        self._shared_data = dict()
        self._shared_data_lock = threading.Lock()

        # The manager-level list.
        #
        self._manager_callbacks = list()

        # The MongoDB database handle.
        self._db = db_connection

        self._um_id = unit_manager_uid

        # The different command queues hold pending operations
        # that are passed to the worker. Queues are inspected during
        # runtime in the run() loop and the worker acts upon them accordingly.
        self._transfer_requests = Queue.Queue()

        if unit_manager_uid is None:
            # Try to register the UnitManager with the database.
            self._um_id = self._db.insert_unit_manager(
                unit_manager_data=unit_manager_data)
        else:
            self._um_id = unit_manager_uid

        self.name = 'UMWThread-%s' % self._um_id

    # ------------------------------------------------------------------------
    #
    def __del__(self):
        if os.getenv("RADICALPILOT_GCDEBUG", None) is not None:
            logger.debug("GCDEBUG __del__(): UnitManagerWorker '%s'." % self._um_id)

    # ------------------------------------------------------------------------
    #
    @classmethod
    def uid_exists(cls, db_connection, unit_manager_uid):
        """Checks wether a particular unit manager UID exists.
        """
        exists = False

        if unit_manager_uid in db_connection.list_unit_manager_uids():
            exists = True

        return exists

    # ------------------------------------------------------------------------
    #
    @property
    def unit_manager_uid(self):
        """Returns the uid of the associated UnitManager
        """
        return self._um_id

    # ------------------------------------------------------------------------
    #
    def stop(self):
        """stop() signals the process to finish up and terminate.
        """
        self._stop.set()
        self.join()
        logger.debug("Worker thread (ID: %s[%s]) for UnitManager %s stopped." %
                    (self.name, self.ident, self._um_id))

    # ------------------------------------------------------------------------
    #
    def get_compute_unit_data(self, unit_uid):
        """Retruns the raw data (json dicts) of one or more ComputeUnits
           registered with this Worker / UnitManager
        """
        # Wait for the initialized event to assert proper operation.
        self._initialized.wait()

        return self._shared_data[unit_uid]["data"]

    # ------------------------------------------------------------------------
    #
    def call_callbacks(self, unit_id, new_state):
        """Wrapper function to call all all relevant callbacks, on unit-level
        as well as manager-level.
        """
        for cb in self._shared_data[unit_id]['callbacks']:
            try:
                cb(self._shared_data[unit_id]['facade_object'],
                   new_state)
            except Exception, ex:
                logger.error(
                    "Couldn't call callback function %s" % str(ex))

        # If we have any manager-level callbacks registered, we
        # call those as well!
        for cb in self._manager_callbacks:
            try:
                cb(self._shared_data[unit_id]['facade_object'],
                   new_state)
            except Exception, ex:
                logger.error(
                    "Couldn't call callback function %s" % str(ex))

    # ------------------------------------------------------------------------
    #
    def _set_state(self, unit_uid, state, log):

        if not isinstance(log, list):
            log = [log]

        # Acquire the shared data lock.
        self._shared_data_lock.acquire()

        old_state = self._shared_data[unit_uid]["data"]["info"]["state"]

        # Update the database.
        self._db.set_compute_unit_state(unit_uid, state, log)

        # Update shared data.
        self._shared_data[unit_uid]["data"]["info"]["state"] = state
        self._shared_data[unit_uid]["data"]["info"]["log"].extend(log)

        # Call the callbacks
        if state != old_state:
            # On a state change, we fire zee callbacks.
            logger.info(
                "ComputeUnit '%s' state changed from '%s' to '%s'." %
                (unit_uid, old_state, state)
            )

            # The state of the unit has changed, We call all
            # unit-level callbacks to propagate this.
            self.call_callbacks(unit_uid, state)

        # Release the shared data lock.
        self._shared_data_lock.release()

    # ------------------------------------------------------------------------
    #
    def run(self):
        """run() is called when the process is started via
           PilotManagerWorker.start().
        """
        logger.debug("Worker thread (ID: %s[%s]) for UnitManager %s started." %
                    (self.name, self.ident, self._um_id))

        # transfer results contains the futures to the results of the
        # asynchronous transfer operations.
        transfer_results = list()

        while not self._stop.is_set():

            # =================================================================
            #
            # Process any new transfer requests.
            try:
                request = self._transfer_requests.get_nowait()
                self._set_state(
                    request["unit_uid"],
                    TRANSFERRING_INPUT,
                    ["start transferring %s" % request]
                )

                description = request["description"]

                transfer_result = self._worker_pool.apply_async(
                    transfer_input_func, args=(
                        request["pilot_uid"],
                        request["unit_uid"],
                        request["credentials"],
                        request["unit_sandbox"],
                        description["input_data"])
                )
                transfer_results.append(transfer_result)

            except Queue.Empty:
                pass

            # =================================================================
            #
            # Check if any of the asynchronous operations has returned a result
            new_transfer_results = list()

            for transfer_result in transfer_results:
                if transfer_result.ready():
                    result = transfer_result.get()

                    self._set_state(
                        result["unit_uid"],
                        result["state"],
                        result["log"]
                    )
                    if result["state"] == PENDING_EXECUTION:
                        self._db.assign_compute_units_to_pilot(
                            unit_uids=result["unit_uid"],
                            pilot_uid=result["pilot_uid"]
                        )
                else:
                    new_transfer_results.append(transfer_result)

            transfer_results = new_transfer_results

            # =================================================================
            #
            # Check and update units. This needs to be optimized at
            # some point, i.e., state pulling should be conditional
            # or triggered by a tailable MongoDB cursor, etc.
            unit_list = self._db.get_compute_units(unit_manager_id=self._um_id)

            for unit in unit_list:
                unit_id = str(unit["_id"])

                new_state = unit["info"]["state"]
                if unit_id in self._shared_data:
                    old_state = self._shared_data[unit_id]["data"]["info"]["state"]
                else:
                    old_state = None
                    self._shared_data_lock.acquire()
                    self._shared_data[unit_id] = {
                        'data':          unit,
                        'callbacks':     [],
                        'facade_object': None
                    }
                    self._shared_data_lock.release()

                self._shared_data_lock.acquire()
                self._shared_data[unit_id]["data"] = unit
                self._shared_data_lock.release()

                if new_state != old_state:
                    # On a state change, we fire zee callbacks.
                    logger.info("ComputeUnit '%s' state changed from '%s' to '%s'." % (unit_id, old_state, new_state))

                    # The state of the unit has changed, We call all
                    # unit-level callbacks to propagate this.
                    self.call_callbacks(unit_id, new_state)

            # After the first iteration, we are officially initialized!
            if not self._initialized.is_set():
                self._initialized.set()
                logger.debug("Worker status set to 'initialized'.")

            time.sleep(1)

        # shut down the pool
        self._worker_pool.terminate()
        self._worker_pool.join()

        logger.debug("Thread main loop terminated")

    # ------------------------------------------------------------------------
    #
    def register_unit_callback(self, unit, callback_func):
        """Registers a callback function for a ComputeUnit.
        """
        unit_uid = unit.uid

        self._shared_data_lock.acquire()
        self._shared_data[unit_uid]['callbacks'].append(callback_func)
        self._shared_data_lock.release()

        # Add the facade object if missing, e.g., after a re-connect.
        if self._shared_data[unit_uid]['facade_object'] is None:
            self._shared_data_lock.acquire()
            self._shared_data[unit_uid]['facade_object'] = unit # weakref.ref(unit)
            self._shared_data_lock.release()

        # Callbacks can only be registered when the ComputeAlready has a
        # state. To partially address this shortcomming we call the callback
        # with the current ComputePilot state as soon as it is registered.
        self.call_callbacks(
            unit_uid,
            self._shared_data[unit_uid]["data"]["info"]["state"]
        )

    # ------------------------------------------------------------------------
    #
    def register_manager_callback(self, callback_func):
        """Registers a manager-level callback.
        """
        self._manager_callbacks.append(callback_func)

    # ------------------------------------------------------------------------
    #
    def get_unit_manager_data(self):
        """Returns the raw data (JSON dict) for a UnitManger.
        """
        return self._db.get_unit_manager(self._um_id)

    # ------------------------------------------------------------------------
    #
    def get_pilot_uids(self):
        """Returns the UIDs of the pilots registered with the UnitManager.
        """
        return self._db.unit_manager_list_pilots(self._um_id)

    # ------------------------------------------------------------------------
    #
    def get_compute_unit_uids(self):
        """Returns the UIDs of all ComputeUnits registered with the
        UnitManager.
        """
        return self._db.unit_manager_list_compute_units(self._um_id)

    # ------------------------------------------------------------------------
    #
    def get_compute_unit_states(self, unit_uids=None):
        """Returns the states of all ComputeUnits registered with the
        Unitmanager.
        """
        return self._db.get_compute_unit_states(
            self._um_id, unit_uids)

    # ------------------------------------------------------------------------
    #
    def get_compute_unit_stdout(self, compute_unit_uid):
        """Returns the stdout for a compute unit.
        """
        return self._db.get_compute_unit_stdout(compute_unit_uid)

    # ------------------------------------------------------------------------
    #
    def get_compute_unit_stderr(self, compute_unit_uid):
        """Returns the stderr for a compute unit.
        """
        return self._db.get_compute_unit_stderr(compute_unit_uid)

    # ------------------------------------------------------------------------
    #
    def add_pilots(self, pilots):
        """Links ComputePilots to the UnitManager.
        """
        # Extract the uids
        pids = []
        for pilot in pilots:
            pids.append(pilot.uid)

        self._db.unit_manager_add_pilots(unit_manager_id=self._um_id,
                                         pilot_ids=pids)

    # ------------------------------------------------------------------------
    #
    def remove_pilots(self, pilot_uids):
        """Unlinks one or more ComputePilots from the UnitManager.
        """
        self._db.unit_manager_remove_pilots(unit_manager_id=self._um_id,
                                            pilot_ids=pilot_uids)

    # ------------------------------------------------------------------------
    #
    def schedule_compute_units(self, pilot_uid, units, session):
        """Request the scheduling of one or more ComputeUnits on a
           ComputePilot.
        """

        # Get the credentials from the session.
        cred_dict = []
        for cred in session.credentials:
            cred_dict.append(cred.as_dict())

        unit_descriptions = list()
        wu_transfer = list()
        wu_notransfer = list()

        # Get some information about the pilot sandbox from the database.
        pilot_info = self._db.get_pilots(pilot_ids=pilot_uid)
        pilot_sandbox = pilot_info[0]['info']['sandbox']

        # Split units into two different lists: the first list contains the CUs
        # that need file transfer and the second list contains the CUs that
        # don't. The latter is added to the pilot directly, while the former
        # is added to the transfer queue.
        for unit in units:
            if unit.description.input_data is None:
                wu_notransfer.append(unit.uid)
            else:
                wu_transfer.append(unit)

        # Add all units to the database.
        results = self._db.insert_compute_units(
            pilot_uid=pilot_uid,
            pilot_sandbox=pilot_sandbox,
            unit_manager_uid=self._um_id,
            units=units,
            unit_log=[]
        )

        assert len(units) == len(results)

        # Match results with units.
        for unit in units:
            # Create a shared data store entry
            self._shared_data[unit.uid] = {
                'data':          results[unit.uid],
                'callbacks':     [],
                'facade_object': unit # weakref.ref(unit)
            }

        # Bulk-add all non-transfer units-
        self._db.assign_compute_units_to_pilot(
            unit_uids=wu_notransfer,
            pilot_uid=pilot_uid
        )

        for unit in wu_notransfer:
            log = "Scheduled for execution on ComputePilot %s." % pilot_uid
            self._set_state(unit, PENDING_EXECUTION, log)

        logger.info(
            "Scheduled ComputeUnits %s for execution on ComputePilot '%s'." %
            (wu_notransfer, pilot_uid)
        )

        # Bulk-add all units that need transfer to the transfer queue.
        # Add the startup request to the request queue.
        if len(wu_transfer) > 0:
            transfer_units = list()
            for unit in wu_transfer:
                transfer_units.append(pilot_uid)
                self._transfer_requests.put(
                    {"pilot_uid":    pilot_uid,
                     "unit_uid":     unit.uid,
                     "credentials":  cred_dict,
                     "unit_sandbox": results[unit.uid]["info"]["sandbox"],
                     "description":  unit.description}
                )
                log = "Scheduled for data tranfer to ComputePilot %s." % pilot_uid
                self._set_state(unit.uid, PENDING_INPUT_TRANSFER, log)

            logger.info(
                "Data transfer scheduled for ComputeUnits %s to ComputePilot '%s'." % 
                (transfer_units, pilot_uid)
            )
