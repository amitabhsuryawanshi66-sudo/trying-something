import os
import random
import datetime
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# Fix Pillow/MoviePy compatibility
if not hasattr(Image, "ANTIALIAS"):
    Image.ANTIALIAS = Image.Resampling.LANCZOS

from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, ColorClip, concatenate_videoclips
import moviepy.video.fx.all as vfx
from moviepy.video.fx.all import crop, resize

class ReelEditor:
    def __init__(self, output_dir="exports/instagram_reels"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.width = 1080
        self.height = 1920

    def create_reel(self, gameplay_paths, vo_path, script_data, output_filename="final_reel.mp4", music_path=None):
        """
        Assembles a viral Instagram Reel using structured script data.
        """
        audio_vo = AudioFileClip(vo_path)
        duration = audio_vo.duration

        # Audio setup
        final_audio = audio_vo
        if music_path and os.path.exists(music_path):
            try:
                music = AudioFileClip(music_path).volumex(0.15)
                if music.duration < duration:
                    music = music.loop(duration=duration)
                else:
                    music = music.subclip(0, duration)
                from moviepy.audio.AudioClip import CompositeAudioClip
                final_audio = CompositeAudioClip([audio_vo, music])
            except:
                pass

        opened_clips = []

        # 1. Process Gameplay Clips based on scenes
        gameplay_clips = []
        current_t = 0

        # Fallback if no specific scenes
        if not script_data:
            script_data = [{"start": 0, "end": duration, "caption": "", "visual_tag": "parkour"}]

        for scene in script_data:
            scene_duration = scene.get('end', current_t + 2) - scene.get('start', current_t)
            if scene_duration <= 0: continue

            # Select clip matching tag or random
            tag = scene.get('visual_tag', 'parkour')
            possible_clips = [p for p in gameplay_paths if tag in p.lower()]
            clip_path = random.choice(possible_clips if possible_clips else gameplay_paths)

            try:
                clip = VideoFileClip(clip_path)
                # Random subclip if source is longer than scene
                if clip.duration > scene_duration:
                    start_cut = random.uniform(0, clip.duration - scene_duration)
                    clip = clip.subclip(start_cut, start_cut + scene_duration)
                else:
                    clip = clip.set_duration(scene_duration)

                opened_clips.append(clip)

                # Viral formatting & effects
                clip = self._format_to_916(clip)
                clip = self._apply_viral_effects(clip, scene.get('edit_effect', 'zoom_in'))

                gameplay_clips.append(clip)
                current_t += scene_duration
            except Exception as e:
                print(f"Error processing clip {clip_path}: {e}")

        if not gameplay_clips:
            final_video = ColorClip(size=(self.width, self.height), color=(0,0,0)).set_duration(duration)
        else:
            final_video = concatenate_videoclips(gameplay_clips).set_duration(duration)

        final_video = final_video.set_audio(final_audio)

        # 2. Add Viral Captions
        caption_clips = []
        try:
            for scene in script_data:
                text = scene.get('caption', '').upper()
                if text:
                    start = scene.get('start', 0)
                    end = scene.get('end', start + 2)
                    caption_clips.extend(self._create_viral_captions(text, start, end))
        except Exception as e:
            print(f"Caption engine failed: {e}")

        # Combine
        result = CompositeVideoClip([final_video] + caption_clips, size=(self.width, self.height))

        output_path = os.path.join(self.output_dir, output_filename)
        # Use fast preset for quick rendering
        result.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac", temp_audiofile="temp-audio.m4a", remove_temp=True, preset="ultrafast")

        # Cleanup
        result.close()
        for c in opened_clips: c.close()

        return output_path

    def _format_to_916(self, clip):
        target_ratio = 1080 / 1920
        clip_ratio = clip.w / clip.h
        if clip_ratio > target_ratio:
            new_w = clip.h * target_ratio
            clip = crop(clip, x_center=clip.w/2, width=new_w)
        else:
            new_h = clip.w / target_ratio
            clip = crop(clip, y_center=clip.h/2, height=new_h)
        return clip.resize(width=1080)

    def _apply_viral_effects(self, clip, effect):
        if effect == "zoom_in":
            return clip.fx(vfx.resize, lambda t: 1 + 0.1 * t)
        elif effect == "shake":
            # Simple shake simulation via random cropping
            return clip.fx(vfx.crop, x1=5, y1=5, x2=1075, y2=1915).resize(width=1080)
        return clip

    def _create_viral_captions(self, text, start, end):
        clips = []
        try:
            txt_clip = TextClip(
                text,
                fontsize=90,
                color='yellow' if start < 3 else 'white',
                font='Arial-Bold',
                stroke_color='black',
                stroke_width=3,
                method='caption',
                size=(self.width * 0.8, None)
            ).set_start(start).set_duration(end - start).set_position(('center', 1200))

            # Pop effect
            txt_clip = txt_clip.fx(vfx.resize, lambda t: 1.1 if t < 0.1 else 1.0)
            clips.append(txt_clip)
        except:
            pass
        return clips
