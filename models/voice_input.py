import whisper
import tempfile
import os

def transcribe_audio(uploaded_file):
    try:
        model = whisper.load_model("base")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
            temp_file.write(uploaded_file.read())
            temp_file_path = temp_file.name

        result = model.transcribe(temp_file_path)
        os.remove(temp_file_path)
        return result["text"]
    except Exception as e:
        return f"❌ Error transcribing audio: {str(e)}"
