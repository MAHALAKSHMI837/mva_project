import cv2
import numpy as np
from utils import setup_logger

logger = setup_logger("click_detector")

def detect_clicks(video_path, threshold=0.8):
    """Advanced click detection using motion analysis"""
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    clicks = []
    prev_frame = None
    frame_idx = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        if prev_frame is not None:
            # Detect sudden motion spikes (potential clicks)
            diff = cv2.absdiff(prev_frame, gray)
            motion = np.sum(diff) / (diff.shape[0] * diff.shape[1])
            
            if motion > threshold:
                timestamp = frame_idx / fps
                clicks.append({"timestamp": timestamp, "intensity": motion})
        
        prev_frame = gray
        frame_idx += 1
    
    cap.release()
    return clicks