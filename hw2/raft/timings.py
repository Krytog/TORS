from random import randint
from time import time
from threading import Lock


ELECTIONS_TIMEOUT_FROM = 200
ELECTIONS_TIMEOUT_TO = 500


class Timing:
    def __init__(self):
        self.elections_timeout = randint(ELECTIONS_TIMEOUT_FROM, ELECTIONS_TIMEOUT_TO) / 1000
        self.last_action_timestamp = time()
        self.mutex = Lock()

    def should_start_elections(self):
        with self.mutex:
            timestamp = self.elections_timeout + self.last_action_timestamp
            return time() > timestamp
    
    def set_new_random_timeout(self):
        self.elections_timeout = randint(ELECTIONS_TIMEOUT_FROM, ELECTIONS_TIMEOUT_TO) / 1000

    def set_new_last_action_timestamp_safe(self, value):
        with self.mutex:
            self.last_action_timestamp = value


TIMING = Timing()
