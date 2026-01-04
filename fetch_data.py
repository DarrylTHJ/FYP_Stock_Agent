import os
import time
import random
import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

# --- CONFIGURATION ---
DATA_RAW_RETAIL = "./data/retail/scraped"
DATA_RAW_INST = "./data/institutional/scraped"

# TARGET: The "Videos" tab of the channel
# Example: https://www.youtube.com/@SparkLiang/videos
TARGET_URLS = [
    "https://www.youtube.com/@AlfredChenOfficial/videos", 
]

def sanitize_filename(name):
    # Aggressive cleaning to avoid Windows file path errors
    clean = "".join([c for c in name if c.isalpha() or c.isdigit() or c in " .-_"]).strip()
    return clean[:100] # Limit filename length

def fetch_youtube_transcripts():
    print("\n📺 Starting Full Channel Scan...")
    
    ydl_opts = {
        'extract_flat': True,       # Fast scan (metadata only)
        'quiet': True,
        'ignoreerrors': True,
        # 'playlistend': 50,  <--- DELETED: Now fetches EVERYTHING
    }

    formatter = TextFormatter()

    for url in TARGET_URLS:
        print(f"   Scanning Channel: {url}")
        print("   (This may take a minute if the channel is huge...)")
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                # 1. Get the list of ALL videos
                info = ydl.extract_info(url, download=False)
                
                if 'entries' not in info: 
                    print("   ❌ No videos found.")
                    continue
                    
                videos = list(info['entries']) # Convert generator to list
                total_videos = len(videos)
                print(f"   📋 Found {total_videos} total videos.")
                
            except Exception as e:
                print(f"      ❌ Channel Error: {e}")
                continue

            # 2. Iterate through them
            for i, video in enumerate(videos):
                if not video: continue
                
                video_id = video.get('id')
                title = sanitize_filename(video.get('title', 'Unknown'))
                
                # Filename format
                filename = f"retail_{video_id}.txt"
                filepath = os.path.join(DATA_RAW_RETAIL, filename)
                
                # --- CHECKPOINT: SKIP EXISTING ---
                if os.path.exists(filepath):
                    # Print every 50 skips just so you know it's alive
                    if i % 50 == 0:
                        print(f"      ⏭️  Skipped {i}/{total_videos} (Already downloaded)")
                    continue 

                # --- PROCESSING NEW FILE ---
                print(f"   ⬇️  [{i+1}/{total_videos}] Fetching: {title}...")
                
                try:
                    # A. Instantiate
                    api = YouTubeTranscriptApi()
                    
                    # B. Fetch (Chinese first, then English)
                    transcript = api.fetch(
                        video_id, 
                        languages=['zh-Hans', 'zh-Hant', 'en', 'zh']
                    )
                    
                    # C. Save
                    formatted_text = formatter.format_transcript(transcript)
                    file_content = f"Title: {title}\nSource: YouTube ({video_id})\n\n{formatted_text}"
                    
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(file_content)
                        
                    print(f"       ✅ Saved!")
                    
                    # D. SAFETY SLEEP (Randomized)
                    # 20s to 40s is the safe zone for bulk downloading
                    sleep_time = random.uniform(20, 40)
                    print(f"       ⏳ Pausing {sleep_time:.1f}s...")
                    time.sleep(sleep_time)
                    
                except Exception as e:
                    print(f"       ⚠️ Failed: {e}")
                    # If it's a 'TranscriptsDisabled' error, we just move on fast.
                    # If it's a network error, we wait a bit.
                    if "Too Many Requests" in str(e):
                        print("       🛑 RATE LIMIT HIT. Sleeping 5 minutes...")
                        time.sleep(300)
                    else:
                        time.sleep(2) # Short pause for minor errors

def main_loop():
    os.makedirs(DATA_RAW_RETAIL, exist_ok=True)
    os.makedirs(DATA_RAW_INST, exist_ok=True)
    
    print("==============================================")
    print(f"   FULL CHANNEL ARCHIVER")
    print(f"   Target Folder: {DATA_RAW_RETAIL}")
    print("==============================================")

    while True:
        fetch_youtube_transcripts()
        print("\n✅ Channel scan complete!")
        print("💤 Sleeping for 12 hours before next check...")
        time.sleep(43200) 

if __name__ == "__main__":
    main_loop()