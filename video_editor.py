import os
import random
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, ColorClip, concatenate_videoclips
from moviepy.video.fx.all import crop, resize
import moviepy.video.fx.all as vfx

class ReelEditor:
    def __init__(self, output_dir="exports/final_reels"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.width = 1080
        self.height = 1920

    def create_reel(self, gameplay_paths, vo_path, script_data, output_filename="final_video.mp4"):
        """
        Assembles a finished reel.
        script_data: list of dicts with {'start': 0, 'end': 2, 'text': '...', 'vo': '...'}
        """
        audio = AudioFileClip(vo_path)
        duration = audio.duration

        clips = []
        current_time = 0

        # 1. Process Gameplay Clips
        if not gameplay_paths:
            # Fallback to a color clip if no gameplay
            gameplay_clips = [ColorClip(size=(self.width, self.height), color=(0,0,0)).set_duration(duration)]
        else:
            gameplay_clips = []
            random.shuffle(gameplay_paths)
            temp_duration = 0
            idx = 0
            while temp_duration < duration:
                path = gameplay_paths[idx % len(gameplay_paths)]
                clip = VideoFileClip(path)

                # Resize and crop to 9:16
                clip = self._format_to_916(clip)

                # Pacing: cut every 2-3 seconds or based on script
                sub_duration = min(3, duration - temp_duration)
                if clip.duration > sub_duration:
                    start_t = random.uniform(0, clip.duration - sub_duration)
                    clip = clip.subclip(start_t, start_t + sub_duration)

                # Add zoom effect occasionally
                if random.random() > 0.5:
                    clip = self._apply_zoom(clip)

                gameplay_clips.append(clip)
                temp_duration += clip.duration
                idx += 1

        final_video = concatenate_videoclips(gameplay_clips).set_duration(duration)
        final_video = final_video.set_audio(audio)

        # 2. Add Captions (Fallback to basic subtitles if ImageMagick fails)
        caption_clips = []
        try:
            for segment in script_data:
                start = segment.get('start', 0)
                end = segment.get('end', start + 2)
                text = segment.get('text', '')

                if text:
                    # Split text into chunks of 3-5 words
                    words = text.split()
                    chunk_size = 4
                    for i in range(0, len(words), chunk_size):
                        chunk = " ".join(words[i:i+chunk_size]).upper()
                        chunk_duration = (end - start) / (len(words) / chunk_size)
                        chunk_start = start + (i / chunk_size) * chunk_duration

                        txt_clip = TextClip(
                            chunk,
                            fontsize=70,
                            color='yellow',
                            font='Arial-Bold',
                            stroke_color='black',
                            stroke_width=2,
                            method='caption',
                            size=(self.width * 0.8, None)
                        ).set_start(chunk_start).set_duration(chunk_duration).set_position(('center', 1400))

                        # Pop animation
                        txt_clip = txt_clip.fx(vfx.resize, lambda t: 1 + 0.1 * (t / chunk_duration) if t < 0.1 else 1)

                        caption_clips.append(txt_clip)
        except Exception as e:
            print(f"Caption generation failed (likely ImageMagick): {e}. Proceeding without captions.")

        # Combine
        result = CompositeVideoClip([final_video] + caption_clips, size=(self.width, self.height))

        output_path = os.path.join(self.output_dir, output_filename)
        result.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")

        return output_path

    def _format_to_916(self, clip):
        """Resizes and crops a clip to 1080x1920."""
        target_ratio = 1080 / 1920
        clip_ratio = clip.w / clip.h

        if clip_ratio > target_ratio:
            # Clip is wider than target
            new_w = clip.h * target_ratio
            clip = crop(clip, x_center=clip.w/2, width=new_w)
        else:
            # Clip is taller than target
            new_h = clip.w / target_ratio
            clip = crop(clip, y_center=clip.h/2, height=new_h)

        return clip.resize(width=1080)

    def _apply_zoom(self, clip):
        """Applies a subtle zoom-in effect."""
        return clip.fx(vfx.resize, lambda t: 1 + 0.05 * t)

if __name__ == "__main__":
    # Test stub
    print("ReelEditor module loaded.")
