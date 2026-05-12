import os
import requests
import urllib.parse
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class ContentGenerator:
    def __init__(self, api_key=None, provider="free"):
        self.provider = provider
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = None
        if self.provider == "openai":
            if self.api_key:
                self.client = OpenAI(api_key=self.api_key)

    def generate_content(self, prompt, model="gpt-4o", max_tokens=500):
        """
        Generates text content. Supports 'openai' and 'free' (Pollinations.ai text API).
        """
        if self.provider == "openai":
            return self._generate_openai(prompt, model, max_tokens)
        else:
            return self._generate_free(prompt)

    def _generate_openai(self, prompt, model, max_tokens):
        if not self.client:
            return "Error: OpenAI client not initialized. Check your API key."
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
            return f"An error occurred with OpenAI: {e}"

    def _generate_free(self, prompt):
        """
        Uses Pollinations.ai text API for free content generation.
        """
        try:
            encoded_prompt = urllib.parse.quote(prompt)
            url = f"https://text.pollinations.ai/{encoded_prompt}"
            response = requests.get(url)
            if response.status_code == 200:
                return response.text
            else:
                return f"Error from free service: {response.status_code}"
        except Exception as e:
            return f"An error occurred with free service: {e}"

    def generate_caption(self, description):
        """
        Helper to generate a social media caption based on an image description.
        """
        prompt = f"Create an engaging Instagram caption with hashtags for an image described as: {description}"
        return self.generate_content(prompt)

    def generate_reel_plan(self, topic):
        """
        Brainstorms a reel plan: Idea, Script, and Visual Prompt.
        """
        prompt = (
            f"Create a plan for a short Instagram Reel about: {topic}. "
            "Format your response exactly as follows:\n"
            "IDEA: [One sentence about the reel concept]\n"
            "SCRIPT: [A short script for the influencer to say or text to display]\n"
            "VISUAL: [A descriptive prompt for an AI video generator to create the background]"
        )
        return self.generate_content(prompt)

if __name__ == "__main__":
    # Quick test
    gen = ContentGenerator(provider="free")
    print(f"Free Reel Plan: {gen.generate_reel_plan('Healthy habits')}")
