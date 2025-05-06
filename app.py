from flask import Flask, render_template, request, send_file
from pytube import YouTube
import subprocess
import os
import uuid

app = Flask(__name__)

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def clean_url(url):
    return url.strip().split("&")[0]

def merge_streams(video_stream, audio_stream):
    unique_id = str(uuid.uuid4())
    video_path = os.path.join(DOWNLOAD_DIR, f"video_{unique_id}.mp4")
    audio_path = os.path.join(DOWNLOAD_DIR, f"audio_{unique_id}.mp4")
    final_path = os.path.join(DOWNLOAD_DIR, f"final_{unique_id}.mp4")

    video_stream.download(filename=video_path)
    audio_stream.download(filename=audio_path)

    command = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-i", audio_path,
        "-c:v", "copy",
        "-c:a", "aac",
        "-strict", "experimental",
        final_path
    ]
    subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    os.remove(video_path)
    os.remove(audio_path)

    return final_path

def download_video(url):
    try:
        yt = YouTube(clean_url(url))

        video_stream = yt.streams.filter(res="1080p", progressive=False, file_extension="mp4").first()
        audio_stream = yt.streams.filter(only_audio=True, file_extension="mp4").first()
        if video_stream and audio_stream:
            return merge_streams(video_stream, audio_stream)

        video_stream = yt.streams.filter(progressive=False, file_extension="mp4").order_by("resolution").desc().first()
        if video_stream and audio_stream:
            return merge_streams(video_stream, audio_stream)

        stream = yt.streams.filter(progressive=True, file_extension="mp4").order_by("resolution").desc().first()
        if stream:
            fallback_path = os.path.join(DOWNLOAD_DIR, f"video_{uuid.uuid4()}.mp4")
            stream.download(filename=fallback_path)
            return fallback_path

        return None

    except Exception as e:
        print("Download failed:", e)
        return None

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form.get("url", "").strip()
        if not url or ("youtube.com" not in url and "youtu.be" not in url):
            return "Invalid or empty YouTube URL."

        final_file = download_video(url)
        if final_file:
            return send_file(final_file, as_attachment=True)
        else:
            return "Could not download in 1080p or fallback resolution."

    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=81)
