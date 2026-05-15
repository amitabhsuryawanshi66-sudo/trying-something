import os
import urllib.parse
from PIL import Image
from dotenv import load_dotenv

# Fix Pillow/MoviePy compatibility issue
if not hasattr(Image, "ANTIALIAS"):
    Image.ANTIALIAS = Image.Resampling.LANCZOS

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
            import uuid
            from moviepy.editor import ImageClip

            encoded_prompt = urllib.parse.quote(prompt)
            # Use high-quality 9:16 aspect ratio (720x1280) for Reels
            image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=720&height=1280&nologo=true"

            response = requests.get(image_url)
            if response.status_code != 200:
                return f"Error: Image generation failed with status {response.status_code}"

            unique_id = str(uuid.uuid4())[:8]
            temp_img = f"temp_{unique_id}.jpg"
            with open(temp_img, "wb") as f:
                f.write(response.content)

            # Create a 5-second video clip from the image
            # This is robust and guaranteed to work as long as Pollinations image API is up
            output_video = f"reel_{unique_id}.mp4"
            clip = ImageClip(temp_img).set_duration(5)
            # Write to file - libx264 is standard for Instagram
            clip.write_videofile(output_video, fps=24, codec="libx264", audio=False)

            # Cleanup temp image
            if os.path.exists(temp_img):
                os.remove(temp_img)

            return os.path.abspath(output_video)
        except Exception as e:
            return f"Error in free video generation: {e}"

class VoiceoverGenerator:
    def __init__(self, provider="gtts"):
        self.provider = provider.lower()

    def generate_vo(self, text, output_path="vo.mp3"):
        if self.provider == "gtts":
            return self._generate_gtts(text, output_path)
        elif self.provider == "pyttsx3":
            return self._generate_pyttsx3(text, output_path)
        else:
            # Fallback to gtts
            return self._generate_gtts(text, output_path)

    def _generate_gtts(self, text, output_path):
        try:
            from gtts import gTTS
            tts = gTTS(text=text, lang='en')
            tts.save(output_path)
            return output_path
        except Exception as e:
            print(f"gTTS failed: {e}. Falling back to pyttsx3.")
            return self._generate_pyttsx3(text, output_path)

    def _generate_pyttsx3(self, text, output_path):
        try:
            import pyttsx3
            engine = pyttsx3.init()
            # On some systems, pyttsx3 save_to_file might be tricky
            # We'll try it
            engine.save_to_file(text, output_path)
            engine.runAndWait()
            return output_path
        except Exception as e:
            return f"Error in pyttsx3: {e}"

if __name__ == "__main__":
    vo = VoiceoverGenerator()
    print(f"VO generated at: {vo.generate_vo('Hello world')}")
