import unittest

from nymms.scheduler.lock.SchedulerLock import SchedulerLock

NOW = 1391115581.238759
DURATION = 30

class TestSchedulerLock(unittest.TestCase):
    def setUp(self):
        self.lock = SchedulerLock(DURATION)

    def test_lock_expired(self):
        no_lock = None
        self.assertIs(self.lock._lock_expired(no_lock, NOW), None)
        expired_lock = {'timestamp': NOW - (DURATION + 5), 'id': self.lock.id}
        self.assertEquals(self.lock._lock_expired(expired_lock, NOW),
                          expired_lock['timestamp'])
        valid_lock = {'timestamp': NOW - 1, 'id': self.lock.id}
        self.assertIs(self.lock._lock_expired(valid_lock, NOW), False)
