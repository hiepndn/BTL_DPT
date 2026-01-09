import os
from moviepy import AudioFileClip, VideoFileClip

def convert_to_wav(input_path, output_path="temp_converted.wav"):
    """Chuyển đổi MP3, M4A, MP4 sang WAV 16-bit Mono chuẩn cho DSP"""
    ext = os.path.splitext(input_path)[1].lower()

    try:
        
        if ext == ".wav":
            return input_path

        audio = None
        
        if ext in [".mp3", ".m4a"]:
            audio = AudioFileClip(input_path)

        elif ext == ".mp4":
            video = VideoFileClip(input_path)
            audio = video.audio
        
        else:
            return None

        audio.write_audiofile(
            output_path,
            fps=44100,
            nbytes=2,
            codec="pcm_s16le",
            ffmpeg_params=["-ac", "1"],
            logger=None 
        )

        audio.close()
        if ext == ".mp4": video.close() 
        
        return output_path

    except Exception as e:
        print(f"❌ Lỗi convert: {e}")
        return None