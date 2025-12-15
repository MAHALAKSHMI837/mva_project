# shortened for space; same as previous message
# scene_detection.py
import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim
from pathlib import Path
from utils import setup_logger, ensure_dir
# Removed moviepy dependency - using OpenCV only
from tqdm import tqdm

logger = setup_logger("scene_detection")
OUT_DIR = ensure_dir("data/frames")

def extract_audio_duration(video_path):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    cap.release()
    return frame_count / fps if frame_count > 0 else 0

def frame_change_events(video_path, diff_threshold=0.35, min_interval_sec=0.5, max_frames=None):
    """
    Walk through video and detect scene changes using SSIM.
    Returns list of events: {timestamp, frame_path, change_score}
    """
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) if cap.get(cv2.CAP_PROP_FRAME_COUNT) else 0
    logger.info(f"Video FPS: {fps}, frames: {total}")
    prev_gray = None
    events = []
    last_event_time = -999
    frame_idx = 0
    pbar = tqdm(total=total if total else None, desc="Detecting scenes")
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_idx += 1
        if max_frames and frame_idx > max_frames:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if prev_gray is None:
            prev_gray = gray
            continue
        # compute structural similarity
        score, _ = ssim(prev_gray, gray, full=True)
        change_score = 1.0 - score  # larger = more different
        timestamp = frame_idx / fps
        # spike detection for clicks: high localized difference
        if change_score >= diff_threshold and (timestamp - last_event_time) >= min_interval_sec:
            frame_path = OUT_DIR / f"frame_{frame_idx:06d}.jpg"
            cv2.imwrite(str(frame_path), frame)
            events.append({"timestamp": timestamp, "frame": str(frame_path), "change_score": float(change_score), "frame_index": frame_idx})
            last_event_time = timestamp
        prev_gray = gray
        pbar.update(1)
    pbar.close()
    cap.release()
    logger.info(f"Found {len(events)} scene events")
    return events

# Optional helper: refine events by looking for micro-motions to detect clicks
def detect_click_spikes(video_path, window=3, spike_threshold=0.15):
    """
    Alternative approach: compute frame-to-frame diffs and find small transient spikes (possible clicks).
    Returns list of (timestamp, frame_path, magnitude)
    """
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    ret, prev = cap.read()
    if not ret:
        return []
    prev_gray = cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY)
    events = []
    idx = 1
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        diff = cv2.absdiff(prev_gray, gray)
        mag = np.mean(diff) / 255.0 #
        timestamp = idx / fps
        if mag > spike_threshold:
            path = OUT_DIR / f"click_{idx:06d}.jpg"
            cv2.imwrite(str(path), frame)
            events.append({"timestamp": timestamp, "frame": str(path), "magnitude": float(mag), "frame_index": idx})
        prev_gray = gray
        idx += 1
    cap.release()
    return events
