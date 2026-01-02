from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

# 5 ways to grow your snowball
VIDEO_ID = "ob2wq6VjmM0" 

def fetch_youtube_transcript(video_id):
    try:
        # Instantiate the class first, then call .fetch()
        
        api = YouTubeTranscriptApi() 
        transcript = api.fetch(video_id, languages=['zh-Hans', 'zh-Hant', 'en'])
        
        # -----------------------

        # Format the text
        formatter = TextFormatter()
        #Pass the transcript object directly first (standard for v1.2+).
        text_formatted = formatter.format_transcript(transcript)
        
        # Save to file
        filename = f"data_raw/retail_{video_id}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(text_formatted)
            
        print(f"✅ Success! Transcript saved to {filename}")
        print("Preview of text:")
        print(text_formatted[:200])

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    fetch_youtube_transcript(VIDEO_ID)