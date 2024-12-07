from raft.config import CONFIG, MY_ID
from raft.state import STATE, State
from raft.role_transitions import transit_to_follower
from raft.elections import elections_routine

import threading


if __name__ == '__main__':
    print("Server comes online...")
    transit_to_follower()

    my_id = str(MY_ID)
    print(f"My id is {my_id}, I run at {CONFIG[my_id][0]}:{CONFIG[my_id][1]}")

    thread = threading.Thread(elections_routine())
