from raft.config import CONFIG, MY_ID

import pickle
from common.logging import logger


STATE_FILENAME = "state.pickle"


class LogEntry:
    def __init__(self, term, key, value):
        self.term = term
        self.key = key
        self.value = value


class State:
    def __init__(self, my_id):
        self.my_id = my_id

        self.term = 0
        self.voted_for = 0
        self.log = []
        self.log.append(LogEntry(0, None, None))  # a dummy value so the log is never empty

        self.log_commited_index = 0
        self.log_last_applied = 0

    
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


class LeaderState:
    def __init__(self, leader_log_last_index):
        self.log_next_indices = {}
        self.log_match_index = {}
        for server_id, _ in CONFIG.items():
            self.log_next_indices[server_id] = leader_log_last_index + 1
            self.log_match_index[server_id] = 0


STATE = State(MY_ID)
STATE.load_state_from_storage()
LEADER_STATE = None
