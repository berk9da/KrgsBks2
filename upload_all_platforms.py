"""
Multi-Platform Upload Script

Uploads videos to:
- YouTube Shorts
- Instagram Reels
- TikTok
- Facebook Reels

Each platform requires its own API credentials.
"""

import os
from pathlib import Path
import datetime

# Import platform-specific uploaders
from upload_to_youtube import upload_to_youtube
from upload_instagram import upload_to_instagram
from upload_tiktok import upload_to_tiktok
from upload_facebook import upload_to_facebook
from upload_threads import upload_to_threads
from upload_twitter import upload_to_twitter
from upload_telegram import upload_to_telegram

def main():
    """Upload video to all configured platforms."""
    video_file = Path('output/final_video.mp4')
    
    if not video_file.exists():
        print("[upload] ❌ No video found at output/final_video.mp4")
        return
    
    # Read the selected topic for dynamic metadata
    topic_file = Path('output/topic.txt')
    if topic_file.exists():
        topic = topic_file.read_text(encoding='utf-8').strip()
        clean_topic = topic.replace('[BOOK] ', '')
        
        # Extract book title and author
        if ' by ' in clean_topic:
            book_title = clean_topic.split(' by ')[0].strip()
            author = clean_topic.split(' by ')[1].strip()
        else:
            book_title = clean_topic
            author = ''
        
        # Create platform-specific content
        youtube_title = f"{book_title} by {author} - Book Summary #Shorts"[:100]
        
        caption = f"""📚 {book_title} by {author}

Discover this timeless literary masterpiece!

A powerful summary of one of history's greatest books.

#ClassicalLiterature #BookSummary #{book_title.replace(' ', '')} #{author.split()[-1] if author else 'Books'} #Literature #Books #Reading #Education"""
        
        youtube_description = f"""📚 {book_title} by {author}

Discover the timeless wisdom of classical literature through this powerful summary and analysis.

This video presents the key themes, plot points, and lasting impact of this literary masterpiece.

Perfect for students, book lovers, and anyone who loves great storytelling!

#Shorts #ClassicalLiterature #BookSummary #Literature #Books #Reading #Education #{book_title.replace(' ', '')} #{author.split()[-1] if author else 'ClassicBooks'}"""
        
    else:
        book_title = "Classic Literature"
        youtube_title = "Classic Literature Summary #Shorts"
        caption = "📚 Discover timeless classics!\n\n#ClassicalLiterature #BookSummary #Literature #Books"
        youtube_description = "Discover the timeless wisdom of classical literature.\n\n#Shorts #ClassicalLiterature #BookSummary"
    
    tags = [
        'Classical Literature', 'Book Summary', 'Literature',
        'Shorts', 'Books', 'Reading', 'Education', 'Book Review',
        book_title, author if author else 'Classic Books'
    ]

    
    results = {}
    
    # Upload to YouTube
    if all([
        os.getenv('YT_CLIENT_ID'),
        os.getenv('YT_CLIENT_SECRET'),
        os.getenv('YT_REFRESH_TOKEN')
    ]):
        print("\n" + "="*60)
        print("📺 Uploading to YouTube...")
        print("="*60)
        try:
            result = upload_to_youtube(video_file, youtube_title, youtube_description, tags)
            results['youtube'] = result
            print(f"✅ YouTube: https://youtube.com/shorts/{result['id']}")
        except Exception as e:
            print(f"❌ YouTube failed: {e}")
            results['youtube'] = None
    else:
        print("⏭️  Skipping YouTube (credentials not set)")
    
    # Upload to Instagram
    if all([
        os.getenv('IG_ACCESS_TOKEN'),
        os.getenv('IG_USER_ID')
    ]):
        print("\n" + "="*60)
        print("📸 Uploading to Instagram...")
        print("="*60)
        try:
            result = upload_to_instagram(video_file, caption)
            results['instagram'] = result
            print(f"✅ Instagram: Uploaded successfully")
        except Exception as e:
            print(f"❌ Instagram failed: {e}")
            results['instagram'] = None
    else:
        print("⏭️  Skipping Instagram (credentials not set)")
    
    # Upload to TikTok
    if os.getenv('TIKTOK_ACCESS_TOKEN'):
        print("\n" + "="*60)
        print("🎵 Uploading to TikTok...")
        print("="*60)
        try:
            result = upload_to_tiktok(video_file, youtube_title, caption)
            results['tiktok'] = result
            print(f"✅ TikTok: Uploaded successfully")
        except Exception as e:
            print(f"❌ TikTok failed: {e}")
            results['tiktok'] = None
    else:
        print("⏭️  Skipping TikTok (credentials not set)")
    
    # Upload to Facebook
    if all([
        os.getenv('FB_ACCESS_TOKEN'),
        os.getenv('FB_PAGE_ID')
    ]):
        print("\n" + "="*60)
        print("📘 Uploading to Facebook...")
        print("="*60)
        try:
            result = upload_to_facebook(video_file, caption)
            results['facebook'] = result
            print(f"✅ Facebook: Uploaded successfully")
        except Exception as e:
            print(f"❌ Facebook failed: {e}")
            results['facebook'] = None
    else:
        print("⏭️  Skipping Facebook (credentials not set)")
    
    # Upload to Threads
    if all([
        os.getenv('THREADS_ACCESS_TOKEN'),
        os.getenv('THREADS_USER_ID')
    ]):
        print("\n" + "="*60)
        print("🧵 Uploading to Threads...")
        print("="*60)
        try:
            result = upload_to_threads(video_file, caption)
            results['threads'] = result
            print(f"✅ Threads: Uploaded successfully")
        except Exception as e:
            print(f"❌ Threads failed: {e}")
            results['threads'] = None
    else:
        print("⏭️  Skipping Threads (credentials not set)")
    
    # Upload to Twitter/X
    if all([
        os.getenv('TWITTER_API_KEY'),
        os.getenv('TWITTER_API_SECRET'),
        os.getenv('TWITTER_ACCESS_TOKEN'),
        os.getenv('TWITTER_ACCESS_SECRET')
    ]):
        print("\n" + "="*60)
        print("🐦 Uploading to Twitter/X...")
        print("="*60)
        try:
            result = upload_to_twitter(video_file, caption)
            results['twitter'] = result
            print(f"✅ Twitter: Uploaded successfully")
        except Exception as e:
            print(f"❌ Twitter failed: {e}")
            results['twitter'] = None
    else:
        print("⏭️  Skipping Twitter (credentials not set)")
    
    # Upload to Telegram
    if all([
        os.getenv('TELEGRAM_BOT_TOKEN'),
        os.getenv('TELEGRAM_CHANNEL_ID')
    ]):
        print("\n" + "="*60)
        print("✈️ Uploading to Telegram...")
        print("="*60)
        try:
            upload_to_telegram()
            results['telegram'] = True
        except Exception as e:
            print(f"❌ Telegram failed: {e}")
            results['telegram'] = None
    else:
        print("⏭️  Skipping Telegram (credentials not set)")
    
    # Summary
    print("\n" + "="*60)
    print("📊 Upload Summary")
    print("="*60)
    for platform, result in results.items():
        status = "✅ Success" if result else "❌ Failed"
        print(f"{platform.capitalize()}: {status}")
    print("="*60)

if __name__ == '__main__':
    main()
