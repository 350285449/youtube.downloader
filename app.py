from flask import Flask, render_template, request, send_file
from pytube import YouTube
from moviepy.editor import VideoFileClip, AudioFileClip
import os
import uuid

app = Flask(__name__)

def download_1080p_video(url):
    yt = YouTube(url)
    video_stream = yt.streams.filter(res="1080p", progressive=False, file_extension='mp4').first()
    audio_stream = yt.streams.filter(only_audio=True, file_extension='mp4').first()

    if not video_stream or not audio_stream:
        return None

    unique_id = str(uuid.uuid4())
    video_path = f"video_{unique_id}.mp4"
    audio_path = f"audio_{unique_id}.mp4"
    final_path = f"final_{unique_id}.mp4"

    video_stream.download(filename=video_path)
    audio_stream.download(filename=audio_path)

    final_clip = VideoFileClip(video_path)
    final_audio = AudioFileClip(audio_path)
    final_clip = final_clip.set_audio(final_audio)
    final_clip.write_videofile(final_path, codec='libx264', audio_codec='aac')

    os.remove(video_path)
    os.remove(audio_path)

    return final_path

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form["url"]
        final_file = download_1080p_video(url)
        if final_file:
            return send_file(final_file, as_attachment=True)
        else:
            return "Could not download in 1080p."
    return render_template("index.html")

if __name__ == "__main__":
    app.run()
