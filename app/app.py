import streamlit as st
import cv2
import numpy as np
import torch
from ultralytics import YOLO
import yt_dlp
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Paths
model_aug_path = '/Users/treyshanks/data_science/Court_Vision/notebooks/lebron_aug_best.pt'

# Load YOLO model and set device
device = 'mps' if torch.backends.mps.is_available() else 'cpu'
model = YOLO(model_aug_path)
model.model.to(device)

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

# Function to run inference on a video frame by frame
def run_inference_on_video(video_path, conf_threshold, iou_threshold):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        logger.error("Error: Could not open video.")
        return

    stframe = st.empty()

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Run inference on the frame
        results = model.predict(
            source=frame,
            device=device,
            conf=conf_threshold,
            iou=iou_threshold,
            imgsz=640
        )

        for result in results:
            boxes = result.boxes.xyxy.cpu().numpy()
            confidences = result.boxes.conf.cpu().numpy()
            class_ids = result.boxes.cls.cpu().numpy().astype(int)

            for box, conf, class_id in zip(boxes, confidences, class_ids):
                x1, y1, x2, y2 = map(int, box)
                label = model.model.names[class_id]
                text = f'{label} {conf:.2f}'
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Display the frame
        stframe.image(frame, channels="BGR")

    cap.release()
    cv2.destroyAllWindows()

# Streamlit app
st.title("YOLOv8 YouTube Video Inference")

url = st.text_input("Enter YouTube URL:")
conf_threshold = st.slider("Confidence Threshold", 0.0, 1.0, 0.5)
iou_threshold = st.slider("IoU Threshold", 0.0, 1.0, 0.5)

if st.button("Process Video"):
    if url:
        with st.spinner('Downloading video...'):
            try:
                download_youtube_video(url)
            except Exception as e:
                logger.error(f"Error downloading video: {e}")
                st.error(f"Error downloading video: {e}")

        if os.path.exists('downloaded_video.mp4'):
            run_inference_on_video('downloaded_video.mp4', conf_threshold, iou_threshold)
            os.remove('downloaded_video.mp4')
            logger.info("Video processing completed.")
    else:
        st.write("Please enter a valid YouTube URL.")
        logger.warning("No URL entered for video processing.")
