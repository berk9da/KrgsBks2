import os
import requests
from pathlib import Path

def upload_to_telegram():
    """Upload video to Telegram channel."""
    print("-" * 50)
    print("TELEGRAM UPLOAD")
    print("-" * 50)

    # 1. Get credentials
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    channel_id = os.getenv("TELEGRAM_CHANNEL_ID")

    if not bot_token or not channel_id:
        print("[telegram] ⚠️ TELEGRAM_BOT_TOKEN or TELEGRAM_CHANNEL_ID not set. Skipping.")
        return

    # 2. Get video file
    video_path = Path("output/final_video.mp4")
    if not video_path.exists():
        print("[telegram] ❌ Video file not found at output/final_video.mp4")
        return

    # 3. Get title/caption from topic
    caption = "#ClassicalLiterature #Books #Literature\\n\\nDiscover timeless wisdom 📚"
    try:
        topic_path = Path("output/topic.txt")
        if topic_path.exists():
            topic = topic_path.read_text(encoding="utf-8").strip()
            clean_topic = topic.replace('[BOOK] ', '')
            
            if ' by ' in clean_topic:
                book_title = clean_topic.split(' by ')[0]
                author = clean_topic.split(' by ')[1].strip()
                caption = f"**{book_title} by {author}**\\n\\n#ClassicalLiterature #Books #Literature\\n\\n📚 Discover timeless wisdom!"
            else:
                caption = f"**{clean_topic}**\\n\\n#ClassicalLiterature #Books #Literature\\n\\n📚 Discover timeless wisdom!"
    except Exception as e:
        print(f"[telegram] Warning reading topic: {e}")

    # 4. Upload
    print(f"[telegram] Uploading video to {channel_id}...")
    
    url = f"https://api.telegram.org/bot{bot_token}/sendVideo"
    
    try:
        with open(video_path, "rb") as video_file:
            files = {"video": video_file}
            data = {
                "chat_id": channel_id,
                "caption": caption,
                "parse_mode": "Markdown",
                "supports_streaming": "true"
            }
            
            response = requests.post(url, files=files, data=data, timeout=120)
            response.raise_for_status()
            
            print("[telegram] ✅ Upload successful!")
            try:
                result = response.json()
                if result.get("ok"):
                    print(f"[telegram] Message ID: {result['result']['message_id']}")
                else:
                    print(f"[telegram] API returned error: {result}")
            except:
                pass
                
    except Exception as e:
        print(f"[telegram] ❌ Upload failed: {e}")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    upload_to_telegram()
