import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class ContentGenerator:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API Key not found. Please set it in the .env file.")
        self.client = OpenAI(api_key=self.api_key)

    def generate_content(self, prompt, model="gpt-4o", max_tokens=500):
        """
        Generates text content using OpenAI's GPT model.
        """
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a creative social media manager for an AI influencer."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"An error occurred: {e}"

    def generate_caption(self, description):
        """
        Helper to generate a social media caption based on an image description.
        """
        prompt = f"Create an engaging Instagram caption with hashtags for an image described as: {description}"
        return self.generate_content(prompt)

if __name__ == "__main__":
    # Quick test if run directly
    try:
        gen = ContentGenerator()
        print("ContentGenerator initialized successfully.")
    except Exception as e:
        print(f"Initialization failed: {e}")
