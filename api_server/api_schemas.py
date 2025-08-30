from datetime import date, datetime
from typing import Any

from pydantic import AwareDatetime, BaseModel, RootModel, SerializeAsAny, model_validator
from deepfake.rpc.api_server.webserver_bgwork import ProgressTask


class Ping(BaseModel):
    status: str


class AccessToken(BaseModel):
    access_token: str


class AccessAndRefreshToken(AccessToken):
    refresh_token: str


class Version(BaseModel):
    version: str


class StatusMsg(BaseModel):
    status: str


class BgJobStarted(StatusMsg):
    job_id: str


class BackgroundTaskStatus(BaseModel):
    job_id: str
    job_category: str
    status: str
    running: bool
    progress: float | None = None
    progress_tasks: dict[str, ProgressTask] | None = None
    error: str | None = None


class BackgroundTaskResult(BaseModel):
    error: str | None = None
    status: str


class ResultMsg(BaseModel):
    result: str
