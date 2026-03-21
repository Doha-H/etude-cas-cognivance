from mistralai import Mistral
import os
from dotenv import load_dotenv

load_dotenv()

client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))

def structure_fiche(transcription: str) -> str:
    """
    Structure une transcription audio brute en fiche technique professionnelle.

    Args:
        transcription: Texte brut transcrit depuis l'audio

    Returns:
        Fiche technique structurée
    """
    prompt = f"""
    Tu es un expert en maintenance industrielle pour la plateforme le beau geste.
    Voici une transcription audio brute issue d'un environnement de travail très bruité.
    Ton rôle est de :
    1. Analyser la transcription pour identifier et corriger les erreurs de saisie phonétique en te basant sur ton expertise technique (noms de pièces, modèles, outils et matériaux).
    2. Structurer ces informations pour créer une fiche technique professionnelle avec : titre, problème, matériel utilisé et étapes de l'intervention.
    Transcription brute : {transcription}
    """

    chat_response = client.chat.complete(
        model="mistral-large-latest",
        messages=[{"role": "user", "content": prompt}]
    )

    return chat_response.choices[0].message.content

def answer_question(question: str, context_fiches: list[dict]) -> str:
    """
    Répond à une question en utilisant le contexte des fiches techniques.

    Args:
        question: Question de l'utilisateur
        context_fiches: Liste de fiches trouvées par recherche sémantique

    Returns:
        Réponse générée par Mistral
    """
    # Construction du contexte à partir des fiches
    contexte = "\n\n---\n\n".join([
        f"Fiche {i+1} (ID: {fiche['id']}):\n{fiche['contenu']}"
        for i, fiche in enumerate(context_fiches)
    ])

    prompt_rag = f"""
    Tu es l'assistant intelligent de la plateforme le beau geste.
    Utilise uniquement les informations des fiches techniques suivantes pour répondre à la question.
    Si l'information n'est pas dans les fiches, dis que tu ne sais pas.

    Fiches techniques :
    {contexte}

    Question : {question}
    """

    response_rag = client.chat.complete(
        model="mistral-large-latest",
        messages=[{"role": "user", "content": prompt_rag}]
    )

    return response_rag.choices[0].message.content
