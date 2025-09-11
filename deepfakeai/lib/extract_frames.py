import os
import cv2
import dlib
import json
import logging
import os
from tqdm import tqdm
from pathlib import Path
import numpy as np
from glob import glob
from imutils import face_utils

logger = logging.getLogger(__name__)


PREDICTOR_PATH = "shape_predictor_81_face_landmarks.dat"
NUM_FRAMES = 1
IMG_META_DICT = dict()


def parse_labels(video_path: str):
    label = None
    if "original" in video_path:
        label = 0
    else:
        label = 1
    return label

def parse_source_save_path(save_path: str):
    source_save_path = None
    if "original" in save_path:
        source_save_path = save_path
    else:
        img_meta = save_path.split('/')
        source_target_index = img_meta[-1]
        source_index = source_target_index.split('_')[0]
        manipulation_name = img_meta[-4]
        original_name = "youtube"
        source_save_path = save_path.replace(
            "manipulated_sequences", "original_sequences"
        ).replace(
            manipulation_name, original_name
        ).replace(
            source_target_index, source_index
        )
    return source_save_path


def preprocess_video(video_path: str, save_path: str, face_detector, face_predictor):
    # save the video meta info here
    video_dict = dict()
    
    # get the labels
    label = parse_labels(video_path)
    
    # get the path of corresponding source imgs
    source_save_path = parse_source_save_path(save_path)
    
    # prepare the save path
    os.makedirs(save_path, exist_ok=True)
    
    # read the video and prepare the sampled index
    cap_video = cv2.VideoCapture(video_path)
    frame_count_video = int(cap_video.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_idxs = np.linspace(0, frame_count_video - 1, NUM_FRAMES, endpoint=True, dtype=int)
    
    # process each frame
    for cnt_frame in range(frame_count_video):
        ret, frame = cap_video.read()
        height, width = frame.shape[:-1]
        if not ret:
            tqdm.write('Frame read {} Error! : {}'.format(cnt_frame, os.path.basename(video_path)))
            continue
        if cnt_frame not in frame_idxs:
            continue
        if frame is None:
            logger.warning(f"Warning: Failed to read frame from {video_path}")
            continue
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        faces = face_detector(frame_rgb, 1)
    
        if len(faces) == 0:
            tqdm.write('No faces in {}:{}'.format(cnt_frame, os.path.basename(video_path)))
            continue
        landmarks = list()  # save the landmark
        size_list = list()  # save the size of the detected face
        for face_idx in range(len(faces)):
            landmark = face_predictor(frame, faces[face_idx])
            landmark = face_utils.shape_to_np(landmark)
            x0, y0 = landmark[:, 0].min(), landmark[:, 1].min()
            x1, y1 = landmark[:, 0].max(), landmark[:, 1].max()
            face_s = (x1 - x0) * (y1 - y0)
            size_list.append(face_s)
            landmarks.append(landmark)
            
        # save the landmark with the biggest face
        landmarks = np.concatenate(landmarks).reshape((len(size_list),)+landmark.shape)
        landmarks = landmarks[np.argsort(np.array(size_list))[::-1]][0]
        
        # save the meta info of the video
        video_dict['landmark'] = landmarks.tolist()
        video_dict['source_path'] = f"{source_save_path}/frame_{cnt_frame}"
        video_dict['label'] = label
        IMG_META_DICT[f"{save_path}/frame_{cnt_frame}"] = video_dict
        
        # save one frame
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        image_path = f"{save_path}/frame_{cnt_frame}.png"
        cv2.imwrite(image_path, frame)
        
    cap_video.release()
    return


def extract_frames(config: dict):
    predictor_path = config["modelsdir"] / PREDICTOR_PATH
    face_detector = dlib.get_frontal_face_detector()
    face_predictor = dlib.shape_predictor(str(predictor_path))

    original_videos_path = config["datadir"] / "original"
    deepfake_videos_path = config["datadir"] / "deepfake"
    mode: str = config["mode"]  # "train" or "test"

    # Process both original and deepfake directories
    for class_path in [original_videos_path, deepfake_videos_path]:
        class_name = class_path.name  # Will be 'original' or 'deepfake'
        
        for root, _, files in os.walk(class_path):
            for file in files:
                if file.endswith(".mp4"):
                    video_path = Path(root) / file

                    # Save path includes mode (train/test) and class name
                    save_path_per_video = (
                        config["imgdir"] / mode / class_name
                    ).with_suffix('').as_posix().replace("/videos", "/frames")
                    
                    preprocess_video(
                        str(video_path),
                        str(save_path_per_video),
                        face_detector,
                        face_predictor
                    )
    # Save image metadata
    with open(f"{config['imgdir']}/ldm.json", 'w') as f:
        json.dump(IMG_META_DICT, f)

