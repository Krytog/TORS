from crdt.config import CONFIG
from crdt.communication import COMMUNICATION_STATUS
from common.logger import logger

import requests
import concurrent
import time


BETWEEN_HEARTBEATS = 5.0
HEARTBEAT_MESSAGE_TIMEOUT = 0.3
HEARTBEAT_CYCLE_TIMEOUT = 0.5


def heartbeat_task(server, log):
    try:
        requests.put(f"http://{server}/sync", json={"log": tuple(log)}, timeout=HEARTBEAT_MESSAGE_TIMEOUT)
    except Exception as err:
        logger.error(f"Something went wrong during the heartbeat task. What: {str(err)}")


def send_heartbeats(crdt):
    log = []
    with crdt.mutex:
        for entry in crdt.log:
            log.append(entry.get_serialized())

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = set()
        for server_id, server_addr in CONFIG.items():
            if server_id != crdt.id:
                futures.add(executor.submit(heartbeat_task, server_addr, log))
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

        if COMMUNICATION_STATUS.should_communicate:
            send_heartbeats(crdt)

        sleep_until(timepoint + BETWEEN_HEARTBEATS)
