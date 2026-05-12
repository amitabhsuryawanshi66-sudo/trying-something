import os
import urllib.parse
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class ImageGenerator:
    def __init__(self, api_key=None, provider="free"):
        self.provider = provider
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = None
        if self.provider == "openai":
            if not self.api_key:
                # We won't raise error here, we'll handle it in generate_image or UI
                pass
            else:
                self.client = OpenAI(api_key=self.api_key)

    def generate_image(self, prompt, model="dall-e-3", size="1024x1024", quality="standard", n=1):
        """
        Generates an image. Supports 'openai' and 'free' (Pollinations.ai) providers.
        """
        if self.provider == "openai":
            return self._generate_openai(prompt, model, size, quality, n)
        else:
            return self._generate_free(prompt)

    def _generate_openai(self, prompt, model, size, quality, n):
        if not self.client:
             return "Error: OpenAI client not initialized. Check your API key."
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
            return f"An error occurred with OpenAI: {e}"

    def _generate_free(self, prompt):
        """
        Uses Pollinations.ai for free image generation. No API key required.
        """
        encoded_prompt = urllib.parse.quote(prompt)
        # Pollinations.ai returns an image directly at this URL
        image_url = f"https://pollinations.ai/p/{encoded_prompt}?width=1024&height=1024&nologo=true"
        return image_url

if __name__ == "__main__":
    # Quick test
    gen = ImageGenerator(provider="free")
    print(f"Free image URL: {gen.generate_image('A stylish AI influencer')}")
