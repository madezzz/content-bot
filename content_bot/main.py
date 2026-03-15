"""
main.py — Full Content Automation Pipeline
Chains: Trend → Script → Voice → Video → Upload (YouTube + Instagram + X)
Run manually: python main.py
Runs automatically: GitHub Actions every day at 6am Jakarta
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path

# ── Setup logging ──────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("pipeline.log")
    ]
)
log = logging.getLogger(__name__)

# ── Import all modules ─────────────────────────────────────────────────────────
from trend_finder import get_trending_topics
from script_writer import write_script
from tts_voice import text_to_speech_free
from make_video import create_video
from uploader import upload_to_youtube, upload_to_instagram, post_to_x


def run_pipeline():
    """Runs the full automation pipeline end-to-end."""

    start_time = datetime.now()
    log.info("=" * 60)
    log.info("CONTENT AUTOMATION PIPELINE STARTED")
    log.info(f"Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    log.info("=" * 60)

    # ── Create output folder for today ────────────────────────────────────────
    today = datetime.now().strftime("%Y-%m-%d")
    output_dir = Path(f"output/{today}")
    output_dir.mkdir(parents=True, exist_ok=True)

    results = {
        "date": today,
        "topic": None,
        "script_path": None,
        "voice_path": None,
        "video_path": None,
        "shorts_path": None,
        "youtube_id": None,
        "instagram_id": None,
        "x_post_id": None,
        "errors": []
    }

    # ── STEP 1: Find trending topic ────────────────────────────────────────────
    log.info("\n[STEP 1] Finding trending topics...")
    try:
        topics = get_trending_topics()
        topic = topics[0] if topics else "5 cara hemat uang di Indonesia 2025"
        results["topic"] = topic
        log.info(f"  Topic selected: {topic}")
    except Exception as e:
        topic = "How to save money and build wealth in 2025"
        results["topic"] = topic
        results["errors"].append(f"Trend finder error (using fallback): {e}")
        log.warning(f"  Trend finder failed, using fallback topic: {topic}")

    # ── STEP 2: Write script ───────────────────────────────────────────────────
    log.info("\n[STEP 2] Writing video script with Claude AI...")
    try:
        script = write_script(topic)
        script_path = output_dir / "script.txt"
        script_path.write_text(script, encoding="utf-8")
        results["script_path"] = str(script_path)
        log.info(f"  Script saved: {script_path}")
        log.info(f"  Script preview: {script[:120]}...")
    except Exception as e:
        results["errors"].append(f"Script writer failed: {e}")
        log.error(f"  Script writer failed: {e}")
        _save_results(results)
        return results

    # ── STEP 3: Text-to-speech ─────────────────────────────────────────────────
    log.info("\n[STEP 3] Generating voiceover...")
    try:
        voice_path = str(output_dir / "voice.mp3")
        text_to_speech_free(script, output_path=voice_path, lang="en")
        results["voice_path"] = voice_path
        log.info(f"  Voice saved: {voice_path}")
    except Exception as e:
        results["errors"].append(f"TTS failed: {e}")
        log.error(f"  TTS failed: {e}")
        _save_results(results)
        return results

    # ── STEP 4: Create long video (YouTube) ───────────────────────────────────
    log.info("\n[STEP 4a] Creating long video for YouTube...")
    try:
        video_path = str(output_dir / "video_long.mp4")
        create_video(
            voice_path=voice_path,
            script_path=str(script_path),
            output_path=video_path,
            format="landscape"   # 1920x1080 for YouTube
        )
        results["video_path"] = video_path
        log.info(f"  Long video saved: {video_path}")
    except Exception as e:
        results["errors"].append(f"Long video creation failed: {e}")
        log.error(f"  Long video failed: {e}")

    # ── STEP 4b: Create Shorts/Reels (vertical) ───────────────────────────────
    log.info("\n[STEP 4b] Creating vertical video for Shorts/Reels...")
    try:
        shorts_path = str(output_dir / "video_short.mp4")
        create_video(
            voice_path=voice_path,
            script_path=str(script_path),
            output_path=shorts_path,
            format="vertical"    # 1080x1920 for Shorts/Reels
        )
        results["shorts_path"] = shorts_path
        log.info(f"  Shorts video saved: {shorts_path}")
    except Exception as e:
        results["errors"].append(f"Shorts creation failed: {e}")
        log.error(f"  Shorts video failed: {e}")

    # ── STEP 5a: Upload to YouTube ─────────────────────────────────────────────
    log.info("\n[STEP 5a] Uploading to YouTube...")
    if results["video_path"]:
        try:
            title = _make_title(topic, script)
            description = _make_description(script, topic)
            tags = _make_tags(topic)

            yt_id = upload_to_youtube(
                video_path=results["video_path"],
                title=title,
                description=description,
                tags=tags
            )
            results["youtube_id"] = yt_id
            log.info(f"  YouTube upload success: https://youtube.com/watch?v={yt_id}")
        except Exception as e:
            results["errors"].append(f"YouTube upload failed: {e}")
            log.error(f"  YouTube upload failed: {e}")
    else:
        log.warning("  Skipping YouTube — no long video available")

    # ── STEP 5b: Upload to Instagram Reels ────────────────────────────────────
    log.info("\n[STEP 5b] Uploading to Instagram Reels...")
    if results["shorts_path"]:
        try:
            caption = _make_instagram_caption(script, topic)
            ig_id = upload_to_instagram(
                video_path=results["shorts_path"],
                caption=caption
            )
            results["instagram_id"] = ig_id
            log.info(f"  Instagram Reels upload success: ID {ig_id}")
        except Exception as e:
            results["errors"].append(f"Instagram upload failed: {e}")
            log.error(f"  Instagram upload failed: {e}")
    else:
        log.warning("  Skipping Instagram — no short video available")

    # ── STEP 5c: Post to X (Twitter) ──────────────────────────────────────────
    log.info("\n[STEP 5c] Posting to X (Twitter)...")
    try:
        tweet_thread = _make_tweet_thread(script, topic, results.get("youtube_id"))
        x_id = post_to_x(tweet_thread)
        results["x_post_id"] = x_id
        log.info(f"  X post success: ID {x_id}")
    except Exception as e:
        results["errors"].append(f"X post failed: {e}")
        log.error(f"  X post failed: {e}")

    # ── Final summary ──────────────────────────────────────────────────────────
    duration = (datetime.now() - start_time).seconds
    log.info("\n" + "=" * 60)
    log.info("PIPELINE COMPLETE")
    log.info(f"Duration: {duration}s")
    log.info(f"Topic: {results['topic']}")
    log.info(f"YouTube: {'OK - ' + results['youtube_id'] if results['youtube_id'] else 'FAILED'}")
    log.info(f"Instagram: {'OK - ' + str(results['instagram_id']) if results['instagram_id'] else 'FAILED'}")
    log.info(f"X: {'OK - ' + str(results['x_post_id']) if results['x_post_id'] else 'FAILED'}")
    if results["errors"]:
        log.warning(f"Errors: {len(results['errors'])}")
        for err in results["errors"]:
            log.warning(f"  - {err}")
    log.info("=" * 60)

    _save_results(results)
    return results


# ── Helper functions ───────────────────────────────────────────────────────────

def _make_title(topic: str, script: str) -> str:
    """Creates a click-worthy YouTube title from the topic."""
    first_line = script.split('\n')[0].strip()
    title = first_line[:80] if len(first_line) > 10 else topic[:80]
    return title

def _make_description(script: str, topic: str) -> str:
    """Creates YouTube description with timestamps and hashtags."""
    hashtags = "#finance #uang #Indonesia #motivation #money #investing"
    desc = f"{script[:400]}\n\n"
    desc += "⏰ Timestamps:\n0:00 Introduction\n0:30 Main tips\n1:00 Action steps\n\n"
    desc += f"{hashtags}\n\n"
    desc += "Subscribe for daily finance and motivation content!\n"
    desc += "Dukung channel ini dengan subscribe dan share ke teman-teman!"
    return desc

def _make_tags(topic: str) -> list:
    """Generates relevant YouTube tags."""
    base_tags = [
        "finance", "money", "Indonesia", "motivation", "uang",
        "investasi", "menabung", "keuangan", "tips uang", "finansial"
    ]
    topic_words = [w.lower() for w in topic.split() if len(w) > 3]
    return (base_tags + topic_words)[:30]

def _make_instagram_caption(script: str, topic: str) -> str:
    """Creates Instagram Reels caption with hashtags."""
    hook = script.split('\n')[0][:150]
    hashtags = (
        "#finance #money #Indonesia #motivasi #uang #investasi "
        "#menabung #finansial #keuangan #successmindset "
        "#moneyadvice #financetips #indonesian #jakarta #rupiah"
    )
    return f"{hook}\n\nSave this post! Follow for daily tips\n\n{hashtags}"

def _make_tweet_thread(script: str, topic: str, yt_id: str = None) -> list:
    """Creates a 5-tweet thread from the script."""
    lines = [l.strip() for l in script.split('\n') if l.strip()]
    thread = []

    # Tweet 1: Hook
    thread.append(f"🧵 {lines[0][:240]}\n\n(Thread on: {topic[:60]})")

    # Tweets 2-4: Main points
    for i, line in enumerate(lines[1:4], 2):
        if len(line) > 20:
            thread.append(f"{i}/ {line[:260]}")

    # Tweet 5: CTA with YouTube link
    yt_link = f"https://youtube.com/watch?v={yt_id}" if yt_id else ""
    thread.append(
        f"5/ Follow for daily money tips in English + Bahasa Indonesia 🇮🇩\n\n"
        f"Full video: {yt_link}\n\n#finance #money #Indonesia"
    )

    return thread

def _save_results(results: dict):
    """Saves pipeline results to a JSON log file."""
    log_path = Path("output") / f"results_{results['date']}.json"
    log_path.parent.mkdir(exist_ok=True)
    with open(log_path, "w") as f:
        json.dump(results, f, indent=2)
    log.info(f"Results saved: {log_path}")


if __name__ == "__main__":
    run_pipeline()
