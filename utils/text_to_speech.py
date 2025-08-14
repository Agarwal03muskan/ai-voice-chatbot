from gtts import gTTS

def convert_text_to_speech(text, output_path):
    """
    Converts text to an MP3 audio file using gTTS.
    """
    try:
        tts = gTTS(text=text, lang='en', tld='com')
        tts.save(output_path)
        return output_path
    except Exception as e:
        print(f"Error in gTTS conversion: {e}")
        return None