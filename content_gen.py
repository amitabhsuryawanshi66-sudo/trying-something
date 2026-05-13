import os
import requests
import urllib.parse
import re
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class ContentGenerator:
    def __init__(self, api_key=None, provider="pollinations", groq_key=None):
        self.provider = provider.lower()
        self.openai_key = api_key or os.getenv("OPENAI_API_KEY")
        self.groq_key = groq_key or os.getenv("GROQ_API_KEY")

        self.openai_client = None
        if self.provider == "openai" and self.openai_key:
            self.openai_client = OpenAI(api_key=self.openai_key)

        self.groq_client = None
        if self.provider == "groq" and self.groq_key:
            try:
                from groq import Groq
                self.groq_client = Groq(api_key=self.groq_key)
            except ImportError:
                print("Groq library not found. Please install with 'pip install groq'.")

    def generate_content(self, prompt, model=None, max_tokens=500):
        """
        Generates text content. Supports 'openai', 'groq', and 'pollinations'.
        """
        if self.provider == "openai":
            return self._generate_openai(prompt, model or "gpt-4o", max_tokens)
        elif self.provider == "groq":
            return self._generate_groq(prompt, model or "llama3-8b-8192", max_tokens)
        elif self.provider == "pollinations":
            return self._generate_pollinations(prompt)
        else:
            return self._generate_template(prompt)

    def _generate_openai(self, prompt, model, max_tokens):
        if not self.openai_client:
            return "Error: OpenAI client not initialized. Check your API key."
        try:
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a creative social media manager for an AI influencer."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"OpenAI Error: {e}"

    def _generate_groq(self, prompt, model, max_tokens):
        if not self.groq_client:
            return "Error: Groq client not initialized. Check your API key."
        try:
            chat_completion = self.groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a creative social media manager for an AI influencer."},
                    {"role": "user", "content": prompt}
                ],
                model=model,
                max_tokens=max_tokens
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            return f"Groq Error: {e}"

    def _generate_pollinations(self, prompt):
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
                return f"Pollinations Error: {response.status_code}"
        except Exception as e:
            return f"Pollinations Connection Error: {e}"

    def _generate_template(self, prompt):
        """
        Fallback template generator if no AI is available.
        """
        if "Reel" in prompt or "plan" in prompt:
            return (
                "IDEA: A day in the life of an AI creator.\n"
                "SCRIPT: Behind every pixel is a line of code. Welcome to my world.\n"
                "VISUAL: A clean, futuristic workspace with holographic screens."
            )
        return "Enjoying the digital frontier! #AI #TechLife"

    def parse_reel_plan(self, text):
        """
        Robustly parses the plan using regex.
        """
        plan = {
            "idea": "Unique AI content creation.",
            "script": "Check out this amazing AI-generated content!",
            "visual": "A futuristic digital landscape."
        }

        idea_match = re.search(r"IDEA:\s*(.*)", text, re.IGNORECASE)
        script_match = re.search(r"SCRIPT:\s*(.*)", text, re.IGNORECASE)
        visual_match = re.search(r"VISUAL:\s*(.*)", text, re.IGNORECASE)

        if idea_match: plan["idea"] = idea_match.group(1).strip()
        if script_match: plan["script"] = script_match.group(1).strip()
        if visual_match: plan["visual"] = visual_match.group(1).strip()

        return plan

    def generate_reel_plan(self, topic):
        """
        Brainstorms a reel plan: Idea, Script, and Visual Prompt.
        """
        prompt = (
            f"Create a plan for a short Instagram Reel about: {topic}. "
            "Respond ONLY with this format:\n"
            "IDEA: [One sentence idea]\n"
            "SCRIPT: [Short script or overlay text]\n"
            "VISUAL: [Descriptive prompt for an image generator]"
        )
        content = self.generate_content(prompt)
        return self.parse_reel_plan(content)

if __name__ == "__main__":
    gen = ContentGenerator(provider="pollinations")
    print(f"Test Plan: {gen.generate_reel_plan('Morning routine')}")
