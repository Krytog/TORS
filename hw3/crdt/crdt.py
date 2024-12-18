from crdt.vectorclock import VectorClock, CompareStatus
from crdt.config import MY_ID
from common.logger import logger

from threading import Lock


class LogEntry:
    def __init__(self, source, key, value, vectorclock):
        self.source = source
        self.key = key
        self.value = value
        self.vectorclock = vectorclock


class CRDT:
    def __init__(self, my_id):
        self.id = my_id
        self.data = {}
        self.localclock = VectorClock({})
        self.localclock.timestamps[self.id] = 0
        self.keysclocks = {}
        self.log = []
        self.mutex = Lock()


    def increment_localclock(self):
        self.localclock.timestamps[self.id] += 1


    def set_key_unsafe(self, key, value, vectorclock, source):
        self.data[key] = value
        self.keysclocks[key] = vectorclock
        self.log.append(
            LogEntry(
                source,
                key,
                value,
                vectorclock,
            )
        )


    def set_key_safe(self, key, value, vectorclock, source):
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
            if self.id < source:
                self.set_key_unsafe(key, value, vectorclock)
                logger.info(f"Successfully set {key}={value}, localclock CONFLICTS, but our id is lesser: {self.id} < {source}")
            else:
                logger.info(f"Tried to append key {key}, localclock CONFLICTS, but our id is greater: {self.id} > {source}")
            return
        
        if compare_status == CompareStatus.Same:
            logger.error(f"Something went really wrong, localclock is SAME")
            return

CRDT_INSTANCE = CRDT(MY_ID)
