import logging
from copy import deepcopy
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.exceptions import HTTPException

from deepfake import __version__
from deepfake.exceptions import OperationalException
from deepfake.rpc import RPC
from deepfake.rpc.api_server.api_schemas import (
    Ping,
    ResultMsg,
    StatusMsg,
    Version,

)
from deepfake.rpc.api_server.deps import get_config, get_rpc, get_rpc_optional
from deepfake.rpc.rpc import RPCException


logger = logging.getLogger(__name__)

API_VERSION = 2.43

# Public API, requires no auth.
router_public = APIRouter()
# Private API, protected by authentication
router = APIRouter()


@router_public.get("/ping", response_model=Ping)
def ping():
    """simple ping"""
    return {"status": "pong"}


@router.get("/version", response_model=Version, tags=["info"])
def version():
    """Bot Version info"""
    return {"version": __version__}
