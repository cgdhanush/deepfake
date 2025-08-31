import logging
import os
from pathlib import Path

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from fastapi.responses import FileResponse

from deepfake.api_server.api_schemas import BackgroundTaskStatus
from deepfake.api_server.deps import get_config
from deepfake.api_server.webserver_bgwork import ApiBG


logger = logging.getLogger(__name__)

# Private API, protected by authentication and webserver_mode dependency
router = APIRouter()

@router.get("/uploads/{filename}", tags=["webserver"])
def get_video(filename: str,  config: dict = Depends(get_config),):
    
    UPLOAD_DIR = config["upload_dir"]
    file_path: Path = UPLOAD_DIR / filename
   
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Video not found")
    return FileResponse(path=file_path, media_type='video/mp4', filename=filename)


@router.get("/background", response_model=list[BackgroundTaskStatus], tags=["webserver"])
def background_job_list():
    return [
        {
            "job_id": jobid,
            "job_category": job["category"],
            "status": job["status"],
            "running": job["is_running"],
            "progress": job.get("progress"),
            "progress_tasks": job.get("progress_tasks"),
            "error": job.get("error", None),
        }
        for jobid, job in ApiBG.jobs.items()
    ]


@router.get("/background/{jobid}", response_model=BackgroundTaskStatus, tags=["webserver"])
def background_job(jobid: str):
    if not (job := ApiBG.jobs.get(jobid)):
        raise HTTPException(status_code=404, detail="Job not found.")

    return {
        "job_id": jobid,
        "job_category": job["category"],
        "status": job["status"],
        "running": job["is_running"],
        "progress": job.get("progress"),
        "progress_tasks": job.get("progress_tasks"),
        "error": job.get("error", None),
    }
