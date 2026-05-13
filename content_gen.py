import os
import requests
import urllib.parse
import re
import json
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

    def generate_content(self, prompt, model=None, max_tokens=1000):
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
                    {"role": "system", "content": "You are a creative social media manager for an AI influencer and faceless content creator."},
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
                    {"role": "system", "content": "You are a creative social media manager for an AI influencer and faceless content creator."},
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
        prompt_lower = prompt.lower()
        if "ideas" in prompt_lower:
            if "minecraft" in prompt_lower:
                return "TITLE: Minecraft Parkour Brainrot\nHOOK: Why are you still watching this?\nANGLE: Fast-paced parkour with satisfying sounds.\nTRIGGER: Visual satisfaction\nCTA: Follow for more satisfying clips.\nMONETIZATION: Selling custom parkour maps.\nVISUALS: High-speed Minecraft parkour in the End."
            elif "self-improvement" in prompt_lower or "discipline" in prompt_lower:
                return "TITLE: The 5 AM Rule\nHOOK: 99% of people fail this.\nANGLE: Discipline over motivation.\nTRIGGER: FOMO (Fear Of Missing Out) on success.\nCTA: Type 'READY' if you're starting today.\nMONETIZATION: Coaching program.\nVISUALS: Dark cinematic shots of someone working out early."
            elif "money" in prompt_lower or "side hustle" in prompt_lower:
                return "TITLE: Student Side Hustle\nHOOK: Make $100/day using only your phone.\nANGLE: Easy entry for students.\nTRIGGER: Financial freedom\nCTA: Check the link in bio for the full tutorial.\nMONETIZATION: Affiliate marketing.\nVISUALS: Split screen with phone screen recording and aesthetic office."

        if "script" in prompt_lower:
            return "0:00 - VO: You've been lied to about success. TEXT: THE SUCCESS LIE. VISUAL: Cinematic slow motion of rain.\n0:05 - VO: It's not about talent, it's about discipline. TEXT: DISCIPLINE > TALENT. VISUAL: Fast cuts of intense training.\n0:15 - VO: Start today, not tomorrow. TEXT: START NOW. VISUAL: Motivational quote on dark background."

        return "Enjoying the digital frontier! #AI #TechLife"

    def generate_ideas(self, niche, count=3):
        prompt = (
            f"Generate {count} viral content ideas for a faceless {niche} channel. "
            "For each idea, provide exactly these fields:\n"
            "TITLE: [Catchy title]\n"
            "HOOK: [First 3-second hook]\n"
            "ANGLE: [Unique video perspective]\n"
            "TRIGGER: [Emotional trigger like FOMO, curiosity, anger, or joy]\n"
            "CTA: [Call to action]\n"
            "MONETIZATION: [How to make money from this video]\n"
            "VISUALS: [Suggested visuals for Minecraft parkour or aesthetic b-roll]\n"
            "---"
        )
        content = self.generate_content(prompt)
        ideas_raw = content.split("---")
        ideas = []
        for raw in ideas_raw:
            if raw.strip():
                idea = {}
                for line in raw.strip().split('\n'):
                    if ':' in line:
                        key, val = line.split(':', 1)
                        idea[key.strip().lower()] = val.strip()
                if idea:
                    ideas.append(idea)
        return ideas

    def generate_script(self, idea_title, niche):
        prompt = (
            f"Write a 15-45 second short-form video script for the idea: '{idea_title}' in the {niche} niche. "
            "Format exactly like this for each segment:\n"
            "TIMESTAMP - VO: [Voiceover text] TEXT: [On-screen text] VISUAL: [Visual direction]\n"
            "Keep it fast-paced and high-retention."
        )
        return self.generate_content(prompt)

    def generate_metadata(self, idea_title, niche):
        prompt = (
            f"Generate captions and hashtags for a video titled '{idea_title}' in the {niche} niche.\n"
            "TikTok Caption: [Text]\n"
            "YouTube Shorts Title: [Text]\n"
            "Instagram Reel Caption: [Text]\n"
            "Hashtags: [#tag1 #tag2 ...]\n"
            "Pinned Comment: [Text]\n"
            "CTA: [Text]"
        )
        return self.generate_content(prompt)

    def generate_visual_prompts(self, visual_description):
        prompt = (
            f"Convert this visual description into 3 detailed AI image/video generation prompts (Minecraft-inspired, voxel, or cinematic b-roll, no copyrighted names): '{visual_description}'"
        )
        return self.generate_content(prompt)

    def generate_reel_plan(self, topic):
        # Keeping for backward compatibility but using the new structure
        ideas = self.generate_ideas(topic, count=1)
        if ideas:
            idea = ideas[0]
            script = self.generate_script(idea.get('title', topic), topic)
            return {
                "idea": idea.get('title', topic),
                "script": script,
                "visual": idea.get('visuals', topic)
            }
        return {"idea": topic, "script": "N/A", "visual": topic}

if __name__ == "__main__":
    gen = ContentGenerator(provider="pollinations")
    print(f"Test Ideas: {gen.generate_ideas('Minecraft brainrot', count=2)}")
