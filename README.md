# Meeting Video Captioning & Documentation

A comprehensive Python-based solution for automatically generating detailed documented reports with captions for meeting videos. This system ensures no important information is missed by capturing every screen change, interaction, and associating captions with precise timestamps.

## 🎯 Features

### Video Input Support
- **Local Video Files**: MP4, MOV, AVI, MKV, WMV
- **YouTube Videos**: Public video URLs
- **Web Platform Videos**: HTTP/HTTPS direct links
- **Google Drive**: Shared video links
- **Private Platforms**: Videos requiring user credentials (with Selenium automation)

### Core Capabilities
- **Automatic Caption Generation**: Speech-to-text transcription using OpenAI Whisper
- **Scene Change Detection**: Intelligent detection of content transitions, slides, and interactions
- **Burned-in Captions**: Captions permanently embedded in the video
- **Detailed Reports**: Timestamped documentation in DOCX format
- **Single-Click Processing**: Fully automated pipeline with minimal user input

### Advanced Features
- **Cross-Platform Support**: Windows, macOS, and Linux
- **Multiple Whisper Models**: From tiny (fast) to large (accurate)
- **Configurable Sensitivity**: Adjustable scene change detection
- **Error Handling**: Robust error recovery and user feedback
- **GUI Interface**: User-friendly graphical interface
- **Command Line Interface**: For automation and scripting

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or download the project
cd mva_project

# Run the setup script (recommended)
python setup.py

# Or install manually
pip install -r requirements.txt
```

### 2. Launch GUI (Easiest Method)

```bash
python run.py --gui
```

### 3. Command Line Usage

```bash
# Process local video
python run.py -i "path/to/video.mp4"

# Process YouTube video
python run.py -i "https://youtube.com/watch?v=..." -t youtube

# Process with custom settings
python run.py -i "video.mp4" --whisper medium --diff 0.25
```

## 📋 System Requirements

### Software Requirements
- **Python 3.8+** (Required)
- **FFmpeg** (Required for video processing)
- **Chrome Browser** (Required for private platform access)

### Hardware Recommendations
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 5GB free space for processing
- **CPU**: Multi-core processor recommended
- **GPU**: Optional, for faster Whisper transcription

## 🎮 Usage Guide

### GUI Interface

1. **Launch the GUI**: `python run.py --gui`
2. **Select Input Type**: Local file, YouTube, or HTTP URL
3. **Choose Video**: Browse for local files or paste URL
4. **Adjust Settings**: 
   - Whisper model (tiny/base/small/medium/large)
   - Scene change threshold (0.1-1.0)
5. **Click "Process Video"**: Single-click processing
6. **View Results**: Open generated video and report

### Command Line Interface

```bash
# Basic usage
python run.py -i INPUT_SOURCE [OPTIONS]

# Options:
-t, --type          Input type: local|youtube|http|private|gdrive
--whisper          Whisper model: tiny|base|small|medium|large
--diff             Scene change threshold: 0.1-1.0
--username         Username for private platforms
--password         Password for private platforms
--gui              Launch GUI interface
```

### Examples

```bash
# Local video with high accuracy
python run.py -i "meeting.mp4" --whisper large

# YouTube video with sensitive detection
python run.py -i "https://youtube.com/watch?v=xyz" -t youtube --diff 0.15

# Private platform (requires credentials)
python run.py -i "https://company.com/video" -t private --username user --password pass

# Google Drive shared video
python run.py -i "https://drive.google.com/file/d/xyz" -t gdrive
```

## 📁 Output Structure

```
data/
├── videos/          # Downloaded videos
├── frames/          # Extracted scene frames
├── transcripts/     # Audio transcriptions (.srt, .json)
├── captioned/       # Videos with burned-in captions
└── reports/         # Detailed DOCX reports

logs/                # Application logs
```

## 📊 Generated Reports

Each report includes:
- **Video Information**: Title, duration, source
- **Scene Analysis**: Timestamped screenshots of every significant change
- **Interaction Detection**: Clicks, transitions, slide changes
- **Full Transcription**: Complete speech-to-text with timestamps
- **Segment Summaries**: Key points for each video section
- **Visual Documentation**: Screenshots with associated captions

## ⚙️ Configuration

### Whisper Models
- **tiny**: Fastest, least accurate (~39 MB)
- **base**: Good balance (~74 MB)
- **small**: Recommended default (~244 MB)
- **medium**: Higher accuracy (~769 MB)
- **large**: Best accuracy (~1550 MB)

### Scene Detection Sensitivity
- **0.1-0.2**: Very sensitive (detects minor changes)
- **0.3-0.4**: Balanced (recommended)
- **0.5-1.0**: Less sensitive (major changes only)

## 🔧 Troubleshooting

### Common Issues

**FFmpeg not found**
```bash
# Windows: Download from https://ffmpeg.org/
# macOS: brew install ffmpeg
# Linux: sudo apt-get install ffmpeg
```

**Whisper model download fails**
- Check internet connection
- Try smaller model first
- Ensure sufficient disk space

**Video download fails**
- Verify URL is accessible
- Check for private/restricted content
- Try different video quality

**GUI doesn't start**
- Ensure tkinter is installed
- Try: `python -m tkinter` to test
- Use command line interface as fallback

### Performance Optimization

**For faster processing:**
- Use smaller Whisper models (tiny/base)
- Increase scene change threshold
- Process shorter video segments
- Use SSD storage for temporary files

**For better accuracy:**
- Use larger Whisper models (medium/large)
- Decrease scene change threshold
- Ensure good audio quality
- Process in quiet environment

## 🔒 Security & Privacy

- **Credentials**: Never hardcoded, passed securely
- **Local Processing**: All processing done locally
- **No Data Collection**: No telemetry or data sharing
- **Temporary Files**: Cleaned up after processing
- **Private Videos**: Handled with appropriate access controls

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs in the `logs/` directory
3. Create an issue with detailed information
4. Include system information and error messages

## 🔄 Updates

To update the application:
```bash
git pull origin main
python setup.py  # Re-run setup if needed
```

---

**Note**: This application processes videos locally and requires significant computational resources for large videos. Processing time varies based on video length, quality, and selected accuracy settings.