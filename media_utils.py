import os
import wave
import numpy as np
from moviepy import AudioFileClip, VideoFileClip

def convert_to_wav(input_path, output_path="temp.wav"):
    ext = os.path.splitext(input_path)[1].lower()

    try:
        # ======================
        # WAV → giữ nguyên
        # ======================
        if ext == ".wav":
            return input_path

        # ======================
        # MP3 / M4A → audio
        # ======================
        if ext in [".mp3", ".m4a"]:
            audio = AudioFileClip(input_path)

        # ======================
        # MP4 → tách audio
        # ======================
        elif ext == ".mp4":
            video = VideoFileClip(input_path)
            audio = video.audio

        else:
            return None

        # Xuất WAV 16-bit, mono
        audio.write_audiofile(
            output_path,
            fps=44100,
            nbytes=2,
            codec="pcm_s16le",
            ffmpeg_params=["-ac", "1"],
            logger=None
        )

        audio.close()
        return output_path

    except Exception as e:
        print("Lỗi convert:", e)
        return None
