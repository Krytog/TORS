from crdt.vectorclock import VectorClock, CompareStatus
from logging.logger import logger


class CRDT:
    def __init__(self, my_id):
        self.id = my_id
        self.data = {}
        self.localclock = VectorClock()
        self.localclock.timestamps[self.id] = 0
        self.keysclocks = {}


    def increment_localclock(self):
        self.localclock.timestamps[self.id] += 1


    def set_key_unsafe(self, key, value, vectorclock):
        self.data[key] = value
        self.keysclocks[key] = vectorclock


    def append_key_safe(self, key, value, vectorclock, other_id):
        if key not in self.data:
            self.set_key_unsafe(self, key, value, vectorclock)
            return
        
        keyclock = self.keysclocks[key]
        compare_status = self.localclock.compare_against(keyclock)

        if compare_status == CompareStatus.After:
            logger.info(f"Tried to append key {key}, but localclock is AFTER")
            return

        if compare_status == CompareStatus.Before:
            self.set_key_unsafe(key, value, vectorclock)
            logger.info(f"Successfully set {key}={value}, localclock is BEFORE")
            return

        if compare_status == CompareStatus.Conflict:
            if self.id < other_id:
                self.set_key_unsafe(key, value, vectorclock)
                logger.info(f"Successfully set {key}={value}, localclock CONFLICTS, but our id is lesser: {self.id} < {other_id}")
            else:
                logger.info(f"Tried to append key {key}, localclock CONFLICTS, but our id is greater: {self.id} > {other_id}")
            return
        
        if compare_status == CompareStatus.Same:
            logger.error(f"Something went really wrong, localclock is SAME")
            return
        