# shortened
# run.py
import argparse
from video_input import from_local, from_youtube, from_http
from scene_detection import frame_change_events
from transcribe import transcribe_with_whisper, segments_to_srt
from burn_captions import burn_srt_into_video
from report import generate_report_docx
from utils import setup_logger, ensure_dir
from pathlib import Path
import os

logger = setup_logger("run")
ensure_dir("data")
ensure_dir("data/videos")
ensure_dir("data/frames")
ensure_dir("data/transcripts")
ensure_dir("data/captioned")
ensure_dir("data/reports")

def process_video(input_source, source_type="local", whisper_model="small", diff_threshold=0.35, username=None, password=None):
    """
    Main video processing pipeline.
    
    Args:
        input_source: path or URL
        source_type: 'local' | 'youtube' | 'http' | 'private' | 'gdrive'
        whisper_model: Whisper model size
        diff_threshold: Scene change detection threshold
        username: For private platforms
        password: For private platforms
    """
    logger.info(f"Starting pipeline for {input_source} (type={source_type})")
    
    try:
        # 1. Input validation
        if not input_source or not input_source.strip():
            raise ValueError("Input source cannot be empty")
        
        # 2. Auto-detect YouTube and fetch video
        logger.info("Step 1/6: Fetching video...")
        
        # Auto-detect YouTube URLs regardless of selected type
        if "youtube.com" in input_source or "youtu.be" in input_source:
            logger.info("Auto-detected YouTube URL")
            video_path = from_youtube(input_source)
        elif source_type == "local":
            video_path = from_local(input_source)
        elif source_type == "youtube":
            video_path = from_youtube(input_source)
        elif source_type == "http":
            video_path = from_http(input_source)
        elif source_type == "private":
            from video_input import from_private
            video_path = from_private(input_source, username, password)
        elif source_type == "gdrive":
            from video_input import from_google_drive
            video_path = from_google_drive(input_source)
        else:
            raise ValueError(f"Unknown source_type: {source_type}")
        
        logger.info(f"Video acquired: {video_path}")
        
        # 3. Validate video file
        if not Path(video_path).exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        # Check file size and validity
        file_size = Path(video_path).stat().st_size
        if file_size < 1024:  # Less than 1KB
            raise ValueError(f"Video file is too small ({file_size} bytes). File may be corrupted.")
        
        # Check if video is valid
        import cv2
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            cap.release()
            raise ValueError(f"Invalid video format or corrupted file. Please use a valid MP4/MOV/AVI file.")
        
        # Check if video has frames
        frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        cap.release()
        if frame_count <= 0:
            raise ValueError(f"Video has no frames. File may be corrupted or still downloading.")
        
        # 4. Scene / event detection
        logger.info("Step 2/6: Detecting scene changes and interactions...")
        events = frame_change_events(video_path, diff_threshold=diff_threshold)
        
        if not events:
            logger.warning("No scene changes detected. Using lower threshold.")
            events = frame_change_events(video_path, diff_threshold=diff_threshold * 0.5)
        
        logger.info(f"Detected {len(events)} scene changes")
        
        # 5. Transcribe audio
        logger.info("Step 3/6: Transcribing audio...")
        segments = transcribe_with_whisper(video_path, model_name=whisper_model)
        
        if not segments:
            logger.warning("No audio segments transcribed")
            segments = []
        
        logger.info(f"Transcribed {len(segments)} audio segments")
        
        # 6. SRT generation
        logger.info("Step 4/6: Generating subtitles...")
        srt_path = Path("data/transcripts") / (Path(video_path).stem + ".srt")
        segments_to_srt(segments, srt_path)
        
        # 7. Burn captions
        logger.info("Step 5/6: Burning captions into video...")
        captioned = burn_srt_into_video(video_path, srt_path)
        
        # 8. Generate report
        logger.info("Step 6/6: Generating detailed report...")
        report = generate_report_docx(video_path, events, segments)
        
        logger.info("Pipeline completed successfully!")
        logger.info(f"Outputs:")
        logger.info(f" - Captioned video: {captioned}")
        logger.info(f" - Detailed report: {report}")
        
        return {
            "captioned": captioned, 
            "report": report,
            "events_count": len(events),
            "segments_count": len(segments),
            "original_video": video_path
        }
        
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")
        raise

def main():
    parser = argparse.ArgumentParser(description="Meeting Video Captioning & Documentation - Single Click")
    parser.add_argument("--input", "-i", help="Path or URL of video")
    parser.add_argument("--type", "-t", default="local", 
                       choices=["local", "youtube", "http", "private", "gdrive"], 
                       help="Input type")
    parser.add_argument("--whisper", default="small", 
                       choices=["tiny", "base", "small", "medium", "large"],
                       help="Whisper model size")
    parser.add_argument("--diff", type=float, default=0.35, 
                       help="Frame diff threshold (0.1-1.0)")
    parser.add_argument("--username", help="Username for private platforms")
    parser.add_argument("--password", help="Password for private platforms")
    parser.add_argument("--gui", action="store_true", help="Launch GUI interface")
    
    args = parser.parse_args()
    
    # Launch GUI if requested
    if args.gui:
        from ui.gui import main as gui_main
        gui_main()
        return
    
    # Validate arguments for CLI mode
    if not args.gui:
        if not args.input:
            logger.error("Input argument required for CLI mode")
            return
        
        if args.diff < 0.1 or args.diff > 1.0:
            logger.error("Diff threshold must be between 0.1 and 1.0")
            return
        
        if args.type == "private" and (not args.username or not args.password):
            logger.error("Username and password required for private platform access")
            return
    
    try:
        logger.info("=" * 60)
        logger.info("Meeting Video Captioning & Documentation")
        logger.info("=" * 60)
        
        res = process_video(
            args.input, 
            source_type=args.type, 
            whisper_model=args.whisper, 
            diff_threshold=args.diff,
            username=args.username,
            password=args.password
        )
        
        print("\n" + "=" * 60)
        print("PROCESSING COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print(f"📹 Captioned Video: {res['captioned']}")
        print(f"📄 Detailed Report: {res['report']}")
        print(f"🎬 Scene Changes: {res['events_count']}")
        print(f"🎤 Audio Segments: {res['segments_count']}")
        print("=" * 60)
        
    except KeyboardInterrupt:
        logger.info("Processing interrupted by user")
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        print(f"\nERROR: {e}")
        print("Check the logs for more details.")

if __name__ == "__main__":
    main()
