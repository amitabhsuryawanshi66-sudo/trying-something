import os
import requests
from content_gen import ContentGenerator
from video_gen import VideoGenerator
from social_manager import InstagramManager
from dotenv import load_dotenv

def download_file(url, local_filename):
    # Check if the URL is actually a local file path
    if os.path.exists(url):
        # Already local, just return it
        return url

    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return local_filename

def run_reel_automation(topic, provider="pollinations", openai_key=None, groq_key=None):
    load_dotenv()

    # 1. Idea & Script Generation
    print(f"Generating plan for topic: {topic} using {provider}...")
    content_gen = ContentGenerator(api_key=openai_key, provider=provider, groq_key=groq_key)
    plan = content_gen.generate_reel_plan(topic)

    # 2. Visual Generation
    print("Generating video...")
    # For now, video_gen primarily uses 'free' mode for the image-to-video pipeline
    video_gen = VideoGenerator(provider="free")
    video_url = video_gen.generate_video(plan['visual'])

    # 3. Prepare for download (needed for posting)
    # The video_url might already be a local path from our generator
    local_video = video_url if os.path.exists(video_url) else f"reel_{topic.replace(' ', '_')}.mp4"

    return {
        "plan": plan,
        "video_url": video_url,
        "local_video": local_video
    }

if __name__ == "__main__":
    # Test with default pollinations
    results = run_reel_automation("Morning routine of an AI")
    print(f"Automation results: {results}")
