import anthropic
import os

def write_script(topic, language="bilingual"):
    client = anthropic.Anthropic(
        api_key=os.environ["ANTHROPIC_API_KEY"]  # Set in GitHub Secrets
    )
    
    prompt = f"""Write a 90-second YouTube video script about: {topic}

Format:
- HOOK (0-5 sec): Shocking statement to grab attention
- MAIN POINT 1 (5-30 sec): Key insight with Indonesia example  
- MAIN POINT 2 (30-60 sec): Actionable tip
- MAIN POINT 3 (60-80 sec): Money/success angle
- CTA (80-90 sec): Ask to subscribe + comment

Style: Simple English + add 2-3 Bahasa Indonesia phrases naturally.
Keep each section SHORT and punchy. No filler words.
Return ONLY the script, no extra commentary."""

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",  # Fastest free model
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return message.content[0].text

if __name__ == "__main__":
    script = write_script("5 ways to save money in Indonesia 2025")
    print(script)
    # Save to file
    with open("output/script.txt", "w") as f:
        f.write(script)
