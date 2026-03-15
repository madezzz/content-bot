from moviepy.editor import *
import os

def create_video(
    voice_path="output/voice.mp3",
    output_path="output/final_video.mp4",
    background_color=(10, 10, 40)  # Dark blue background
):
    # Load voice audio
    audio = AudioFileClip(voice_path)
    duration = audio.duration
    
    # Create background (solid color - no copyright issues)
    bg = ColorClip(size=(1080, 1920), color=background_color, duration=duration)
    
    # Add text overlay from script
    with open("output/script.txt", "r") as f:
        script_lines = f.read().split('
')[:8]  # First 8 lines
    
    text_clips = []
    for i, line in enumerate(script_lines):
        if line.strip():
            txt = TextClip(
                line[:60],  # Max 60 chars per line
                fontsize=50,
                color='white',
                font='Arial-Bold',
                size=(1000, None),
                method='caption'
            ).set_position(('center', 400 + i * 120))              .set_start(i * (duration / len(script_lines)))              .set_duration(duration / len(script_lines))
            text_clips.append(txt)
    
    # Compose final video
    final = CompositeVideoClip([bg] + text_clips)
    final = final.set_audio(audio)
    
    os.makedirs("output", exist_ok=True)
    final.write_videofile(
        output_path,
        fps=30,
        codec='libx264',
        audio_codec='aac'
    )
    print(f"Video saved: {output_path}")
    return output_path

if __name__ == "__main__":
    create_video()
