import os
from typing import Dict, List
from unittest import result
import requests
import urllib.request
import yt_dlp


class YouTubeData(object):

    def __init__(self, url) -> None:
        self.url = url
        with yt_dlp.YoutubeDL() as ydl:
            download = ydl.extract_info(self.url, download=False)
        self.title = download['title']
        self.video_id = download['id']

    def list_all_subtitles(self) -> Dict[str, List[Dict]]:
        results = {}
        ydl_opts = {
            "writeautomaticsub": True, 
            'writeinfojson': True,
            'writeannotations': True, 
            'subtitleslangs': ['en', 'fr', 'ar'],
            'subtitlesformat': 'ttml'
            }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            meta = ydl.extract_info(self.url, download=False) 
            results = meta['automatic_captions']
        subs = meta.get('subtitles')
        if subs is not None:
            for lang in subs:
                results[lang] = subs[lang]
        return results

    def get_subtitle(self, lang, format, save_to_file=False, filename=None):
        all_subs = self.list_all_subtitles()
        lang_subs = all_subs.get(lang, [])
        sub_url = None
        for sub in lang_subs:
            if sub.get('ext') == format:
                sub_url = sub.get('url')
                break
        if sub_url is None:
            return None
        response = requests.get(sub_url)
        data = response.text
        if not filename:
            filename = f'{self.title}-{self.video_id}.{format}'
        if save_to_file:
            with open(filename, 'w') as f:
                f.write(data)
        return data

    def download_audio_track(self):
        filename = f"{self.title}-{self.video_id}.wav"
        ydl_opts = {
            "format": "bestaudio/best"
        }
        if os.path.exists(filename):
            return filename

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            download = ydl.extract_info(self.url, download=False)
        
        urllib.request.urlretrieve(download['url'], filename)
        return filename
         
