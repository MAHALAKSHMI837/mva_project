# shortened
# burn_captions.py
import subprocess
from pathlib import Path
from utils import setup_logger, ensure_dir

logger = setup_logger("burn_captions")
OUT_DIR = ensure_dir("data/captioned")

def burn_srt_into_video(input_video, srt_path, out_path=None):
    if out_path is None:
        out_path = OUT_DIR / (Path(input_video).stem + "_captioned.mp4")
    else:
        out_path = Path(out_path)
    
    # Try multiple FFmpeg paths
    ffmpeg_paths = [
        "ffmpeg",
        r"C:\ffmpeg\bin\ffmpeg.exe", 
        r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
        r"C:\Users\Dell\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-7.1-full_build\bin\ffmpeg.exe"
    ]
    
    ffmpeg_cmd = None
    for path in ffmpeg_paths:
        try:
            subprocess.run([path, "-version"], capture_output=True, check=True)
            ffmpeg_cmd = path
            break
        except:
            continue
    
    if not ffmpeg_cmd:
        logger.error("FFmpeg not found in any common location")
        # Copy original video as fallback
        import shutil
        shutil.copy2(input_video, out_path)
        logger.info(f"Copied original video (no captions): {out_path}")
        return str(out_path)
    
    # Fix Windows path issues for FFmpeg
    srt_path_fixed = str(srt_path).replace("\\", "/")
    
    cmd = [
        ffmpeg_cmd, "-y",
        "-i", str(input_video),
        "-vf", f"subtitles='{srt_path_fixed}'",
        "-c:a", "copy",
        str(out_path)
    ]
    logger.info("Running ffmpeg to burn subtitles...")
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        logger.error("ffmpeg failed: " + str(e))
        raise
    except FileNotFoundError:
        logger.error("FFmpeg not found in PATH")
        raise
    logger.info(f"Captioned video saved to {out_path}")
    return str(out_path)
