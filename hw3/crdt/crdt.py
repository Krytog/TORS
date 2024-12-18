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

    def get_serialized(self):
        return {
            "source": self.source,
            "key": self.key,
            "value": self.value,
            "vectorclock": self.vectorclock.timestamps,
        }
    
    def from_serialized(data):
        normal_map = {}
        for key, value in data["vectorclock"].items():
            normal_map[int(key)] = value
        return LogEntry(data["source"], data["key"], data["value"], VectorClock(normal_map))


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
            self.set_key_unsafe(key, value, vectorclock, source)
            return

        keyclock = self.keysclocks[key]
        compare_status = keyclock.compare_against(vectorclock)

        logger.debug(f"Working with {key}={value}, its keyclock: {keyclock.timestamps}, given vectorclock: {vectorclock.timestamps}, status: {compare_status}")

        if compare_status == CompareStatus.After:
            logger.debug(f"Tried to append key {key}, but localclock is AFTER")
            return

        if compare_status == CompareStatus.Before:
            self.set_key_unsafe(key, value, vectorclock, source)
            logger.debug(f"Successfully set {key}={value}, localclock is BEFORE")
            return

        if compare_status == CompareStatus.Conflict:
            if self.id < source:
                self.set_key_unsafe(key, value, vectorclock, source)
                logger.debug(f"Successfully set {key}={value}, localclock CONFLICTS, but our id is lesser: {self.id} < {source}")
            else:
                logger.debug(f"Tried to append key {key}, localclock CONFLICTS, but our id is greater: {self.id} > {source}")
            return
        
        if compare_status == CompareStatus.Same:
            logger.debug(f"Do not do anything, localclock is SAME")
            return

CRDT_INSTANCE = CRDT(MY_ID)
