import os
import json
import uuid
from PIL import Image

# Fix Pillow/MoviePy compatibility issue
if not hasattr(Image, "ANTIALIAS"):
    Image.ANTIALIAS = Image.Resampling.LANCZOS

from moviepy.editor import VideoFileClip

class GameplayProcessor:
    def __init__(self, processed_dir="uploads/gameplay/processed"):
        self.processed_dir = processed_dir
        os.makedirs(self.processed_dir, exist_ok=True)
        self.metadata_path = os.path.join(self.processed_dir, "metadata.json")
        self.metadata = self._load_metadata()

    def _load_metadata(self):
        if os.path.exists(self.metadata_path):
            with open(self.metadata_path, "r") as f:
                return json.load(f)
        return {}

    def _save_metadata(self):
        with open(self.metadata_path, "w") as f:
            json.dump(self.metadata, f, indent=4)

    def process_long_video(self, video_path, default_tags=None, split_length=2.0):
        """
        Splits a long video into micro-clips and saves them.
        """
        if default_tags is None:
            default_tags = ["neutral"]

        video_filename = os.path.basename(video_path)

        # Avoid reprocessing
        if video_filename in self.metadata.get("processed_sources", []):
            print(f"Source {video_filename} already processed. Skipping.")
            return []

        print(f"Processing long video: {video_path}")
        new_clips = []

        try:
            with VideoFileClip(video_path) as video:
                duration = video.duration
                current_t = 0

                while current_t + split_length <= duration:
                    clip_id = str(uuid.uuid4())[:8]
                    clip_filename = f"micro_{clip_id}.mp4"
                    clip_path = os.path.join(self.processed_dir, clip_filename)

                    # Extract subclip
                    subclip = video.subclip(current_t, current_t + split_length)
                    subclip.write_videofile(clip_path, codec="libx264", audio=False, fps=24, logger=None)

                    self.metadata[clip_filename] = {
                        "source": video_filename,
                        "tags": default_tags,
                        "duration": split_length,
                        "path": clip_path
                    }

                    new_clips.append(clip_path)
                    current_t += split_length

            # Mark source as processed
            if "processed_sources" not in self.metadata:
                self.metadata["processed_sources"] = []
            self.metadata["processed_sources"].append(video_filename)

            self._save_metadata()
            print(f"Successfully created {len(new_clips)} micro-clips.")

        except Exception as e:
            print(f"Error processing {video_path}: {e}")

        return new_clips

if __name__ == "__main__":
    gp = GameplayProcessor()
    print("GameplayProcessor module loaded.")
