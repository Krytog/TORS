import pytest
import common

import time


def test_leader_selected():
    leader1 = common.get_leader(1)
    leader2 = common.get_leader(2)
    leader3 = common.get_leader(3)
    assert leader1 == leader2
    assert leader2 == leader3


def test_leader_reselected():
    old_leader = common.get_leader(1)
    common.kill_server(old_leader)
    time.sleep(10)
    leaders = []
    for i in range(1, 4):
        if i != old_leader:
            leaders.append(common.get_leader(i))
    assert leaders[0] == leaders[1]

    common.restart_server(old_leader)


def test_stale_leader():
    time.sleep(5)
    leaders = []
    for i in range(1, 4):
        leaders.append(common.get_leader(i))
    assert leaders[0] == leaders[1]
    assert leaders[0] == leaders[2]


def test_eventual_recover():
    leader_id = common.get_leader(1)
    kill_ids = []
    kill_ids.append(leader_id)
    kill_ids.append(1 + leader_id % 3)
    for i in kill_ids:
        common.kill_server(i)
    time.sleep(5)
    for i in kill_ids:
        common.restart_server(i)
    time.sleep(10)
    leaders = []
    for i in range(1, 4):
        leaders.append(common.get_leader(i))
    assert leaders[0] == leaders[1]
    assert leaders[0] == leaders[2]
