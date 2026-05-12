import os
import urllib.parse
from dotenv import load_dotenv

load_dotenv()

class VideoGenerator:
    def __init__(self, provider="free"):
        self.provider = provider

    def generate_video(self, prompt):
        """
        Generates a video. Currently supports Pollinations.ai for free generation.
        """
        if self.provider == "free":
            return self._generate_free(prompt)
        else:
            return "Error: Only 'free' provider is currently supported for video."

    def _generate_free(self, prompt):
        """
        Uses Pollinations.ai for free video generation.
        """
        encoded_prompt = urllib.parse.quote(prompt)
        # Pollinations.ai video endpoint
        video_url = f"https://gen.pollinations.ai/video/{encoded_prompt}"
        return video_url

if __name__ == "__main__":
    gen = VideoGenerator()
    print(f"Free video URL: {gen.generate_video('A futuristic city at sunset')}")
