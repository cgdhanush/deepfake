import logging
import os
from pathlib import Path
import shutil

from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.exceptions import HTTPException
from fastapi.responses import FileResponse, JSONResponse

from deepfake.rpc.api_server.deps import get_config, get_rpc
from deepfake.rpc.rpc import RPC

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


@router.post("/upload-video")
async def upload_video(
    user_id: int = Form(...),
    video: UploadFile = File(...),
    title: str = Form(...),
    description: str = Form(""),
    duration: str = Form(...),
    uploadedDate: str = Form(...),

    rpc: RPC = Depends(get_rpc),
    config: dict = Depends(get_config),
):
    try:
        UPLOAD_DIR = config["upload_dir"]
        file_path: Path = UPLOAD_DIR / video.filename

        with file_path.open("wb") as buffer:
            shutil.copyfileobj(video.file, buffer)

        new_entry = rpc._rpc_add_deepfake(
            title=title,
            user_id=user_id,
            description=description,
            duration=duration,
            file_path=str(file_path.resolve()),
            uploadedDate=uploadedDate,
            video_filename=video.filename
        )

        return JSONResponse(content={
            "id": new_entry["id"],
            "message": "Video uploaded successfully",
            "video_filename": new_entry["video_filename"],
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")