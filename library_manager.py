import os
import json
import random

class LibraryManager:
    def __init__(self, library_dir="uploads/gameplay"):
        self.library_dir = library_dir
        self.processed_dir = os.path.join(self.library_dir, "processed")
        os.makedirs(self.processed_dir, exist_ok=True)

        self.metadata_path = os.path.join(self.library_dir, "metadata.json")
        self.processed_metadata_path = os.path.join(self.processed_dir, "metadata.json")

        self.metadata = self._load_json(self.metadata_path)
        self.processed_metadata = self._load_json(self.processed_metadata_path)

    def _load_json(self, path):
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def _save_json(self, path, data):
        with open(path, "w") as f:
            json.dump(data, f, indent=4)

    def add_original_upload(self, filename, tags=None, source_url=None, confirmed_rights=False):
        """Adds a long gameplay upload to the library metadata."""
        self.metadata[filename] = {
            "tags": tags or [],
            "source_url": source_url,
            "confirmed_rights": confirmed_rights,
            "added_at": str(os.path.getctime(os.path.join(self.library_dir, filename)))
        }
        self._save_json(self.metadata_path, self.metadata)

    def list_processed_clips(self):
        """Lists all micro-clips in the library."""
        # Refresh processed metadata
        self.processed_metadata = self._load_json(self.processed_metadata_path)
        clips = []
        for filename, data in self.processed_metadata.items():
            if filename == "processed_sources": continue
            clips.append({
                "filename": filename,
                "path": data.get("path"),
                "tags": data.get("tags", []),
                "source": data.get("source")
            })
        return clips

    def get_clips_by_tags(self, tags):
        """Returns micro-clips that match any of the provided tags."""
        all_clips = self.list_processed_clips()
        matched = []
        for clip in all_clips:
            if any(tag in clip['tags'] for tag in tags):
                matched.append(clip)
        return matched

    def auto_select_clips(self, script_text):
        """
        Automatically selects processed micro-clips based on keywords in the script.
        """
        mapping = {
            "fail": ["mistake", "broke", "lost", "failed", "wasted", "lava", "falling"],
            "parkour": ["discipline", "focus", "grind", "improve", "parkour", "jump"],
            "chest": ["secret", "hidden", "truth", "nobody tells you", "chest", "find"],
            "speedrun": ["win", "success", "level up", "speedrun", "clutch", "high energy"]
        }

        script_lower = script_text.lower()
        target_tags = set()

        for tag, keywords in mapping.items():
            if any(k in script_lower for k in keywords):
                target_tags.add(tag)

        # Always include high_energy as a default search tag if needed
        if not target_tags:
            target_tags = {"high_energy", "parkour", "neutral"}

        matched_clips = self.get_clips_by_tags(list(target_tags))

        if not matched_clips:
            # Fallback to all clips
            matched_clips = self.list_processed_clips()

        if not matched_clips:
            return []

        # Return random sample of paths
        random.shuffle(matched_clips)
        return [c['path'] for c in matched_clips]

if __name__ == "__main__":
    lm = LibraryManager()
    print("LibraryManager upgraded.")
