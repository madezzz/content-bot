"""
uploader.py — Upload to YouTube, Instagram Reels, and X (Twitter)
All three platforms, one file.
"""

import os
import time
import json
import pickle
import requests
import logging

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

log = logging.getLogger(__name__)

# ══════════════════════════════════════════════════════════════════════════════
# YOUTUBE UPLOAD
# ══════════════════════════════════════════════════════════════════════════════

YOUTUBE_SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def _get_youtube_service():
    """Authenticates and returns YouTube API client."""
    creds = None

    # Load saved credentials
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as f:
            creds = pickle.load(f)

    # Refresh or re-authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "client_secrets.json", YOUTUBE_SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open("token.pickle", "wb") as f:
            pickle.dump(creds, f)

    return build("youtube", "v3", credentials=creds)


def upload_to_youtube(video_path, title, description, tags=None, category_id="22"):
    """
    Uploads a video to YouTube.
    category_id 22 = People & Blogs (good for finance/motivation)
    category_id 27 = Education
    """
    youtube = _get_youtube_service()

    body = {
        "snippet": {
            "title": title[:100],
            "description": description[:5000],
            "tags": tags or [],
            "categoryId": category_id,
            "defaultLanguage": "en",
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False,
            "madeForKids": False,
        }
    }

    media = MediaFileUpload(
        video_path,
        mimetype="video/mp4",
        resumable=True,
        chunksize=1024 * 1024  # 1MB chunks
    )

    log.info(f"  Uploading to YouTube: {title[:60]}...")
    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            pct = int(status.progress() * 100)
            log.info(f"  YouTube upload: {pct}%")

    video_id = response["id"]
    log.info(f"  YouTube done: https://youtube.com/watch?v={video_id}")
    return video_id


# ══════════════════════════════════════════════════════════════════════════════
# INSTAGRAM REELS UPLOAD  (via Meta Graph API — free)
# ══════════════════════════════════════════════════════════════════════════════
# Setup:
#   1. Go to developers.facebook.com → Create App (free)
#   2. Add "Instagram Graph API" product
#   3. Get your Instagram Business Account ID
#   4. Generate a long-lived access token (valid 60 days, auto-refresh below)
#   5. Set env vars: IG_ACCESS_TOKEN and IG_ACCOUNT_ID

IG_API = "https://graph.instagram.com/v19.0"

def upload_to_instagram(video_path, caption):
    """
    Uploads a video as an Instagram Reel using Meta Graph API.
    Requires: IG_ACCESS_TOKEN and IG_ACCOUNT_ID environment variables.
    """
    token = os.environ.get("IG_ACCESS_TOKEN")
    account_id = os.environ.get("IG_ACCOUNT_ID")

    if not token or not account_id:
        raise ValueError("Set IG_ACCESS_TOKEN and IG_ACCOUNT_ID in GitHub Secrets")

    # Step 1: Create media container
    # NOTE: Instagram requires the video to be hosted at a public URL.
    # For GitHub Actions, we upload to a temporary host first.
    video_url = _upload_to_temp_host(video_path)

    log.info("  Creating Instagram media container...")
    container_res = requests.post(
        f"{IG_API}/{account_id}/media",
        data={
            "media_type": "REELS",
            "video_url": video_url,
            "caption": caption[:2200],
            "share_to_feed": True,
            "access_token": token
        }
    )
    container_res.raise_for_status()
    container_id = container_res.json()["id"]

    # Step 2: Wait for video processing (Instagram needs time)
    log.info("  Waiting for Instagram to process video...")
    for attempt in range(12):  # Wait up to 2 minutes
        time.sleep(10)
        status_res = requests.get(
            f"{IG_API}/{container_id}",
            params={"fields": "status_code", "access_token": token}
        )
        status = status_res.json().get("status_code", "")
        log.info(f"  Instagram status: {status} (attempt {attempt + 1}/12)")
        if status == "FINISHED":
            break
        if status == "ERROR":
            raise RuntimeError("Instagram video processing failed")

    # Step 3: Publish the container
    log.info("  Publishing Instagram Reel...")
    publish_res = requests.post(
        f"{IG_API}/{account_id}/media_publish",
        data={
            "creation_id": container_id,
            "access_token": token
        }
    )
    publish_res.raise_for_status()
    media_id = publish_res.json()["id"]
    log.info(f"  Instagram published: ID {media_id}")
    return media_id


def _upload_to_temp_host(video_path):
    """
    Uploads video to file.io (free, anonymous, 1-time download link).
    Returns a public URL Instagram can fetch from.
    Alternative: use your own server, S3, or Cloudinary free tier.
    """
    log.info(f"  Uploading video to temp host...")
    with open(video_path, "rb") as f:
        res = requests.post(
            "https://file.io",
            files={"file": f},
            data={"expires": "1d"}  # Expires after 1 day
        )
    res.raise_for_status()
    url = res.json()["link"]
    log.info(f"  Temp URL: {url}")
    return url


def refresh_instagram_token():
    """
    Call this monthly to keep your Instagram token alive.
    Tokens expire after 60 days — this refreshes them automatically.
    """
    token = os.environ.get("IG_ACCESS_TOKEN")
    res = requests.get(
        "https://graph.instagram.com/refresh_access_token",
        params={"grant_type": "ig_refresh_token", "access_token": token}
    )
    new_token = res.json().get("access_token")
    if new_token:
        log.info("Instagram token refreshed successfully")
        return new_token
    return token


# ══════════════════════════════════════════════════════════════════════════════
# X (TWITTER) POST  (via X API v2 free tier)
# ══════════════════════════════════════════════════════════════════════════════
# Setup:
#   1. Go to developer.twitter.com → Apply for free account
#   2. Create a project + app
#   3. Get: API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET
#   4. Set all 4 as GitHub Secrets

def post_to_x(tweet_thread: list) -> str:
    """
    Posts a thread to X (Twitter) using API v2.
    tweet_thread = list of tweet strings (each max 280 chars).
    Returns the ID of the first tweet.
    """
    api_key = os.environ.get("X_API_KEY")
    api_secret = os.environ.get("X_API_SECRET")
    access_token = os.environ.get("X_ACCESS_TOKEN")
    access_token_secret = os.environ.get("X_ACCESS_TOKEN_SECRET")

    if not all([api_key, api_secret, access_token, access_token_secret]):
        raise ValueError("Set X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET in GitHub Secrets")

    # Use requests-oauthlib for OAuth 1.0a
    from requests_oauthlib import OAuth1

    auth = OAuth1(api_key, api_secret, access_token, access_token_secret)
    url = "https://api.twitter.com/2/tweets"

    first_tweet_id = None
    reply_to_id = None

    for i, tweet_text in enumerate(tweet_thread):
        tweet_text = tweet_text[:280]  # Enforce 280 char limit

        payload = {"text": tweet_text}
        if reply_to_id:
            payload["reply"] = {"in_reply_to_tweet_id": reply_to_id}

        response = requests.post(url, auth=auth, json=payload)
        response.raise_for_status()

        tweet_id = response.json()["data"]["id"]
        reply_to_id = tweet_id

        if i == 0:
            first_tweet_id = tweet_id
            log.info(f"  X thread started: https://twitter.com/i/web/status/{tweet_id}")
        else:
            log.info(f"  X reply {i + 1}/{len(tweet_thread)} posted")

        time.sleep(1)  # Small delay between tweets

    return first_tweet_id
