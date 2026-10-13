from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

def encontrar_clip_viral(segmentos_whisper):
    print("✨ Asking Gemini to analyze the transcript...")

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set. Add it to a .env file or export it in your shell.")

    texto_con_tiempos = ""
    for seg in segmentos_whisper:
        texto_con_tiempos += f"[{seg['start']:.1f}s] {seg['text']}\n"

    prompt = f"""
    Act as a professional video editor. Analyze this timestamped transcript.
    Identify the best segment for a viral Short (30-60 seconds).

    Transcript:
    {texto_con_tiempos}

    Respond ONLY in this exact format (no extra explanations):
    TITLE: [Write a catchy title]
    START: [Timestamp in seconds, e.g. 120.5]
    END: [Timestamp in seconds, e.g. 155.0]
    REASON: [Brief explanation]
    """

    client = genai.Client(api_key=api_key)
    interaction = client.interactions.create(
        model="gemini-3.8-flash",
        input=prompt,
        generation_config={"temperature": 0.7},
        store=False
    )
    return interaction.output_text