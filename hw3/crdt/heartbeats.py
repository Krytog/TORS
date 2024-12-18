from crdt.config import CONFIG
from common.logger import logger

import concurrent
import time


BETWEEN_HEARTBEATS = 1.0
HEARTBEAT_CYCLE_TIMEOUT = 0.5


def heartbeat_task(server, log):
    pass


def send_heartbeats(crdt):
    log = None
    with crdt.mutex:
        log = crdt.log.copy()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = set()
        for _, server in CONFIG.items():
            futures.add(executor.submit(heartbeat_task, server, log))
        try:
            for _ in concurrent.futures.as_completed(futures, timeout=HEARTBEAT_CYCLE_TIMEOUT):
                pass
        except Exception as err:
            logger.error(f"Something went wrong during the heartbeat cycle. What: {str(err)}")


def sleep_until(timepoint):
    now = time.time()
    if now >= timepoint:
        return
    time.sleep(timepoint - now)


def heartbeats_routine(crdt):
    while True:
        timepoint = time.time()
        send_heartbeats(crdt)
        sleep_until(timepoint + BETWEEN_HEARTBEATS)
