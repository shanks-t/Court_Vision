import streamlit as st
import cv2
import numpy as np
import torch
from ultralytics import YOLO
import supervision as sv
import yt_dlp
import os
import logging

# configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

model_path = '/Users/treyshanks/data_science/Court_Vision/models/lebron_aug_best.pt'

# load YOLO model and set device
device = 'mps' if torch.backends.mps.is_available() else 'cpu'
# device= 'cpu'
model = YOLO(model_path)
model.model.to(device)

# Initialize tracker and annotators
tracker = sv.ByteTrack()
box_annotator = sv.BoundingBoxAnnotator()
label_annotator = sv.LabelAnnotator()

# Download YouTube video function
def download_youtube_video(url, output_path='downloaded_video.mp4'):
    ydl_opts = {
        'format': 'best',
        'outtmpl': output_path,
        'noplaylist': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    logger.info(f"Downloaded video from URL: {url}")

# Callback function for processing video frames
def callback(frame: np.ndarray, conf_threshold: float) -> np.ndarray:
    results = model(frame, device=device, conf=conf_threshold)[0]
    detections = sv.Detections.from_ultralytics(results)
    tracked_detections = tracker.update_with_detections(detections)

    # Generate tracking labels
    labels = [
        f"{model.model.names[int(class_id)]} {confidence:.2f}"
        for class_id, tracker_id, confidence in zip(tracked_detections.class_id, tracked_detections.tracker_id, tracked_detections.confidence)
    ]

    if len(labels) != len(detections):
        logger.warning(f"The number of labels provided ({len(labels)}) does not match the number of detections ({len(detections)}).")
        return frame

    # Annotate the frame with detections
    annotated_frame = box_annotator.annotate(frame.copy(), detections=tracked_detections)
    annotated_frame = label_annotator.annotate(annotated_frame, detections=tracked_detections, labels=labels)
    
    return annotated_frame

# Streamlit app
st.title("YOLOv8 YouTube Video Inference")

url = st.text_input("Enter YouTube URL:")
conf_threshold = st.slider("Confidence Threshold", 0.0, 1.0, 0.5)
# iou_threshold = st.slider("IoU Threshold", 0.0, 1.0, 0.5)

if st.button("Process Video"):
    if url:
        with st.spinner('Downloading video...'):
            try:
                download_youtube_video(url)
            except Exception as e:
                logger.error(f"Error downloading video: {e}")
                st.error(f"Error downloading video: {e}")

        cap = cv2.VideoCapture('downloaded_video.mp4')

        stframe = st.empty()
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Process frame for detections
            annotated_frame = callback(frame, conf_threshold)

            # Display frame
            stframe.image(annotated_frame, channels="BGR")

        cap.release()
        os.remove('downloaded_video.mp4')
        logger.info("Video processing completed.")
    else:
        st.write("Please enter a valid YouTube URL.")
        logger.warning("No URL entered for video processing.")