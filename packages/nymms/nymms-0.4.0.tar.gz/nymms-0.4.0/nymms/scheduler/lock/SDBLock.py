import logging

logger = logging.getLogger(__name__)

import time

from boto.exception import SDBResponseError

from nymms.scheduler.lock.SchedulerLock import SchedulerLock


class SDBLock(SchedulerLock):
    def __init__(self, duration, conn, domain_name,
                 lock_name="scheduler_lock"):
        super(SDBLock, self).__init__(duration, lock_name)
        self._conn = conn
        self._domain_name = domain_name
        self._domain = None

    def _setup_domain(self):
        if self._domain:
            return
        logger.debug("setting up state domain %s", self._domain_name)
        self._domain = self._conn.create_domain(self._domain_name)

    def acquire_lock(self):
        self._setup_domain()
        now = int(time.time())
        existing_lock = self._domain.get_item(self.lock_name,
                                              consistent_read=True)
        lock_body = {'timestamp': now, 'id': self.id}
        expected_value = ['timestamp', False]
        if existing_lock:
            current_timestamp = existing_lock['timestamp']
            if self._lock_expired(float(current_timestamp), now):
                expected_value = ['timestamp', current_timestamp]

        try:
            self._domain.put_attributes(self.lock_name, lock_body,
                                        replace=bool(existing_lock),
                                        expected_value=expected_value)
            return True
        except SDBResponseError as e:
            if e.status == 409:
                return False
            raise
        return False
