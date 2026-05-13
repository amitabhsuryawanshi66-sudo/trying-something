import os
import urllib.parse
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class ImageGenerator:
    def __init__(self, api_key=None, provider="free"):
        self.provider = provider.lower()
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = None
        if self.provider == "openai" and self.api_key:
            self.client = OpenAI(api_key=self.api_key)

    def generate_image(self, prompt, model="dall-e-3", size="1024x1024", quality="standard", n=1):
        """
        Generates an image. Supports 'openai' and 'free' (Pollinations.ai) providers.
        """
        if self.provider == "openai" and self.client:
            return self._generate_openai(prompt, model, size, quality, n)
        else:
            return self._generate_pollinations(prompt)

    def _generate_openai(self, prompt, model, size, quality, n):
        try:
            response = self.client.images.generate(
                model=model,
                prompt=prompt,
                size=size,
                quality=quality,
                n=n,
            )
            return response.data[0].url
        except Exception as e:
            print(f"OpenAI Image Error: {e}. Falling back to Pollinations.")
            return self._generate_pollinations(prompt)

    def _generate_pollinations(self, prompt):
        """
        Uses Pollinations.ai for free image generation. No API key required.
        """
        encoded_prompt = urllib.parse.quote(prompt)
        # Direct image link for rendering
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true"
        return image_url

if __name__ == "__main__":
    gen = ImageGenerator(provider="free")
    print(f"Free image URL: {gen.generate_image('A stylish AI influencer')}")
