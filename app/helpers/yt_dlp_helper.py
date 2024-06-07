# helpers/yt_dlp_helpers.py

import subprocess
import yt_dlp

def get_video_duration(youtube_url):
    """Get the duration of the video in seconds using yt-dlp."""
    command = ['yt-dlp', '--get-duration', youtube_url]
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    duration_str = result.stdout.strip()

    # Convert duration to seconds
    h, m, s = 0, 0, 0
    parts = duration_str.split(':')
    if len(parts) == 3:
        h, m, s = parts
    elif len(parts) == 2:
        m, s = parts
    elif len(parts) == 1:
        s = parts[0]
    duration = int(h) * 3600 + int(m) * 60 + int(s)
    return duration

def download_youtube_clip(url, start_time, end_time, output_path):
    """Download a specific clip from a YouTube video."""
    ydl_opts = {
        'format': 'bestvideo',
        'outtmpl': output_path,
        'download_sections': [(start_time, end_time)],
        'merge_output_format': 'mp4'
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])