#!/usr/bin/env python3
import os
import random
import cv2
import json
import dlib
import logging
import numpy as np
from glob import glob
from tqdm import tqdm
import multiprocessing
# from imutils import face_utils
from functools import partial

from deepfake.constants import FACE_PREDICTOR_NAME

logger = logging.getLogger(__name__)

# ====== Configuration ======
NUM_FRAMES = 1
IMG_META_DICT = dict()
TEST_LIMIT = 200

# ====== Helper Functions ======
def parse_video_path(videos_path: str, dataset: str):
    if dataset in ["Actors", "Youtube"]:
        dataset_path = f'{videos_path}/original/{dataset}/'
    else:
        dataset_path = f'{videos_path}/manipulated/{dataset}/'

    movies_path_list = sorted(glob(dataset_path + '*.mp4'))
    
    if len(movies_path_list) > 0:
        logger.info(f"{len(movies_path_list)} videos found in {dataset}")
        
    return movies_path_list

def parse_labels(video_path):
    return 0 if "original" in video_path.lower() else 1

def get_output_dir(label, save_images_path):
    return os.path.join(save_images_path, 'real' if label == 0 else 'fake')

def preprocess_video(video_path, save_images_path, face_detector, face_predictor):
    label = parse_labels(video_path)
    save_dir = get_output_dir(label, save_images_path)
    os.makedirs(save_dir, exist_ok=True)

    video_name = os.path.splitext(os.path.basename(video_path))[0]

    cap = cv2.VideoCapture(video_path)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_idxs = np.linspace(0, frame_count - 1, NUM_FRAMES, endpoint=True, dtype=int)

    for cnt_frame in range(frame_count):
        ret, frame = cap.read()
        if not ret:
            logger.error(f"Frame read error at frame {cnt_frame}: {video_path}")
            continue
        if cnt_frame not in frame_idxs:
            continue

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        faces = face_detector(rgb_frame, 1)

        if len(faces) == 0:
            logger.warning(f"No faces in frame {cnt_frame} of {video_name}")
            continue

        landmarks = []
        face_sizes = []

        for face in faces:
            shape = face_predictor(rgb_frame, face)
            shape_np = face_utils.shape_to_np(shape)
            x0, y0 = shape_np[:, 0].min(), shape_np[:, 1].min()
            x1, y1 = shape_np[:, 0].max(), shape_np[:, 1].max()
            face_area = (x1 - x0) * (y1 - y0)
            face_sizes.append(face_area)
            landmarks.append(shape_np)

        landmarks = np.array(landmarks)
        largest_face_idx = np.argmax(face_sizes)
        chosen_landmark = landmarks[largest_face_idx]

        # Save image as: videoName_frameNumber.png
        img_filename = f"{video_name}_frame_{cnt_frame}.png"
        img_path = os.path.join(save_dir, img_filename)
        meta_key = os.path.join(os.path.basename(save_dir), img_filename)

        # Save frame
        cv2.imwrite(img_path, frame)

        # Save metadata
        IMG_META_DICT[meta_key] = {
            "landmark": chosen_landmark.tolist(),
            "label": label
        }

    cap.release()

# ====== Extract Frames ======

def process_video(video_path, save_images_path, face_detector, face_predictor):
    preprocess_video(str(video_path), str(save_images_path), face_detector, face_predictor)
    
def extract_frames(config: dict):
    predictor_path = config["modelsdir"] / FACE_PREDICTOR_NAME
    face_detector = dlib.get_frontal_face_detector()
    face_predictor = dlib.shape_predictor(str(predictor_path))

    datasets = config["datasets"]
    videos_path = config["datadir"]
    save_images_path = config["imgdir"]

    train_size_pcr = config.get("train_size_pcr", 0.8)

    video_paths_to_process = []

    for dataset in datasets:
       
        video_list = parse_video_path(str(videos_path), dataset)

        # Split dataset into 80% train and 20% test
        train_size = int(train_size_pcr * len(video_list))
        test_size = len(video_list) - train_size

        train_videos = random.sample(video_list, train_size)
        test_videos = [v for v in video_list if v not in train_videos]

        # Process train videos
        train_path = save_images_path / "train"
        os.makedirs(train_path, exist_ok=True)
        for video_path in train_videos:
            video_paths_to_process.append((video_path, train_path))

        # Process test videos
        test_path = save_images_path / "test"
        os.makedirs(test_path, exist_ok=True)
        for video_path in test_videos:
            video_paths_to_process.append((video_path, test_path))

    pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
    process_fn = partial(process_video, face_detector=face_detector, face_predictor=face_predictor)

    with tqdm(total=len(video_paths_to_process), desc="Processing videos") as pbar:
        for video_path, save_path in pool.imap_unordered(process_fn, video_paths_to_process):
            process_video(video_path, save_path, face_detector, face_predictor)
            pbar.update(1)

    with open(os.path.join(save_images_path, "ldm.json"), 'w') as f:
        json.dump(IMG_META_DICT, f, indent=4)

    pool.close()
    pool.join()