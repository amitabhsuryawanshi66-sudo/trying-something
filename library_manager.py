import os
import json

class LibraryManager:
    def __init__(self, library_dir="uploads/gameplay"):
        self.library_dir = library_dir
        self.metadata_path = os.path.join(self.library_dir, "metadata.json")
        os.makedirs(self.library_dir, exist_ok=True)
        self.metadata = self._load_metadata()

    def _load_metadata(self):
        if os.path.exists(self.metadata_path):
            with open(self.metadata_path, "r") as f:
                return json.load(f)
        return {}

    def _save_metadata(self):
        with open(self.metadata_path, "w") as f:
            json.dump(self.metadata, f, indent=4)

    def add_clip(self, filename, tags=None):
        """Adds a clip to the library with optional tags."""
        self.metadata[filename] = {
            "tags": tags or [],
            "added_at": str(os.path.getctime(os.path.join(self.library_dir, filename)))
        }
        self._save_metadata()

    def list_clips(self):
        """Lists all clips in the library."""
        clips = []
        for filename in os.listdir(self.library_dir):
            if filename.lower().endswith(('.mp4', '.mov', '.avi', '.mkv')) and filename != "metadata.json":
                clips.append({
                    "filename": filename,
                    "path": os.path.join(self.library_dir, filename),
                    "tags": self.metadata.get(filename, {}).get("tags", [])
                })
        return clips

    def get_clips_by_tags(self, tags):
        """Returns clips that match any of the provided tags."""
        all_clips = self.list_clips()
        matched = []
        for clip in all_clips:
            if any(tag in clip['tags'] for tag in tags):
                matched.append(clip)
        return matched

    def auto_select_clips(self, script_text):
        """Automatically selects clips based on keywords in the script."""
        keywords = {
            "parkour": ["jump", "parkour", "run", "fast"],
            "lava": ["lava", "fire", "burn", "hot"],
            "falling": ["fall", "down", "money lost", "mistake", "drop"],
            "chest": ["opening", "chest", "secret", "loot", "find"],
            "satisfying": ["satisfying", "loop", "smooth", "ai tool"]
        }

        script_lower = script_text.lower()
        selected_tags = []
        for tag, words in keywords.items():
            if any(word in script_lower for word in words):
                selected_tags.append(tag)

        if not selected_tags:
            # Default to everything if no keywords found
            return [c['path'] for c in self.list_clips()]

        matched_clips = self.get_clips_by_tags(selected_tags)
        if not matched_clips:
            # Fallback to all clips if no tag matches found
            return [c['path'] for c in self.list_clips()]

        return [c['path'] for c in matched_clips]

if __name__ == "__main__":
    lm = LibraryManager()
    print("LibraryManager module loaded.")
