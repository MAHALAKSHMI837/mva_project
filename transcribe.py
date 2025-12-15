# shortened
# transcribe.py
import whisper
import json
from pathlib import Path
from utils import setup_logger, ensure_dir
import subprocess

logger = setup_logger("transcribe")
OUT_DIR = ensure_dir("data/transcripts")

def transcribe_with_whisper(video_path, model_name="small"):
    """
    Transcribe audio using Whisper (openai/whisper pip package).
    Returns segments list: [{start, end, text}, ...]
    """
    try:
        logger.info(f"Loading Whisper model: {model_name}")
        
        # Validate model name
        valid_models = ["tiny", "base", "small", "medium", "large"]
        if model_name not in valid_models:
            logger.warning(f"Invalid model '{model_name}', using 'small' instead")
            model_name = "small"
        
        # Load model with error handling
        try:
            model = whisper.load_model(model_name)
        except Exception as e:
            logger.error(f"Failed to load Whisper model '{model_name}': {e}")
            logger.info("Falling back to 'base' model")
            model = whisper.load_model("base")
            model_name = "base"
        
        logger.info(f"Successfully loaded Whisper model: {model_name}")
        logger.info("Transcribing audio (this may take a while depending on video length)...")
        
        # Simple transcription (avoid FFmpeg dependency issues)
        result = model.transcribe(video_path, verbose=False)
        
        segments = result.get("segments", [])
        
        # Validate segments
        if not segments:
            logger.warning("No speech segments detected in the audio")
            logger.info("This could be due to:")
            logger.info("- Very quiet or no audio in the video")
            logger.info("- Audio in a language not well supported")
            logger.info("- Poor audio quality")
        else:
            total_duration = segments[-1]["end"] if segments else 0
            logger.info(f"Transcribed {len(segments)} segments, total duration: {total_duration:.1f}s")
        
        # Save detailed JSON output
        out_json = OUT_DIR / (Path(video_path).stem + "_whisper.json")
        try:
            with open(out_json, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved transcript JSON to {out_json}")
        except Exception as e:
            logger.warning(f"Could not save JSON transcript: {e}")
        
        return segments
        
    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        logger.info("Returning empty segments list")
        return []

def segments_to_srt(segments, srt_path):
    """
    Write srt from whisper segments (list of dicts with start,end,text)
    """
    def fmt_time(t):
        h = int(t // 3600)
        m = int((t % 3600) // 60)
        s = int(t % 60)
        ms = int((t - int(t)) * 1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

    with open(srt_path, "w", encoding="utf-8") as f:
        if not segments:
            # Create placeholder subtitle for silent videos
            f.write("1\n")
            f.write("00:00:00,000 --> 00:00:05,000\n")
            f.write("[No speech detected in video]\n\n")
            logger.info(f"Created placeholder SRT (no audio): {srt_path}")
        else:
            for i, seg in enumerate(segments, start=1):
                start = seg["start"]
                end = seg["end"]
                text = seg["text"].strip().replace("\n", " ")
                f.write(f"{i}\n")
                f.write(f"{fmt_time(start)} --> {fmt_time(end)}\n")
                f.write(text + "\n\n")
            logger.info(f"Wrote SRT with {len(segments)} segments: {srt_path}")
