import logging

logger = logging.getLogger(__name__)

import uuid
import time


class SchedulerLock(object):
    def __init__(self, duration, lock_name="scheduler_lock"):
        self.id = self.get_instance_id()
        self.duration = duration
        self.lock_name = lock_name
        logger.debug("%s:%s initialized with %s duration.",
                     self.__class__.__name__, self.id, duration)

    def get_instance_id(self):
        """ Can be overridden, but a random UUID at launch is probably good
        enough.
        """
        return uuid.uuid4()

    def _lock_expired(self, timestamp, now):
        """ Returns the existing lock's timestamp if the lock is expired, or
        None if there is no existing lock.  If there is a lock and it is not
        expired then it returns False.
        """
        if now - timestamp > self.duration:
            return True
        return False

    def acquire_lock(self):
        """ Should be overridden and return True or False depending on whether
        it got the lock or not.
        """
        pass
