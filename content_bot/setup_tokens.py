"""
setup_tokens.py — Run this ONE TIME on your laptop.
It authorizes YouTube and encodes your token for GitHub Secrets.
After this, everything runs automatically in the cloud.
"""

import pickle
import base64
import os
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def setup_youtube():
    print("\n[1/3] Setting up YouTube...")
    print("     A browser window will open — click 'Allow'")
    print("     Make sure client_secrets.json is in this folder\n")

    flow = InstalledAppFlow.from_client_secrets_file("client_secrets.json", SCOPES)
    creds = flow.run_local_server(port=0)

    with open("token.pickle", "wb") as f:
        pickle.dump(creds, f)

    # Encode for GitHub Secrets
    with open("token.pickle", "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")

    print("\n[2/3] YouTube authorized!")
    print("\n[3/3] Add this to GitHub Secrets as YOUTUBE_TOKEN_B64:")
    print("=" * 60)
    print(encoded[:80] + "...  (truncated, copy the full value below)")
    print("=" * 60)

    with open("YOUTUBE_TOKEN_B64.txt", "w") as f:
        f.write(encoded)

    print("\nFull token saved to: YOUTUBE_TOKEN_B64.txt")
    print("Copy the contents of that file into GitHub Secrets.")
    print("\nDo NOT commit this file to GitHub!")
    print("\nDone! Your pipeline is ready to run automatically.")

def print_secrets_guide():
    print("""
╔══════════════════════════════════════════════════════════════╗
║           GITHUB SECRETS SETUP GUIDE                        ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Go to: github.com → Your Repo → Settings → Secrets         ║
║         → Actions → New repository secret                   ║
║                                                              ║
║  Add these secrets (name = value):                           ║
║                                                              ║
║  ANTHROPIC_API_KEY        → from console.anthropic.com       ║
║  GOOGLE_CLIENT_SECRETS    → contents of client_secrets.json  ║
║  YOUTUBE_TOKEN_B64        → from YOUTUBE_TOKEN_B64.txt       ║
║                                                              ║
║  IG_ACCESS_TOKEN          → from Meta Developer Portal       ║
║  IG_ACCOUNT_ID            → your Instagram Business ID       ║
║                                                              ║
║  X_API_KEY                → from developer.twitter.com       ║
║  X_API_SECRET             → from developer.twitter.com       ║
║  X_ACCESS_TOKEN           → from developer.twitter.com       ║
║  X_ACCESS_TOKEN_SECRET    → from developer.twitter.com       ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
""")

if __name__ == "__main__":
    print_secrets_guide()
    answer = input("Ready to authorize YouTube now? (y/n): ").strip().lower()
    if answer == "y":
        setup_youtube()
    else:
        print("Run this script again when you have client_secrets.json ready.")
