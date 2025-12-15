from utils import setup_logger

logger = setup_logger("summarizer")

def summarize_segment(text, max_length=50):
    """Basic text summarization"""
    if not text or len(text.split()) <= max_length:
        return text
    
    sentences = text.split('.')
    if len(sentences) <= 2:
        return text
    
    # Return first sentence + key phrases
    return sentences[0] + "..."

def extract_key_points(segments):
    """Extract key discussion points from transcript segments"""
    key_points = []
    for seg in segments:
        text = seg.get("text", "").strip()
        if len(text) > 20:  # Only meaningful segments
            summary = summarize_segment(text)
            key_points.append({
                "timestamp": seg.get("start", 0),
                "summary": summary,
                "duration": seg.get("end", 0) - seg.get("start", 0)
            })
    return key_points