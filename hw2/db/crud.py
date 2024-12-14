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


def delete_key(key):
    if key in KV_STORE.data:
        KV_STORE.remove(key)
        return True
    return False


def update_key(key, value):
    if key not in KV_STORE.data:
        return False
    KV_STORE.data[key] = value
    return True
 

def cas_key(key, value, old_value):
    if key not in KV_STORE.data:
        return None
    if KV_STORE.data[key] != old_value:
        return False
    KV_STORE.data[key] = value
    return True
