import os
from instagrapi import Client

class SocialManager:
    def __init__(self):
        pass

    def post_to_instagram(self, image_url, caption):
        print(f"Post to Instagram: {image_url}")
        print(f"Caption: {caption}")
        return "Success: Posted to Instagram (Simulation)"

    def post_to_twitter(self, image_url, caption):
        print(f"Post to Twitter: {image_url}")
        print(f"Caption: {caption}")
        return "Success: Posted to Twitter (Simulation)"

class InstagramManager:
    def __init__(self, username=None, password=None):
        self.cl = Client()
        self.username = username or os.getenv("INSTAGRAM_USERNAME")
        self.password = password or os.getenv("INSTAGRAM_PASSWORD")
        self.logged_in = False

    def login(self):
        if not self.username or not self.password:
            return False, "Error: Instagram credentials not found."
        try:
            self.cl.login(self.username, self.password)
            self.logged_in = True
            return True, "Successfully logged in to Instagram."
        except Exception as e:
            return False, f"Login failed: {e}"

    def upload_reel(self, video_path, caption):
        if not self.logged_in:
            success, msg = self.login()
            if not success:
                return msg
        try:
            media = self.cl.clip_upload(video_path, caption)
            return f"Success: Reel uploaded! Media ID: {media.pk}"
        except Exception as e:
            return f"Reel upload failed: {e}"

    def upload_photo(self, image_path, caption):
        if not self.logged_in:
            success, msg = self.login()
            if not success:
                return msg
        try:
            media = self.cl.photo_upload(image_path, caption)
            return f"Success: Photo uploaded! Media ID: {media.pk}"
        except Exception as e:
            return f"Photo upload failed: {e}"

if __name__ == "__main__":
    im = InstagramManager()
    print("InstagramManager initialized.")
