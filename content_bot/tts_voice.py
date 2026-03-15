import requests
import os

def text_to_speech_free(text, output_path="output/voice.mp3", lang="en"):
    chunks = [text[i:i+200] for i in range(0, len(text), 200)]
    audio_parts = []

    for chunk in chunks:
        if not chunk.strip():
            continue
        params = {
            "ie": "UTF-8",
            "q": chunk,
            "tl": lang,
            "client": "tw-ob"
        }
        headers = {"User-Agent": "Mozilla/5.0"}
        try:
            response = requests.get(
                "https://translate.google.com/translate_tts",
                params=params,
                headers=headers,
                timeout=10
            )
            if response.status_code == 200:
                audio_parts.append(response.content)
        except Exception as e:
            print(f"TTS chunk error: {e}")

    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else "output", exist_ok=True)
    with open(output_path, "wb") as f:
        for part in audio_parts:
            f.write(part)

    print(f"Voice saved: {output_path}")
    return output_path

if __name__ == "__main__":
    with open("output/script.txt", "r") as f:
        script = f.read()
    text_to_speech_free(script)
