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

        self.last_raw_response = ""
        self.last_parse_errors = []

        self.openai_client = None
        if self.provider == "openai" and self.openai_key:
            self.openai_client = OpenAI(api_key=self.openai_key)

        self.groq_client = None
        if self.provider == "groq" and self.groq_key:
            try:
                from groq import Groq
                # Using a more reliable model for JSON
                self.groq_model = "llama-3.3-70b-versatile"
                self.groq_client = Groq(api_key=self.groq_key)
            except ImportError:
                print("Groq library not found. Please install with 'pip install groq'.")

    def generate_content(self, prompt, model=None, max_tokens=1500):
        """
        Generates text content. Supports 'openai', 'groq', and 'pollinations'.
        """
        if self.provider == "openai":
            res = self._generate_openai(prompt, model or "gpt-4o", max_tokens)
        elif self.provider == "groq":
            res = self._generate_groq(prompt, model or getattr(self, 'groq_model', 'llama3-8b-8192'), max_tokens)
        elif self.provider == "pollinations":
            res = self._generate_pollinations(prompt)
        else:
            res = self._generate_template(prompt)

        self.last_raw_response = res
        return res

    def _generate_openai(self, prompt, model, max_tokens):
        if not self.openai_client:
            return "Error: OpenAI client not initialized."
        try:
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a creative social media manager. Respond with STRICT JSON only."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                response_format={ "type": "json_object" }
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"OpenAI Error: {e}"

    def _generate_groq(self, prompt, model, max_tokens):
        if not self.groq_client:
            return "Error: Groq client not initialized."
        try:
            chat_completion = self.groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a creative social media manager. Respond with STRICT JSON ONLY. No conversational text."},
                    {"role": "user", "content": prompt}
                ],
                model=model,
                max_tokens=max_tokens,
                response_format={ "type": "json_object" }
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            # Fallback for models that don't support response_format
            try:
                chat_completion = self.groq_client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": "You are a creative social media manager. Respond with STRICT JSON ONLY. No conversational text."},
                        {"role": "user", "content": prompt}
                    ],
                    model=model,
                    max_tokens=max_tokens
                )
                return chat_completion.choices[0].message.content
            except Exception as e2:
                return f"Groq Error: {e2}"

    def _generate_pollinations(self, prompt):
        try:
            encoded_prompt = urllib.parse.quote(prompt + " Respond with STRICT JSON ONLY.")
            url = f"https://text.pollinations.ai/{encoded_prompt}"
            response = requests.get(url)
            return response.text if response.status_code == 200 else f"Pollinations Error: {response.status_code}"
        except Exception as e:
            return f"Pollinations Error: {e}"

    def _generate_template(self, prompt):
        if "ideas" in prompt.lower():
            return json.dumps({
                "ideas": [
                    {
                        "title": "Minecraft Brainrot Survival",
                        "hook": "I survived 100 days of brainrot Minecraft...",
                        "angle": "First-person parkour while talking about Gen Alpha memes.",
                        "trigger": "Curiosity/Confusion",
                        "visuals": "High-speed Minecraft parkour with colorful shaders.",
                        "cta": "Follow for more brainrot!",
                        "monetization": "AdSense and merch."
                    }
                ]
            })
        return "Fallback content."

    def generate_ideas(self, niche, count=3):
        self.last_parse_errors = []
        prompt = (
            f"Generate {count} viral Instagram Reel ideas for a faceless {niche} channel. "
            "Respond ONLY with a JSON object in this exact structure:\n"
            "{\n"
            "  \"ideas\": [\n"
            "    {\n"
            "      \"title\": \"\",\n"
            "      \"hook\": \"\",\n"
            "      \"angle\": \"\",\n"
            "      \"trigger\": \"\",\n"
            "      \"visuals\": \"\",\n"
            "      \"cta\": \"\",\n"
            "      \"monetization\": \"\"\n"
            "    }\n"
            "  ]\n"
            "}"
        )
        raw_res = self.generate_content(prompt)
        return self._parse_ideas(raw_res, niche)

    def _parse_ideas(self, raw_text, niche):
        # 1. Try direct JSON load
        try:
            # Strip markdown code blocks if present
            clean_text = re.sub(r'```json\s*|\s*```', '', raw_text).strip()
            data = json.loads(clean_text)
            if "ideas" in data and isinstance(data["ideas"], list):
                return [self._validate_idea(i) for i in data["ideas"]]
        except Exception as e:
            self.last_parse_errors.append(f"JSON Parse Failed: {e}")

        # 2. Try regex extraction if JSON fails
        self.last_parse_errors.append("Attempting Regex Extraction...")
        ideas = []
        # Find everything between { }
        json_blocks = re.findall(r'\{[^{}]*\}', raw_text)
        for block in json_blocks:
            idea = {}
            for field in ["title", "hook", "angle", "trigger", "visuals", "cta", "monetization"]:
                match = re.search(f'"{field}"\\s*:\\s*"([^"]*)"', block, re.IGNORECASE)
                if match:
                    idea[field] = match.group(1)
            if idea:
                ideas.append(self._validate_idea(idea))

        # 3. Fallback to template if nothing found
        if not ideas:
            self.last_parse_errors.append("Everything failed. Returning template.")
            template_res = self._generate_template(f"ideas for {niche}")
            return json.loads(template_res)["ideas"]

        return ideas

    def _validate_idea(self, idea):
        fields = ["title", "hook", "angle", "trigger", "visuals", "cta", "monetization"]
        validated = {}
        for f in fields:
            val = idea.get(f, "").strip()
            if not val or val.lower() == "none":
                val = f"Creative {f.replace('_', ' ')}"
            validated[f] = val
        return validated

    def generate_script(self, idea_title, niche):
        prompt = (
            f"Write a 20-35 second Instagram Reel script for: '{idea_title}' in {niche}. "
            "Format: TIMESTAMP - VO: [Text] TEXT: [On-screen] VISUAL: [Direction]. "
            "Include a HUGE HOOK in the first 3 seconds."
        )
        return self.generate_content(prompt)

    def generate_metadata(self, idea_title, niche):
        prompt = (
            f"Generate Instagram-specific metadata for a Reel titled '{idea_title}' in the {niche} niche.\n"
            "Instagram Caption: [Text]\n"
            "Hashtags: [#tag1 #tag2 ...]\n"
            "Pinned Comment: [Text]\n"
            "CTA: [Text]"
        )
        return self.generate_content(prompt)

    def extract_keywords(self, script_text):
        """Extracts search terms for footage search."""
        prompt = (
            f"Extract 5 search terms (single words or short phrases) to find background footage for this script: {script_text}. "
            "Focus on legal gaming/gameplay terms like 'parkour', 'minecraft', 'high energy', 'failure', 'success'. "
            "Respond with a comma-separated list only."
        )
        res = self.generate_content(prompt)
        return [k.strip() for k in res.split(',')]

    def generate_visual_prompts(self, visual_description):
        prompt = f"Create 3 AI image prompts for: {visual_description}"
        return self.generate_content(prompt)

    def generate_reel_plan(self, topic):
        ideas = self.generate_ideas(topic, count=1)
        idea = ideas[0]
        script = self.generate_script(idea['title'], topic)
        return {"idea": idea['title'], "script": script, "visual": idea['visuals']}
