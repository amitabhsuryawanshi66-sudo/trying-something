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
        Uses Pollinations.ai for free image generation and converts it to a video clip.
        This ensures compatibility and a 'free' experience without API keys.
        """
        try:
            import requests
            from moviepy.editor import ImageClip

            encoded_prompt = urllib.parse.quote(prompt)
            # Use high-quality 9:16 aspect ratio (720x1280) for Reels
            image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=720&height=1280&nologo=true"

            response = requests.get(image_url)
            if response.status_code != 200:
                return f"Error: Image generation failed with status {response.status_code}"

            temp_img = "temp_visual.jpg"
            with open(temp_img, "wb") as f:
                f.write(response.content)

            # Create a 5-second video clip from the image
            # This is robust and guaranteed to work as long as Pollinations image API is up
            output_video = "generated_reel.mp4"
            clip = ImageClip(temp_img).set_duration(5)
            # Write to file - libx264 is standard for Instagram
            clip.write_videofile(output_video, fps=24, codec="libx264", audio=False)

            return os.path.abspath(output_video)
        except Exception as e:
            return f"Error in free video generation: {e}"

if __name__ == "__main__":
    gen = VideoGenerator()
    print(f"Free video URL: {gen.generate_video('A futuristic city at sunset')}")
