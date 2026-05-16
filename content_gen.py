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
        if self.openai_key:
            self.openai_client = OpenAI(api_key=self.openai_key)

        self.groq_client = None
        if self.groq_key:
            try:
                from groq import Groq
                self.groq_client = Groq(api_key=self.groq_key)
            except ImportError:
                pass

    def generate_content(self, prompt, model=None, max_tokens=1500, json_mode=True):
        if self.provider == "openai" and self.openai_client:
            return self._generate_openai(prompt, model or "gpt-4o", max_tokens, json_mode)
        elif self.provider == "groq" and self.groq_client:
            return self._generate_groq(prompt, model or "llama-3.3-70b-versatile", max_tokens, json_mode)
        else:
            return self._generate_pollinations(prompt)

    def _generate_openai(self, prompt, model, max_tokens, json_mode):
        try:
            fmt = {"type": "json_object"} if json_mode else None
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a viral social media engineer. Respond with strict JSON ONLY." if json_mode else "You are a viral social media engineer."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                response_format=fmt
            )
            return response.choices[0].message.content
        except Exception as e:
            return str(e)

    def _generate_groq(self, prompt, model, max_tokens, json_mode):
        try:
            fmt = {"type": "json_object"} if json_mode else None
            chat_completion = self.groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a viral social media engineer. Respond with strict JSON ONLY." if json_mode else "You are a viral social media engineer."},
                    {"role": "user", "content": prompt}
                ],
                model=model,
                max_tokens=max_tokens,
                response_format=fmt
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            return str(e)

    def _generate_pollinations(self, prompt):
        try:
            encoded_prompt = urllib.parse.quote(prompt + " Respond with STRICT JSON ONLY.")
            url = f"https://text.pollinations.ai/{encoded_prompt}"
            response = requests.get(url)
            return response.text if response.status_code == 200 else "{}"
        except:
            return "{}"

    def generate_ideas(self, niche, count=3):
        prompt = (
            f"Generate {count} viral Instagram Reel ideas for a faceless {niche} channel. "
            "Focus on high-retention topics: money mistakes, student life, discipline, AI tools, or side hustles. "
            "BANNED style: Generic storytelling, horror (unless specified). "
            "Respond ONLY with a JSON object in this exact structure:\n"
            "{\n"
            "  \"ideas\": [\n"
            "    {\n"
            "      \"title\": \"Short punchy title\",\n"
            "      \"hook\": \"Immediate attention grabber (first 3 seconds)\",\n"
            "      \"angle\": \"The unique spin or perspective\",\n"
            "      \"trigger\": \"Emotional trigger (fear of missing out, curiosity, anger, satisfaction)\",\n"
            "      \"visuals\": \"Visual style (e.g., fast parkour, build reveal)\",\n"
            "      \"cta\": \"Strong call to action\",\n"
            "      \"monetization\": \"Potential revenue source\"\n"
            "    }\n"
            "  ]\n"
            "}"
        )
        res = self.generate_content(prompt)
        try:
            data = json.loads(self._clean_json(res))
            return data.get("ideas", [])
        except:
            return []

    def generate_script(self, idea_obj, niche):
        """
        Generates a structured viral script based on a specific idea object.
        """
        idea_context = json.dumps(idea_obj)
        prompt = (
            f"Generate a 20-35 second high-retention Instagram Reel script for niche '{niche}' based on this idea: {idea_context}.\n\n"
            "RULES:\n"
            "- NO intro like 'Hey guys' or 'Welcome back'.\n"
            "- First line MUST hit instantly with a strong hook.\n"
            "- Sentences must be short and punchy.\n"
            "- NO generic storytelling filler.\n"
            "- BANNED PHRASES: 'join me', 'welcome back', 'in today's video', 'subscribe for more', 'deep within', 'you've been warned'.\n\n"
            "Respond ONLY with a JSON object in this exact structure:\n"
            "{\n"
            "  \"title\": \"\",\n"
            "  \"duration_seconds\": 30,\n"
            "  \"hook_caption\": \"\",\n"
            "  \"voiceover_full_text\": \"The complete text to be read by the AI voice, no technical markers.\",\n"
            "  \"scenes\": [\n"
            "    {\n"
            "      \"start\": 0,\n"
            "      \"end\": 2,\n"
            "      \"voiceover\": \"The specific voiceover for this segment\",\n"
            "      \"caption\": \"UPPERCASE 3-5 words max for on-screen text\",\n"
            "      \"visual_tag\": \"parkour/build/money/etc\",\n"
            "      \"edit_effect\": \"zoom_in/shake/cut\"\n"
            "    }\n"
            "  ],\n"
            "  \"instagram_caption\": \"Viral caption with emojis\",\n"
            "  \"hashtags\": [\"#tag1\", \"#tag2\"],\n"
            "  \"cta\": \"\"\n"
            "}"
        )
        res = self.generate_content(prompt)
        try:
            return json.loads(self._clean_json(res))
        except:
            # Fallback structure
            return {
                "voiceover_full_text": "Error generating script. Please try again.",
                "scenes": []
            }

    def _clean_json(self, text):
        # Strip markdown code blocks
        text = re.sub(r'```json\s*|\s*```', '', text).strip()
        # Find the first { and last }
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1:
            return text[start:end+1]
        return text

    def generate_metadata(self, script_obj):
        caption = script_obj.get("instagram_caption", "")
        tags = " ".join(script_obj.get("hashtags", []))
        return f"{caption}\n\n{tags}"
