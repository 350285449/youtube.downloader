# for 1080 p only

from pytube import YouTube
import os
from moviepy.editor import VideoFileClip, AudioFileClip

def download_1080p_video(url):
    try:
        yt = YouTube(url)
        print(f"Title: {yt.title}")
        print(f"Length: {yt.length // 60} minutes")

        video_stream = yt.streams.filter(res="1080p", progressive=False, file_extension='mp4').first()
        audio_stream = yt.streams.filter(only_audio=True, file_extension='mp4').first()

        if not video_stream or not audio_stream:
            print("1080p video or audio stream not found.")
            return

        print("Downloading video...")
        video_file = video_stream.download(filename="video.mp4")

        print("Downloading audio...")
        audio_file = audio_stream.download(filename="audio.mp4")

        print("Merging video and audio...")
        final_clip = VideoFileClip("video.mp4")
        final_audio = AudioFileClip("audio.mp4")
        final_clip = final_clip.set_audio(final_audio)
        final_clip.write_videofile("final_video.mp4", codec='libx264', audio_codec='aac')

        print("Cleanup...")
        os.remove("video.mp4")
        os.remove("audio.mp4")

        print("Download and merge completed! Saved as final_video.mp4")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    video_url = input("Enter the YouTube video URL: ")
    download_1080p_video(video_url)
