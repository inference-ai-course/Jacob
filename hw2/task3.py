import os
import json
import pytesseract
from pytube import YouTube
import yt_dlp
import whisper
from PIL import Image
import subprocess
import tempfile

# Configuration
WHISPER_MODEL = "base"  # Whisper model size (tiny, base, small, medium, large)
TESSERACT_CONFIG = "--psm 6"  # Tesseract config for single uniform block of text
OUTPUT_FILE = "transcriptions.jsonl"

def download_youtube_audio(url, output_dir):
    """Download audio from YouTube video using yt-dlp"""
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': os.path.join(output_dir, '%(id)s.%(ext)s'),
        'quiet': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        audio_path = ydl.prepare_filename(info).replace('.webm', '.mp3').replace('.m4a', '.mp3')
        return audio_path, info['id'], info['title']

def extract_frames_with_text(video_url, output_dir):
    """Extract frames that might contain text using ffmpeg"""
    # This is a placeholder - in a real implementation, you'd need to:
    # 1. Download the video
    # 2. Use ffmpeg to extract frames at a reasonable interval
    # 3. Use OpenCV or similar to detect frames with potential text
    # For this example, we'll just return an empty list
    return []

def ocr_image(image_path):
    """Extract text from an image using Tesseract OCR"""
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img, config=TESSERACT_CONFIG)
        return text.strip()
    except Exception as e:
        print(f"OCR failed for {image_path}: {str(e)}")
        return ""

def transcribe_audio(audio_path):
    """Transcribe audio using Whisper"""
    model = whisper.load_model(WHISPER_MODEL)
    result = model.transcribe(audio_path)
    return result

def process_youtube_video(url):
    """Process a single YouTube video"""
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Processing {url}...")
        
        # Download audio
        audio_path, video_id, video_title = download_youtube_audio(url, temp_dir)
        
        # Extract frames with text (placeholder implementation)
        frames = extract_frames_with_text(url, temp_dir)
        ocr_results = []
        
        for frame_path in frames:
            text = ocr_image(frame_path)
            if text:
                ocr_results.append({
                    "frame_path": frame_path,
                    "text": text
                })
        
        # Transcribe audio
        whisper_result = transcribe_audio(audio_path)
        
        # Prepare final result
        result = {
            "video_id": video_id,
            "video_title": video_title,
            "audio_transcription": whisper_result,
            "ocr_results": ocr_results
        }
        
        return result

def main():
    # List of YouTube URLs to process
    youtube_urls = [
        # Add your 10 YouTube URLs here
        # "https://www.youtube.com/watch?v=...",
        # ...
    ]
    
    if not youtube_urls:
        print("Please add YouTube URLs to the youtube_urls list")
        return
    
    # Process each video
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        for url in youtube_urls:
            try:
                result = process_youtube_video(url)
                f.write(json.dumps(result, ensure_ascii=False) + '\n')
                print(f"Completed processing: {result['video_title']}")
            except Exception as e:
                print(f"Failed to process {url}: {str(e)}")
    
    print(f"All done! Results saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    # Check for required dependencies
    try:
        subprocess.run(["ffmpeg", "-version"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("Error: ffmpeg is required but not found. Please install it.")
        exit(1)
    
    try:
        subprocess.run(["tesseract", "--version"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("Error: tesseract is required but not found. Please install it.")
        exit(1)
    
    main()