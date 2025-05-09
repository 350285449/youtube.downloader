from pytube import YouTube
import subprocess
import os
import uuid

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def clean_url(url):
    return url.strip().split("&")[0]

def merge_streams(video, audio, uid):
    video_path = os.path.join(DOWNLOAD_DIR, f"video_{uid}.mp4")
    audio_path = os.path.join(DOWNLOAD_DIR, f"audio_{uid}.mp4")
    output_path = os.path.join(DOWNLOAD_DIR, f"final_{uid}.mp4")

    video.download(filename=video_path)
    audio.download(filename=audio_path)

    subprocess.run([
        "ffmpeg", "-y", "-i", video_path, "-i", audio_path,
        "-c:v", "copy", "-c:a", "aac", output_path
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    os.remove(video_path)
    os.remove(audio_path)
    return output_path

def download_video(url):
    try:
        yt = YouTube(clean_url(url))
        uid = str(uuid.uuid4())

        audio = yt.streams.filter(only_audio=True, file_extension="mp4").first()
        for res in ["1080p", "720p", "480p", "360p"]:
            video = yt.streams.filter(res=res, progressive=False, file_extension="mp4").first()
            if video and audio:
                return merge_streams(video, audio, uid)

        # Fallback to progressive stream
        fallback = yt.streams.filter(progressive=True, file_extension="mp4").order_by("resolution").desc().first()
        if fallback:
            path = os.path.join(DOWNLOAD_DIR, f"video_{uid}.mp4")
            fallback.download(filename=path)
            return path

    except Exception as e:
        print("Error:", e)
    return None

if __name__ == "__main__":
    url = input("Enter YouTube URL: ").strip()
    if "youtube.com" not in url and "youtu.be" not in url:
        print("Invalid YouTube URL.")
    else:
        result = download_video(url)
        print("Downloaded to:" if result else "Download failed.", result or "")
