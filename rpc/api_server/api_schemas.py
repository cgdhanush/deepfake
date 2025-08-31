from datetime import date, datetime
from typing import Any, Optional

from pydantic import AwareDatetime, BaseModel, RootModel, SerializeAsAny, model_validator
from deepfake.rpc.api_server.webserver_bgwork import ProgressTask


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


class ResultSchema(BaseModel):
    analysis_model: str
    detection_score: float
    deepfake_detected: bool
    confidence: str

    model_config = {
        "from_attributes": True
    }
    
class DeepfakeResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    duration: Optional[float]
    file_path: Optional[str]
    uploadedDate: Optional[datetime]
    video_filename: Optional[str]
    result: Optional[ResultSchema]

    model_config = {
        "from_attributes": True
    }