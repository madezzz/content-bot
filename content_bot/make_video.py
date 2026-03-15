"""
make_video.py — Create videos in landscape (YouTube) and vertical (Shorts/Reels) formats.
Uses MoviePy (free, open source).
"""

import os
import textwrap
from moviepy.editor import (
    ColorClip, AudioFileClip, TextClip, CompositeVideoClip
)

def create_video(
    voice_path="output/voice.mp3",
    script_path="output/script.txt",
    output_path="output/final_video.mp4",
    format="vertical"   # "vertical" = Shorts/Reels | "landscape" = YouTube
):
    """
    Creates a video combining voiceover audio with animated text.
    format="vertical"  → 1080x1920 (YouTube Shorts, Instagram Reels)
    format="landscape" → 1920x1080 (YouTube long-form)
    """

    # ── Video dimensions ───────────────────────────────────────────────────────
    if format == "vertical":
        width, height = 1080, 1920
        font_size = 58
        max_chars_per_line = 28
    else:
        width, height = 1920, 1080
        font_size = 46
        max_chars_per_line = 50

    # ── Load audio ─────────────────────────────────────────────────────────────
    audio = AudioFileClip(voice_path)
    duration = audio.duration

    # ── Background (deep dark blue — works for finance/motivation) ─────────────
    bg = ColorClip(size=(width, height), color=(8, 12, 35), duration=duration)

    # ── Load and split script into segments ────────────────────────────────────
    with open(script_path, "r", encoding="utf-8") as f:
        raw_script = f.read()

    lines = [l.strip() for l in raw_script.split('\n') if l.strip()]

    # For short videos, use fewer lines; for long, use more
    max_lines = 8 if format == "vertical" else 15
    lines = lines[:max_lines]

    seg_duration = duration / len(lines)
    text_clips = []

    for i, line in enumerate(lines):
        # Wrap long lines
        wrapped = textwrap.fill(line, width=max_chars_per_line)

        # Determine color — first line (hook) gets accent color
        color = "yellow" if i == 0 else "white"
        font_size_actual = font_size + 10 if i == 0 else font_size

        try:
            txt_clip = (
                TextClip(
                    wrapped,
                    fontsize=font_size_actual,
                    color=color,
                    font="DejaVu-Sans-Bold",
                    method="caption",
                    size=(width - 120, None),
                    align="center"
                )
                .set_position("center")
                .set_start(i * seg_duration)
                .set_duration(seg_duration)
                .crossfadein(0.3)
                .crossfadeout(0.2)
            )
            text_clips.append(txt_clip)
        except Exception:
            # Fallback if font not available
            txt_clip = (
                TextClip(
                    wrapped,
                    fontsize=font_size_actual,
                    color=color,
                    method="label"
                )
                .set_position("center")
                .set_start(i * seg_duration)
                .set_duration(seg_duration)
            )
            text_clips.append(txt_clip)

    # ── Add progress bar (bottom of screen) ───────────────────────────────────
    # A thin colored bar that fills left-to-right as the video plays
    progress_clips = []
    bar_height = 6
    bar_y = height - bar_height - 20
    for i in range(len(lines)):
        fill_width = int(width * ((i + 1) / len(lines)))
        bar = (
            ColorClip(size=(fill_width, bar_height), color=(100, 149, 237))
            .set_position((0, bar_y))
            .set_start(i * seg_duration)
            .set_duration(seg_duration)
            .set_opacity(0.7)
        )
        progress_clips.append(bar)

    # ── Add channel watermark text ─────────────────────────────────────────────
    try:
        watermark = (
            TextClip(
                "Subscribe for daily tips",
                fontsize=28,
                color="gray",
                font="DejaVu-Sans"
            )
            .set_position(("center", height - 80))
            .set_duration(duration)
            .set_opacity(0.5)
        )
        extra_clips = [watermark] + progress_clips
    except Exception:
        extra_clips = progress_clips

    # ── Compose final video ───────────────────────────────────────────────────
    all_clips = [bg] + text_clips + extra_clips
    final = CompositeVideoClip(all_clips, size=(width, height))
    final = final.set_audio(audio)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    final.write_videofile(
        output_path,
        fps=30,
        codec="libx264",
        audio_codec="aac",
        bitrate="4000k",
        preset="fast",
        threads=4,
        logger=None  # Suppress verbose MoviePy output
    )

    print(f"Video saved ({format}): {output_path}")
    return output_path
