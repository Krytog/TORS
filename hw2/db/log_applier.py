from raft.state import STATE
from db import crud

import asyncio


def apply_log_entry(log_entry):
    if log_entry.command == "create":
        return crud.create_key(log_entry.key, log_entry.value)
    elif log_entry.command == "delete":
        return crud.delete_key(log_entry.key)
    elif log_entry.command == "update":
        return crud.update_key(log_entry.key, log_entry.value)


async def wait_for_apply(index):
    last_result = None
    while index < STATE.log_last_applied:
        while STATE.log_commited_index > STATE.log_last_applied:
            last_result = apply_log_entry(STATE.get_log_entry_safe(STATE.log_last_applied))
            STATE.log_last_applied += 1
        if index < STATE.log_last_applied:
            await asyncio.sleep(0)
    return last_result
