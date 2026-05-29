"""
Facebook Reels Upload

Facebook Graph API for uploading Reels to Facebook Page.
Includes retry logic and video compression fallback for reliability.
"""

import os
import subprocess
import time
import requests
from pathlib import Path

def _compress_video(video_path, max_size_mb=8):
    """Compress video to stay under Facebook's size limit using ffmpeg."""
    compressed = Path(video_path).parent / "facebook_compressed.mp4"
    # Reduce bitrate to shrink file size
    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "28",
        "-c:a", "aac",
        "-b:a", "64k",
        "-movflags", "+faststart",
        str(compressed)
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    size_mb = compressed.stat().st_size / (1024 * 1024)
    print(f"[facebook] Compressed to {size_mb:.2f} MB")
    return compressed

def _do_upload(video_path, access_token, page_id, description):
    """Single attempt at uploading a video to Facebook."""
    url = f"https://graph.facebook.com/v24.0/{page_id}/videos"
    with open(video_path, 'rb') as video:
        files = {'source': video}
        data = {
            'access_token': access_token,
            'description': description[:500],
            'title': 'Classical Literature'
        }
        print(f"[facebook] Sending request to Facebook API...")
        response = requests.post(url, files=files, data=data, timeout=600)
    
    if response.status_code == 200:
        result = response.json()
        video_id = result.get('id')
        return video_id, None
    else:
        error_data = response.json() if response.text else {}
        error_msg = error_data.get('error', {}).get('message', 'Unknown error')
        error_code = error_data.get('error', {}).get('code', 'N/A')
        return None, f"Facebook API Error {response.status_code} (code {error_code}): {error_msg}"

def upload_to_facebook(video_path, description):
    """
    Upload video to Facebook Page with retry + compression fallback.
    
    Returns dict with upload status and details.
    """
    
    print("\n" + "=" * 60)
    print("📘 FACEBOOK UPLOAD STARTING")
    print("=" * 60)
    
    access_token = os.getenv('FB_ACCESS_TOKEN')
    page_id = os.getenv('FB_PAGE_ID')
    
    if not access_token:
        error_msg = "❌ FB_ACCESS_TOKEN not set in environment variables"
        print(f"[facebook] {error_msg}")
        raise ValueError(error_msg)
    
    if not page_id:
        error_msg = "❌ FB_PAGE_ID not set in environment variables"
        print(f"[facebook] {error_msg}")
        raise ValueError(error_msg)
    
    print(f"[facebook] ✅ Credentials loaded")
    print(f"[facebook] Page ID: {page_id}")
    print(f"[facebook] Token: {access_token[:20]}...")
    
    video_path_obj = Path(video_path)
    if not video_path_obj.exists():
        error_msg = f"❌ Video file not found: {video_path}"
        print(f"[facebook] {error_msg}")
        raise FileNotFoundError(error_msg)
    
    file_size_mb = video_path_obj.stat().st_size / (1024 * 1024)
    print(f"[facebook] ✅ Video file found: {video_path}")
    print(f"[facebook] Video size: {file_size_mb:.2f} MB")
    
    # Decide whether to compress upfront (files over 20MB often fail)
    current_video = video_path_obj
    if file_size_mb > 20:
        print(f"[facebook] Video is large ({file_size_mb:.1f}MB), compressing...")
        current_video = _compress_video(current_video)
    
    # Attempt 1: Direct upload (up to 3 tries)
    print(f"[facebook] 🚀 Uploading to Facebook Page...")
    max_attempts = 3
    for attempt in range(1, max_attempts + 1):
        print(f"[facebook] Upload attempt {attempt}/{max_attempts}...")
        video_id, error = _do_upload(current_video, access_token, page_id, description)
        
        if video_id:
            print(f"[facebook] ✅ SUCCESS! Video uploaded!")
            print(f"[facebook] Video ID: {video_id}")
            print(f"[facebook] Check your Facebook Page to see the post!")
            print("=" * 60)
            
            # Clean up compressed file if it exists
            if current_video != video_path_obj and current_video.exists():
                current_video.unlink()
            
            return {
                'id': video_id,
                'platform': 'facebook',
                'status': 'success',
                'url': f"https://facebook.com/{video_id}"
            }
        
        print(f"[facebook] ❌ Attempt {attempt} failed: {error}")
        
        # On "reduce data" error, try compressing and retrying
        if "reduce the amount of data" in error.lower():
            print(f"[facebook] Data limit hit — compressing video before retry...")
            if current_video == video_path_obj or current_video.stat().st_size > 5 * 1024 * 1024:
                compressed = _compress_video(current_video, max_size_mb=5)
                if current_video != video_path_obj and current_video.exists():
                    current_video.unlink()
                current_video = compressed
        
        if attempt < max_attempts:
            wait = attempt * 10
            print(f"[facebook] Waiting {wait}s before retry...")
            time.sleep(wait)
    
    print("=" * 60)
    raise Exception(f"Facebook upload failed after {max_attempts} attempts. Last error: {error}")

if __name__ == '__main__':
    # Test upload
    from pathlib import Path
    
    video_file = Path('output/final_video.mp4')
    if video_file.exists():
        story_file = Path('output/story.txt')
        description = story_file.read_text(encoding='utf-8') if story_file.exists() else "Test upload"
        
        try:
            result = upload_to_facebook(video_file, description)
            print(f"\n✅ Test successful! Result: {result}")
        except Exception as e:
            print(f"\n❌ Test failed: {e}")
    else:
        print(f"❌ Video not found: {video_file}")
