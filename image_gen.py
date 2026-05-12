import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class ImageGenerator:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API Key not found. Please set it in the .env file.")
        self.client = OpenAI(api_key=self.api_key)

    def generate_image(self, prompt, model="dall-e-3", size="1024x1024", quality="standard", n=1):
        """
        Generates an image using OpenAI's DALL-E model.
        Returns the URL of the generated image.
        """
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
            return f"An error occurred: {e}"

if __name__ == "__main__":
    # Quick test if run directly
    try:
        gen = ImageGenerator()
        print("ImageGenerator initialized successfully.")
    except Exception as e:
        print(f"Initialization failed: {e}")
