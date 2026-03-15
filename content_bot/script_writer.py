import anthropic
import os

def write_script(topic, language="bilingual"):
    client = anthropic.Anthropic(
        api_key=os.environ["ANTHROPIC_API_KEY"]
    )

    prompt = f"""Write a 90-second YouTube video script about: {topic}

Format:
- HOOK (0-5 sec): Shocking statement to grab attention
- MAIN POINT 1 (5-30 sec): Key insight with Indonesia example
- MAIN POINT 2 (30-60 sec): Actionable tip anyone can do today
- MAIN POINT 3 (60-80 sec): Money or success angle
- CTA (80-90 sec): Ask viewer to subscribe and comment

Style rules:
- Simple English + add 2-3 Bahasa Indonesia phrases naturally
- Each section SHORT and punchy — no filler words
- Start with a number or shocking fact when possible

Return ONLY the script text, no labels or commentary."""

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )

    script = message.content[0].text
    os.makedirs("output", exist_ok=True)
    with open("output/script.txt", "w", encoding="utf-8") as f:
        f.write(script)

    return script

if __name__ == "__main__":
    script = write_script("5 ways to save money in Indonesia 2025")
    print(script)
