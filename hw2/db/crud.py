from db.db import KV_STORE


def read_key(key):
    if key in KV_STORE.data:
        return KV_STORE.data[key]
    return None


def create_key(key, value):
    if key in KV_STORE.data:
        return False
    KV_STORE.data[key] = value
    return True
