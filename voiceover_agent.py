import os
import asyncio
import edge_tts
import json
import re
from pydub import AudioSegment, effects
from gtts import gTTS

class VoiceoverAgent:
    def __init__(self, output_dir="exports/audio"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

        # Voice presets
        self.presets = {
            "Viral Male Fast": {
                "voice": "en-US-GuyNeural",
                "rate": "+18%",
                "pitch": "+0Hz"
            },
            "Viral Female Fast": {
                "voice": "en-US-JennyNeural",
                "rate": "+18%",
                "pitch": "+0Hz"
            },
            "Deep Male Hook": {
                "voice": "en-US-BrianNeural",
                "rate": "+10%",
                "pitch": "-2Hz"
            },
            "Clean Narrator": {
                "voice": "en-US-AriaNeural",
                "rate": "+8%",
                "pitch": "+0Hz"
            }
        }

    def extract_voiceover_text(self, script_obj):
        """
        Extracts clean voiceover text from a structured script object.
        Avoids narrating JSON keys, timestamps, or technical markers.
        """
        if isinstance(script_obj, str):
            # If it's a string, it might be raw JSON or just text
            try:
                data = json.loads(script_obj)
                return self._extract_from_dict(data)
            except:
                return self.clean_text(script_obj)
        elif isinstance(script_obj, dict):
            return self._extract_from_dict(script_obj)
        return ""

    def _extract_from_dict(self, data):
        # 1. Try voiceover_full_text key
        if "voiceover_full_text" in data and data["voiceover_full_text"]:
            return self.clean_text(data["voiceover_full_text"])

        # 2. Join scenes voiceover
        if "scenes" in data and isinstance(data["scenes"], list):
            vo_parts = []
            for scene in data["scenes"]:
                if "voiceover" in scene and scene["voiceover"]:
                    vo_parts.append(scene["voiceover"])
            if vo_parts:
                return self.clean_text(" ".join(vo_parts))

        # 3. Fallback to any text that looks like a script
        return self.clean_text(str(data))

    def clean_text(self, text):
        """
        Removes JSON, brackets, timestamps, and technical markers.
        """
        # Remove JSON-like structures
        text = re.sub(r'\{[^{}]*\}', '', text)
        # Remove markdown code blocks
        text = re.sub(r'```[a-z]*\s*|\s*```', '', text)
        # Remove timestamps like [0:00], (0-2s), 0s-3s
        text = re.sub(r'\[\d+:\d+\]|\(\d+-\d+s\)|\d+s-\d+s', '', text)
        # Remove labels like VO:, Visual:, Text:, Caption:
        text = re.sub(r'(?i)(VO|Visual|Text|Caption|Script|Title|Scene \d+):\s*', '', text)
        # Remove brackets and parentheses content that might be technical
        text = re.sub(r'\[.*?\]|\(.*?\)', '', text)
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    async def generate_voiceover(self, script_obj, preset_name="Viral Male Fast", output_filename="voiceover.mp3"):
        text = self.extract_voiceover_text(script_obj)
        if not text:
            raise ValueError("No voiceover text found in script.")

        preset = self.presets.get(preset_name, self.presets["Viral Male Fast"])
        output_path = os.path.join(self.output_dir, output_filename)

        try:
            print(f"Generating Edge-TTS voiceover: {preset_name}")
            communicate = edge_tts.Communicate(text, preset["voice"], rate=preset["rate"], pitch=preset["pitch"])
            await communicate.save(output_path)

            # Post-process
            self.post_process_audio(output_path)
            return output_path

        except Exception as e:
            print(f"Edge-TTS failed: {e}. Falling back to gTTS.")
            return self._fallback_gtts(text, output_path)

    def _fallback_gtts(self, text, output_path):
        try:
            tts = gTTS(text=text, lang='en')
            tts.save(output_path)
            self.post_process_audio(output_path)
            return output_path
        except Exception as e:
            print(f"gTTS fallback failed: {e}")
            return None

    def post_process_audio(self, file_path):
        """
        Trims silence, normalizes volume, and ensures fast pacing.
        """
        try:
            audio = AudioSegment.from_file(file_path)

            # 1. Normalize volume
            audio = effects.normalize(audio)

            # 2. Trim silence (simple thresholding)
            # Find start of audio
            start_trim = self._detect_leading_silence(audio)
            end_trim = self._detect_leading_silence(audio.reverse())

            duration = len(audio)
            audio = audio[start_trim:duration-end_trim]

            # 3. Optional: Subtle speed up if not already fast enough
            # (Edge-TTS rate already handles this, but we can do a final pass if needed)

            audio.export(file_path, format="mp3")
            print(f"Audio post-processed: {file_path}")
        except Exception as e:
            print(f"Audio post-processing error: {e}")

    def _detect_leading_silence(self, sound, silence_threshold=-50.0, chunk_size=10):
        trim_ms = 0
        assert chunk_size > 0
        while trim_ms < len(sound) and sound[trim_ms:trim_ms+chunk_size].dBFS < silence_threshold:
            trim_ms += chunk_size
        return trim_ms

if __name__ == "__main__":
    agent = VoiceoverAgent()
    test_script = {
        "voiceover_full_text": "You are not broke because you are lazy. You are broke because tiny leaks are eating your money every day."
    }
    asyncio.run(agent.generate_voiceover(test_script))
