import os
import requests
import random
import uuid

class FootageSearcher:
    def __init__(self, pixabay_key=None, pexels_key=None, download_dir="uploads/gameplay"):
        self.pixabay_key = pixabay_key or os.getenv("PIXABAY_API_KEY")
        self.pexels_key = pexels_key or os.getenv("PEXELS_API_KEY")
        self.download_dir = download_dir
        os.makedirs(self.download_dir, exist_ok=True)

    def search_and_download(self, keywords, count=3):
        """Searches and downloads clips based on keywords."""
        all_clips = []

        # 1. Search Pixabay
        if self.pixabay_key:
            all_clips.extend(self._search_pixabay(keywords, count))

        # 2. Search Pexels
        if self.pexels_key:
            all_clips.extend(self._search_pexels(keywords, count))

        # 3. Download a selection
        downloaded_paths = []
        # Take a unique sample
        to_download = random.sample(all_clips, min(len(all_clips), count))

        for url in to_download:
            path = self._download_file(url)
            if path:
                downloaded_paths.append(path)

        return downloaded_paths

    def _search_pixabay(self, keywords, count):
        urls = []
        for query in keywords:
            try:
                url = f"https://pixabay.com/api/videos/?key={self.pixabay_key}&q={urllib.parse.quote(query)}&per_page=5"
                res = requests.get(url).json()
                for hit in res.get('hits', []):
                    # Prefer small/medium for fast processing
                    video_url = hit['videos']['small']['url'] or hit['videos']['medium']['url']
                    urls.append(video_url)
            except Exception as e:
                print(f"Pixabay search error: {e}")
        return urls

    def _search_pexels(self, keywords, count):
        urls = []
        headers = {"Authorization": self.pexels_key}
        for query in keywords:
            try:
                url = f"https://api.pexels.com/videos/search?query={urllib.parse.quote(query)}&per_page=5"
                res = requests.get(url, headers=headers).json()
                for video in res.get('videos', []):
                    # Get a suitable file
                    files = video.get('video_files', [])
                    if files:
                        # Find hd or sd file
                        best_file = files[0]['link']
                        for f in files:
                            if f.get('width') and 720 <= f['width'] <= 1920:
                                best_file = f['link']
                                break
                        urls.append(best_file)
            except Exception as e:
                print(f"Pexels search error: {e}")
        return urls

    def _download_file(self, url):
        try:
            filename = f"source_{uuid.uuid4().hex[:8]}.mp4"
            path = os.path.join(self.download_dir, filename)
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                with open(path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            return path
        except Exception as e:
            print(f"Download error: {e}")
            return None

import urllib.parse
