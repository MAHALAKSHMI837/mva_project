import cv2
import numpy as np
from pathlib import Path

# Create a simple test video
def create_test_video():
    output_path = Path("test_video.mp4")
    
    # Video properties
    width, height = 640, 480
    fps = 30
    duration = 10  # seconds
    
    # Create video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
    
    for frame_num in range(fps * duration):
        # Create a frame with changing colors
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Add some visual changes every 2 seconds
        if frame_num // (fps * 2) % 2 == 0:
            frame[:, :] = [100, 150, 200]  # Light blue
        else:
            frame[:, :] = [200, 100, 150]  # Light pink
        
        # Add frame number text
        cv2.putText(frame, f"Frame {frame_num}", (50, 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        out.write(frame)
    
    out.release()
    print(f"Test video created: {output_path.absolute()}")
    return str(output_path.absolute())

if __name__ == "__main__":
    create_test_video()