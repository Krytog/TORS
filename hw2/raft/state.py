from raft.config import CONFIG, MY_ID

import pickle
from common.logging import logger

from threading import Lock


STATE_FILENAME = "state.pickle"


class LogEntry:
    def __init__(self, term, command, key, value):
        self.term = term
        self.command = command
        self.key = key
        self.value = value


class State:
    def __init__(self, my_id):
        self.my_id = my_id
        self.leader_id = 0

        self.term = 0
        self.voted_for = 0
        self.log = []
        self.log.append(LogEntry(0, None, None, None))  # a dummy value so the log is never empty

        self.log_commited_index = 0
        self.log_last_applied = 0
        
        self.__mutex = Lock()

    
    def update_if_stale(self, new_term):
        self.term = new_term
        self.voted_for = 0


    def dump_state_to_storage(self):
        data = {}
        data["id"] = self.my_id
        data["term"] = self.term
        data["voted_for"] = self.voted_for
        data["log"] = self.log

        with open(STATE_FILENAME, "wb") as file:
            pickle.dump(data, file)


    def load_state_from_storage(self):
        data = None
        try:
            with open(STATE_FILENAME, "rb") as file:
                data = pickle.load(file)
            logger.info(f"State for server {self.my_id} is successfully loaded from stable storage")
        except Exception:
            logger.info(f"No saved state is found for server {self.my_id}. It seems it's the very first start")
            return
        
        if data.get("id") != self.my_id:
            raise RuntimeError("Loaded state for incorrect id!")

        self.term = data.get("term")
        self.voted_for = data.get("voted_for")
        self.log = data.get("log")


    def append_to_log_safe(self, entry):
        output = None
        with self.__mutex:
            self.log.append(entry)
            output = len(self.log)
        return output
        

    def get_log_tail_safe(self, index_from):
        output = []
        with self.__mutex:
            for i in range(index_from, len(self.log)):
                output.append(self.log[i])
        return output
    
    def get_log_entry_safe(self, index):
        output = None
        with self.__mutex:
            output = self.log[index]
        return output
    
    def remove_log_tail_safe(self, last_index):
        with self.__mutex:
            self.log = self.log[:last_index + 1]


class LeaderState:
    def __init__(self, leader_log_last_index):
        self.log_next_index = {}
        self.log_match_index = {}
        self.mutex = Lock()
        self.reinit(leader_log_last_index)

    def reinit(self, leader_log_last_index):
        for server, _ in CONFIG.items():
            server_id = int(server)
            self.log_next_index[server_id] = leader_log_last_index + 1
            self.log_match_index[server_id] = 1

    def get_indices_safe(self, server):
        with self.mutex:
            return self.log_next_index[server], self.log_match_index[server]
            

STATE = State(MY_ID)
STATE.load_state_from_storage()
LEADER_STATE = LeaderState(0)
