from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
import pickle, os, json

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def get_youtube_service():
    creds = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as f:
            creds = pickle.load(f)
    if not creds:
        flow = InstalledAppFlow.from_client_secrets_file(
            "client_secrets.json", SCOPES
        )
        creds = flow.run_local_server(port=0)
        with open("token.pickle", "wb") as f:
            pickle.dump(creds, f)
    return build("youtube", "v3", credentials=creds)

def upload_to_youtube(
    video_path,
    title,
    description,
    tags=["finance","uang","Indonesia","motivation"],
    category_id="22"  # People & Blogs
):
    youtube = get_youtube_service()
    
    body = {
        "snippet": {
            "title": title[:100],
            "description": description,
            "tags": tags,
            "categoryId": category_id
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False
        }
    }
    
    media = MediaFileUpload(video_path, mimetype="video/mp4", resumable=True)
    
    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    )
    
    response = request.execute()
    video_id = response["id"]
    print(f"Uploaded! https://youtube.com/watch?v={video_id}")
    return video_id

if __name__ == "__main__":
    with open("output/script.txt") as f:
        script = f.read()
    
    title = script.split('\n')[0][:80]  # First line = title
    upload_to_youtube("output/final_video.mp4", title, script[:500])
  1. Go to: console.cloud.google.com
2. Create new project (free)
3. Enable "YouTube Data API v3"
4. Create OAuth credentials
5. Download as "client_secrets.json"
6. Put file in your project folder
7. Run uploader.py once to authorize
   → It opens a browser, you click Allow
   → token.pickle is saved, never ask again
