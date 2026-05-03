import os, requests

def tts_to_file(text: str, out_path: str="resultado.mp3",
                voice_id: str="21m00Tcm4TlvDq8ikWAM"):  # 'Rachel' por defecto
    api_key = os.getenv("ELEVEN_API_KEY")
    if not api_key:
        raise RuntimeError("Falta ELEVEN_API_KEY en variables de entorno.")

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {"xi-api-key": api_key}
    data = {"text": text, "model_id": "eleven_multilingual_v2"}
    r = requests.post(url, json=data, headers=headers, timeout=60)
    r.raise_for_status()
    with open(out_path, "wb") as f:
        f.write(r.content)
    return out_path
