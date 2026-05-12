import os
import requests
from content_gen import ContentGenerator
from video_gen import VideoGenerator
from social_manager import InstagramManager
from dotenv import load_dotenv

def download_file(url, local_filename):
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return local_filename

def run_reel_automation(topic, provider="free"):
    load_dotenv()

    # 1. Idea & Script Generation
    print(f"Generating plan for topic: {topic}...")
    content_gen = ContentGenerator(provider=provider)
    plan_raw = content_gen.generate_reel_plan(topic)

    # Parse the plan
    plan = {}
    for line in plan_raw.split('\n'):
        if line.startswith('IDEA:'): plan['idea'] = line.replace('IDEA:', '').strip()
        if line.startswith('SCRIPT:'): plan['script'] = line.replace('SCRIPT:', '').strip()
        if line.startswith('VISUAL:'): plan['visual'] = line.replace('VISUAL:', '').strip()

    if not plan.get('visual'):
        plan['visual'] = topic # Fallback

    # 2. Visual Generation
    print("Generating video...")
    video_gen = VideoGenerator(provider=provider)
    video_url = video_gen.generate_video(plan['visual'])

    # 3. Prepare for download (needed for posting)
    local_video = f"reel_{topic.replace(' ', '_')}.mp4"
    # Note: Downloading might fail if the URL isn't immediately ready or valid
    # In a real app, we'd add retries

    return {
        "plan": plan,
        "video_url": video_url,
        "local_video": local_video
    }

if __name__ == "__main__":
    results = run_reel_automation("Morning routine of an AI")
    print(f"Automation results: {results}")
