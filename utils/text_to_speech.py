# utils/text_to_speech.py

from gtts import gTTS
import io

def convert_text_to_speech(text, output_path=None):
    """
    Converts text to speech.
    - If output_path is provided, it saves the audio as an MP3 file.
    - If output_path is None, it returns the audio data as bytes.
    """
    try:
        # Using 'co.in' for a different voice accent, which can sometimes be clearer
        tts = gTTS(text=text, lang='en', tld='co.in')

        if output_path:
            # Original functionality: Save to a file if a path is provided
            tts.save(output_path)
            return output_path
        else:
            # NEW functionality: Save to an in-memory bytes buffer
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0) # Rewind the buffer to the beginning
            return audio_buffer.getvalue()

    except Exception as e:
        print(f"Error in gTTS conversion: {e}")
        return None