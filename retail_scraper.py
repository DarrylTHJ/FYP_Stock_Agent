import time
import os
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

# Configuration
SOURCE_FILE = "retail_sources.txt"
OUTPUT_DIR = "data/retail/scraped"

def extract_video_id(url):
    """Simple helper to grab ID from URL"""
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]
    elif "youtu.be" in url:
        return url.split("/")[-1]
    return None

def batch_scrape_retail():
    # Ensure directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Read the manifest
    if not os.path.exists(SOURCE_FILE):
        print(f"❌ Error: {SOURCE_FILE} not found. Please create it first.")
        return

    with open(SOURCE_FILE, "r") as f:
        urls = [line.strip() for line in f if line.strip()]

    print(f"📋 Found {len(urls)} videos to process...")

    for i, url in enumerate(urls):
        video_id = extract_video_id(url)
        if not video_id:
            print(f"⚠️ Skipping invalid URL: {url}")
            continue

        # Check if already downloaded (Idempotency)
        output_filename = os.path.join(OUTPUT_DIR, f"retail_{video_id}.txt")
        if os.path.exists(output_filename):
            print(f"⏭️  [Skipping] {video_id} - Already exists.")
            continue

        print(f"⬇️  [{i+1}/{len(urls)}] Fetching: {video_id}...")

        try:
            # The Robust Method (Instantiate Class)
            api = YouTubeTranscriptApi()
            transcript = api.fetch(video_id, languages=['zh-Hans', 'zh-Hant', 'en'])
            
            formatter = TextFormatter()
            text_formatted = formatter.format_transcript(transcript)

            with open(output_filename, "w", encoding="utf-8") as f:
                f.write(text_formatted)
            
            print("   ✅ Saved!")

            # BE POLITE - Wait 2 seconds between hits so YouTube doesn't block you
            time.sleep(2)

        except Exception as e:
            print(f"   ❌ Failed: {e}")

if __name__ == "__main__":
    batch_scrape_retail()