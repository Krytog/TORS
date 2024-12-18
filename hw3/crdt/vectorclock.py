from enum import Enum


class CompareStatus(Enum):
    Before = 1,
    After = 2,
    Conflict = 3,
    Same = 4


class VectorClock:
    def __init__(self):
        self.__timestamps = {}


    def compare_against(self, other_clock):
        before_count = 0
        after_count = 0
        for server, timestamp in other_clock.__timestamps:
            if server in self.__timestamps:
                local_timestamp = self.__timestamps[server]
                if local_timestamp <= timestamp:
                    before_count += 1
                elif local_timestamp >= timestamp:
                    after_count += 1
        
        other_clock_len = len(other_clock.__timestamps)
        if before_count == other_clock_len and after_count == other_clock_len:
            return CompareStatus.Same
        if before_count == other_clock_len:
            return CompareStatus.Before
        if after_count == other_clock_len:
            return CompareStatus.After
        return CompareStatus.Conflict
