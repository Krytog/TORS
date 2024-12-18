from crdt.communication import COMMUNICATION_STATUS
from crdt.crdt import CRDT_INSTANCE, LogEntry
from crdt.vectorclock import VectorClock

from fastapi import APIRouter, status, Request
from fastapi.responses import JSONResponse

from functools import wraps


router = APIRouter()


def switching(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        if not COMMUNICATION_STATUS.should_communicate:
            return JSONResponse(status_code=status.HTTP_418_IM_A_TEAPOT, content={"message": "Communication is disabled"})
        return await func(*args, **kwargs)
    return wrapper


@router.put("/switch/{flag}")
async def switch(flag):
    if flag == "0":
        COMMUNICATION_STATUS.should_communicate = False
        return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Requests from other servers will be ignored"})
    COMMUNICATION_STATUS.should_communicate = True
    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Requests from other servers will be handled"})


@router.get("/helloworld")
@switching
async def helloworld():
    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Hello world!"})


@router.put("/sync")
@switching
async def sync(request: Request):
    data = await request.json()
    log = data["log"]
    with CRDT_INSTANCE.mutex:
        for serialized_entry in log:
            entry = LogEntry.from_serialized(serialized_entry)
            CRDT_INSTANCE.set_key_safe(entry.key, entry.value, entry.vectorclock, entry.source)
            CRDT_INSTANCE.localclock.sync_with(entry.vectorclock)
        return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Sync is successful"})


@router.get("/data")
async def get_all_data():
    output = {}
    with CRDT_INSTANCE.mutex:
        output = CRDT_INSTANCE.data.copy()
    return JSONResponse(status_code=status.HTTP_200_OK, content=output)


@router.patch("/set")
async def set_keys(request: Request):
    data = await request.json()
    with CRDT_INSTANCE.mutex:
        for key, value in data.items():
            CRDT_INSTANCE.increment_localclock()
            CRDT_INSTANCE.set_key_safe(
                key, 
                value, 
                VectorClock(CRDT_INSTANCE.localclock.timestamps.copy()), 
                CRDT_INSTANCE.id
            )
    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Operations are added to be processed"})
