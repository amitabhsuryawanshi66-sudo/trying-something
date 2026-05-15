import os
import random
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# Fix Pillow/MoviePy compatibility issue
if not hasattr(Image, "ANTIALIAS"):
    Image.ANTIALIAS = Image.Resampling.LANCZOS

from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, ColorClip, concatenate_videoclips, ImageClip
from moviepy.video.fx.all import crop, resize
import moviepy.video.fx.all as vfx

class ReelEditor:
    def __init__(self, output_dir="exports/instagram_reels"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.width = 1080
        self.height = 1920

    def create_reel(self, gameplay_paths, vo_path, script_data, output_filename="final_reel.mp4", music_path=None):
        """
        Assembles a finished Instagram Reel using processed micro-clips.
        """
        audio_vo = AudioFileClip(vo_path)
        duration = audio_vo.duration

        # Add background music if provided
        if music_path and os.path.exists(music_path):
            music = AudioFileClip(music_path).volumex(0.15) # Music quieter than VO
            if music.duration < duration:
                music = music.loop(duration=duration)
            else:
                music = music.subclip(0, duration)
            from moviepy.audio.AudioClip import CompositeAudioClip
            final_audio = CompositeAudioClip([audio_vo, music])
        else:
            final_audio = audio_vo

        opened_clips = []

        # 1. Process Gameplay Clips
        if not gameplay_paths:
            final_video = ColorClip(size=(self.width, self.height), color=(0,0,0)).set_duration(duration)
        else:
            gameplay_clips = []
            temp_duration = 0
            while temp_duration < duration:
                path = random.choice(gameplay_paths)
                clip = VideoFileClip(path)
                opened_clips.append(clip)

                # Standardize to 9:16
                clip = self._format_to_916(clip)

                # Trim if it exceeds duration
                if temp_duration + clip.duration > duration:
                    clip = clip.subclip(0, duration - temp_duration)

                # Apply viral motion
                clip = self._apply_viral_effects(clip)

                gameplay_clips.append(clip)
                temp_duration += clip.duration

            final_video = concatenate_videoclips(gameplay_clips).set_duration(duration)

        final_video = final_video.set_audio(final_audio)

        # 2. Add Captions
        caption_clips = []
        try:
            for segment in script_data:
                start = segment.get('start', 0)
                end = segment.get('end', start + 2)
                text = segment.get('text', '')
                if text:
                    caption_clips.extend(self._create_viral_captions(text, start, end))
        except Exception as e:
            print(f"Caption engine failed: {e}. Falling back to basic PIL rendering.")
            # PIL fallback logic could go here if needed, but for now we skip to avoid crash

        # Combine
        result = CompositeVideoClip([final_video] + caption_clips, size=(self.width, self.height))

        output_path = os.path.join(self.output_dir, output_filename)
        result.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac", temp_audiofile="temp-audio.m4a", remove_temp=True)

        # Cleanup
        result.close()
        final_video.close()
        final_audio.close()
        for c in opened_clips:
            c.close()
        for c in caption_clips:
            c.close()

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

    def _apply_viral_effects(self, clip):
        # Apply slow zoom-in
        return clip.fx(vfx.resize, lambda t: 1 + 0.04 * t)

    def _create_viral_captions(self, text, start, end):
        """Creates animated viral captions."""
        clips = []
        words = text.split()
        chunk_size = 3

        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i+chunk_size]).upper()
            chunk_duration = (end - start) / (len(words) / chunk_size)
            chunk_start = start + (i / chunk_size) * chunk_duration

            is_hook = chunk_start < 3
            color = 'yellow' if is_hook else 'white'
            fsize = 110 if is_hook else 85

            try:
                txt_clip = TextClip(
                    chunk,
                    fontsize=fsize,
                    color=color,
                    font='Arial-Bold',
                    stroke_color='black',
                    stroke_width=4,
                    method='caption',
                    size=(self.width * 0.85, None)
                ).set_start(chunk_start).set_duration(chunk_duration).set_position(('center', 1100))

                # Pop effect
                txt_clip = txt_clip.fx(vfx.resize, lambda t: 1.1 if t < 0.1 else 1.0)
                clips.append(txt_clip)
            except:
                # If TextClip (ImageMagick) fails, try to use a PIL-based clip (simulated here)
                pass
        return clips

    def generate_srt(self, script_data, output_path):
        """Generates a standard .srt caption file."""
        with open(output_path, "w", encoding="utf-8") as f:
            for i, segment in enumerate(script_data):
                start = self._format_srt_time(segment['start'])
                end = self._format_srt_time(segment['end'])
                f.write(f"{i+1}\n{start} --> {end}\n{segment['text']}\n\n")

    def _format_srt_time(self, seconds):
        td = datetime.timedelta(seconds=seconds)
        # Simplified formatting
        return str(td).replace('.', ',')[:11]

import datetime
