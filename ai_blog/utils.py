import os
from urllib.parse import urlparse, parse_qs
import yt_dlp
from django.conf import settings
import re


def yt_title(link):
    try:
        # ydl_opts= {'quiet': True}
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{settings.MEDIA_ROOT}/%(title)s.%(ext)s',
            'ffmpeg_location': r"C:\Users\Dell\Downloads\ffmpeg-2025-07-12-git-35a6de137a-full_build\ffmpeg-2025-07-12-git-35a6de137a-full_build\bin",
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=False)
            return info.get('title')
    except Exception as e:
        print("yt_dlp error (title):", e)
        return None
    

def clean_youtube_link(link): # use this in get_blog()
    # If it's a youtu.be link, extract the video ID
    if "youtu.be" in link:
        video_id = link.split("/")[-1].split("?")[0]
        return f"https://www.youtube.com/watch?v={video_id}"
    
    # If it's a normal YouTube link with extra params
    if "youtube.com" in link:
        parsed = urlparse(link)
        qs = parse_qs(parsed.query)
        if "v" in qs:
            return f"https://www.youtube.com/watch?v={qs['v'][0]}"
    return link
    

def sanitize_filename(title):
    # Remove invalid characters for Windows and Linux
    return re.sub(r'[\\/*?:"<>|]', "", title)


def download_audio(link, safe_title):
    output_dir = settings.MEDIA_ROOT
    os.makedirs(output_dir, exist_ok=True)  # Ensure media folder exists

    # Always use sanitized title for filename
    audio_path = os.path.join(output_dir, f"{safe_title}.%(ext)s")

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': audio_path,  # Safe filename
        'quiet': True,
        'postprocessors': [
            {'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}
        ]
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(link, download=True)
            # Return full path of the MP3
            mp3_file = os.path.join(output_dir, f"{safe_title}.mp3")
            return mp3_file
    except Exception as e:
        print("yt_dlp error (audio):", e)
        return None

