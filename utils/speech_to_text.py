import os
from openai import OpenAI

def convert_speech_to_text(audio_file_path):
    """
    Converts an audio file to text using OpenAI's Whisper API.
    """
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    try:
        with open(audio_file_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        return transcript.text
    except Exception as e:
        print(f"Error in Whisper API call: {e}")
        return None