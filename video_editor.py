import os
import random
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, ColorClip, concatenate_videoclips
from moviepy.video.fx.all import crop, resize
import moviepy.video.fx.all as vfx

class ReelEditor:
    def __init__(self, output_dir="exports/instagram_reels"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.width = 1080
        self.height = 1920

    def create_reel(self, gameplay_paths, vo_path, script_data, output_filename="final_reel.mp4"):
        """
        Assembles a finished Instagram Reel.
        """
        audio = AudioFileClip(vo_path)
        duration = audio.duration

        opened_clips = [] # Keep track to close later

        # 1. Process Gameplay Clips
        if not gameplay_paths:
            final_video = ColorClip(size=(self.width, self.height), color=(0,0,0)).set_duration(duration)
        else:
            gameplay_clips = []
            random.shuffle(gameplay_paths)
            temp_duration = 0
            idx = 0
            while temp_duration < duration:
                path = gameplay_paths[idx % len(gameplay_paths)]
                clip = VideoFileClip(path)
                opened_clips.append(clip)

                clip = self._format_to_916(clip)

                # Viral pacing: quick cuts every 1.5 - 2.5 seconds
                sub_duration = min(random.uniform(1.5, 2.5), duration - temp_duration)
                if clip.duration > sub_duration:
                    start_t = random.uniform(0, clip.duration - sub_duration)
                    clip = clip.subclip(start_t, start_t + sub_duration)

                # Zoom/Shake effects
                clip = self._apply_viral_effects(clip)

                gameplay_clips.append(clip)
                temp_duration += clip.duration
                idx += 1

            final_video = concatenate_videoclips(gameplay_clips).set_duration(duration)

        final_video = final_video.set_audio(audio)

        # 2. Add Captions
        caption_clips = []
        try:
            for segment in script_data:
                start = segment.get('start', 0)
                end = segment.get('end', start + 2)
                text = segment.get('text', '')

                if text:
                    # Viral style: 3 words per line, large, bold
                    words = text.split()
                    chunk_size = 3
                    for i in range(0, len(words), chunk_size):
                        chunk = " ".join(words[i:i+chunk_size]).upper()
                        chunk_duration = (end - start) / (len(words) / chunk_size)
                        chunk_start = start + (i / chunk_size) * chunk_duration

                        # Use huge font for the first 3 seconds (The Hook)
                        is_hook = chunk_start < 3
                        fsize = 100 if is_hook else 75

                        txt_clip = TextClip(
                            chunk,
                            fontsize=fsize,
                            color='white',
                            font='Arial-Bold',
                            stroke_color='black',
                            stroke_width=3,
                            method='caption',
                            size=(self.width * 0.9, None)
                        ).set_start(chunk_start).set_duration(chunk_duration).set_position(('center', 1000))

                        # Scale/Pop animation
                        txt_clip = txt_clip.fx(vfx.resize, lambda t: 1 + 0.2 * (t / chunk_duration) if t < 0.1 else 1)

                        caption_clips.append(txt_clip)
        except Exception as e:
            print(f"Caption error: {e}")

        # Combine
        result = CompositeVideoClip([final_video] + caption_clips, size=(self.width, self.height))

        output_path = os.path.join(self.output_dir, output_filename)
        result.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")

        # Cleanup
        result.close()
        final_video.close()
        audio.close()
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
        # Randomly apply zoom or slight shake
        if random.random() > 0.5:
            return clip.fx(vfx.resize, lambda t: 1 + 0.08 * t)
        return clip
