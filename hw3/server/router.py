from crdt.communication import COMMUNICATION_STATUS

from fastapi import APIRouter, status
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
