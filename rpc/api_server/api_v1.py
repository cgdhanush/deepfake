import logging
import json
from copy import deepcopy
from pathlib import Path
from typing import Annotated, List
from uuid import uuid4
import shutil
from datetime import datetime
from sqlalchemy.orm import joinedload

from fastapi import APIRouter, Depends, Query, File, Form, UploadFile, HTTPException
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse

from deepfake import __version__
from deepfake.persistence import Video
from deepfake.rpc import RPC

from deepfake.rpc.api_server.api_schemas import DeepfakeResponse, Ping
from deepfake.rpc.api_server.deps import get_config, get_rpc
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


@router.get("/deepfakes", response_model=List[DeepfakeResponse], tags=["info"],)
def deepfakes(rpc: RPC = Depends(get_rpc)):
    try:
        return rpc._rpc_deepfakes()
    except RPCException:
        return []

@router.get("/deepfakes/{deepfake_id}", response_model=DeepfakeResponse, tags=["info"])
def get_deepfake_by_id(deepfake_id: int):
    video = (
        Video.session.query(Video)
        .options(joinedload(Video.result))
        .filter(Video.id == deepfake_id)
        .first()
    )

    if not video:
        raise HTTPException(status_code=404, detail="Deepfake not found")

    return video

@router.delete("/deepfakes/{deepfake_id}")
def delete_deepfake_endpoint(deepfake_id: int,  rpc: RPC = Depends(get_rpc)):
    success = rpc._rpc_delete_deepfake(deepfake_id)
    if not success:
        raise HTTPException(status_code=404, detail="Deepfake not found")
    return {"message": "Deepfake deleted successfully"}