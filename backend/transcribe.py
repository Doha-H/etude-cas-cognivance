import whisper
import os

# Chargement du modèle Whisper (base)
model = whisper.load_model("base")

def transcribe_audio(file_path: str) -> str:
    """
    Transcrit un fichier audio en texte avec Whisper.

    Args:
        file_path: Chemin vers le fichier audio

    Returns:
        Texte transcrit
    """
    result = model.transcribe(file_path)
    return result["text"]
