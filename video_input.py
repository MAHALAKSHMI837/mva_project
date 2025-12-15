# shortened due to length; same as previous message
from utils import setup_logger, ensure_dir
# ... placeholder content
# video_input.py
import os
import requests
from pytube import YouTube
# yt-dlp installed for better YouTube support
from pathlib import Path
from utils import setup_logger, ensure_dir

logger = setup_logger("video_input")

DOWNLOAD_DIR = ensure_dir("data/videos")

def from_local(path):
    p = Path(path)
    if not p.exists():
        logger.error(f"Local file not found: {path}")
        raise FileNotFoundError(f"Video file not found: {path}")
    
    # Validate file format
    supported_formats = ['.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv', '.webm']
    if p.suffix.lower() not in supported_formats:
        logger.warning(f"File format {p.suffix} may not be supported. Supported: {supported_formats}")
    
    # Check file size
    file_size = p.stat().st_size
    logger.info(f"Video file size: {file_size / (1024*1024):.1f} MB")
    
    return str(p.resolve())

def from_youtube(url, resolution="720p"):
    logger.info(f"Downloading YouTube: {url}")
    
    # Try yt-dlp first (more reliable)
    try:
        import subprocess
        
        # Extract video ID for filename
        video_id = url.split('v=')[-1].split('&')[0] if 'v=' in url else url.split('/')[-1]
        output_template = str(DOWNLOAD_DIR / f"{video_id}.%(ext)s")
        
        cmd = [
            "yt-dlp", 
            "-f", "best[ext=mp4]/best",
            "-o", output_template,
            url
        ]
        
        logger.info("Trying yt-dlp downloader...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            # Find the downloaded file
            for file in DOWNLOAD_DIR.glob(f"{video_id}.*"):
                if file.suffix in ['.mp4', '.webm', '.mkv']:
                    logger.info(f"Downloaded with yt-dlp: {file}")
                    return str(file)
                    
    except Exception as e:
        logger.warning(f"yt-dlp failed: {e}")
    
    # Fallback to pytube
    try:
        logger.info("Trying pytube downloader...")
        yt = YouTube(url)
        stream = yt.streams.filter(progressive=True, file_extension='mp4').first()
        if not stream:
            stream = yt.streams.filter(file_extension='mp4').first()
        
        if stream:
            out = stream.download(output_path=str(DOWNLOAD_DIR))
            logger.info(f"Downloaded with pytube: {out}")
            return out
            
    except Exception as e:
        logger.error(f"All YouTube downloaders failed: {e}")
    
    raise Exception("YouTube download failed. Use a local video file instead.")

def from_http(url, filename=None):
    logger.info(f"Downloading HTTP resource: {url}")
    if not filename:
        filename = url.split("?")[0].split("/")[-1] or "downloaded_video.mp4"
    
    # Ensure filename has extension
    if not any(filename.endswith(ext) for ext in ['.mp4', '.mov', '.avi', '.mkv']):
        filename += '.mp4'
    
    dest = DOWNLOAD_DIR / filename
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        with requests.get(url, stream=True, headers=headers, timeout=30) as r:
            r.raise_for_status()
            
            # Get file size if available
            total_size = int(r.headers.get('content-length', 0))
            
            with open(dest, "wb") as f:
                downloaded = 0
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            if downloaded % (1024 * 1024) == 0:  # Log every MB
                                logger.info(f"Downloaded {progress:.1f}%")
                                
    except requests.exceptions.RequestException as e:
        logger.error(f"Download failed: {e}")
        if dest.exists():
            dest.unlink()  # Clean up partial download
        raise
    
    logger.info(f"Saved to {dest}")
    return str(dest)

def from_private(url, username=None, password=None, download_path=None):
    """
    Download from private platforms requiring authentication.
    Uses Selenium for login and video extraction.
    """
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from webdriver_manager.chrome import ChromeDriverManager
    import time
    
    if not username or not password:
        raise ValueError("Username and password required for private platform access")
    
    logger.info(f"Accessing private platform: {url}")
    
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    try:
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
        driver.get(url)
        
        # Generic login handling - adapt based on platform
        try:
            # Look for common login elements
            username_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "username")) or
                EC.presence_of_element_located((By.NAME, "email")) or
                EC.presence_of_element_located((By.ID, "username"))
            )
            password_field = driver.find_element(By.NAME, "password") or driver.find_element(By.ID, "password")
            
            username_field.send_keys(username)
            password_field.send_keys(password)
            
            # Find and click login button
            login_btn = driver.find_element(By.XPATH, "//button[@type='submit']" or "//input[@type='submit']")
            login_btn.click()
            
            # Wait for login to complete
            time.sleep(3)
            
        except Exception as e:
            logger.warning(f"Automated login failed: {e}. Manual intervention may be required.")
        
        # Try to find video source
        video_elements = driver.find_elements(By.TAG_NAME, "video")
        if video_elements:
            video_src = video_elements[0].get_attribute("src")
            if video_src:
                logger.info(f"Found video source: {video_src}")
                driver.quit()
                return from_http(video_src, download_path)
        
        # If direct video not found, try to find download links
        download_links = driver.find_elements(By.XPATH, "//a[contains(@href, '.mp4') or contains(@href, '.mov') or contains(@href, '.avi')]")
        if download_links:
            download_url = download_links[0].get_attribute("href")
            logger.info(f"Found download link: {download_url}")
            driver.quit()
            return from_http(download_url, download_path)
        
        driver.quit()
        raise Exception("Could not locate video source on the page")
        
    except Exception as e:
        logger.error(f"Private platform access failed: {e}")
        raise

def from_google_drive(url, download_path=None):
    """
    Download from Google Drive shared links.
    """
    import re
    
    # Extract file ID from Google Drive URL
    file_id_match = re.search(r'/d/([a-zA-Z0-9-_]+)', url)
    if not file_id_match:
        raise ValueError("Invalid Google Drive URL")
    
    file_id = file_id_match.group(1)
    download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
    
    logger.info(f"Downloading from Google Drive: {file_id}")
    return from_http(download_url, download_path or f"gdrive_{file_id}.mp4")
