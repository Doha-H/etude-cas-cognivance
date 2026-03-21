from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid
from datetime import datetime
import os
from typing import List

from transcribe import transcribe_audio
from structure import structure_fiche, answer_question
import vector_store

app = FastAPI(
    title="Audio-to-Knowledge API",
    version="2.0"
)

# Configuration CORS pour permettre les requêtes depuis le frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QuestionRequest(BaseModel):
    question: str

class QuestionResponse(BaseModel):
    reponse: str
    sources: List[dict]

class FicheResponse(BaseModel):
    id: str
    transcription: str
    fiche_structuree: str
    date: str

class StatsResponse(BaseModel):
    nombre_fiches: int

@app.get("/")
def root():
    """Endpoint racine - Informations sur l'API"""
    return {
        "message": "Audio-to-Knowledge API",
        "description": "Pipeline LLM + RAG pour transformer des enregistrements audio bruités en fiches techniques structurées et interrogeables."
    }

@app.post("/fiches", response_model=FicheResponse)
async def create_fiche(audio: UploadFile = File(...)):
    """
    Upload un fichier audio, le transcrit, le structure et le stocke dans ChromaDB.

    Returns:
        - id: UUID unique de la fiche
        - transcription: Texte brut transcrit
        - fiche_structuree: Fiche technique structurée
        - date: Date de création
    """
    # Validation du type de fichier
    allowed_extensions = [".mp3", ".m4a", ".wav"]
    file_extension = os.path.splitext(audio.filename)[1].lower()
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Format de fichier non supporté. Formats acceptés : {', '.join(allowed_extensions)}"
        )

    # Sauvegarde temporaire du fichier
    temp_filename = f"temp_audio_{uuid.uuid4()}{file_extension}"
    try:
        with open(temp_filename, "wb") as f:
            content = await audio.read()
            f.write(content)

        # Étape 1 : Transcription avec Whisper
        transcription = transcribe_audio(temp_filename)

        # Étape 2 : Structuration avec Mistral
        fiche_structuree = structure_fiche(transcription)

        # Étape 3 : Stockage dans ChromaDB
        fiche_id = str(uuid.uuid4())
        date_creation = datetime.now().isoformat()

        metadata = {
            "date": date_creation,
            "filename": audio.filename
        }

        vector_store.store_fiche(
            fiche_id=fiche_id,
            contenu=fiche_structuree,
            metadata=metadata
        )

        return FicheResponse(
            id=fiche_id,
            transcription=transcription,
            fiche_structuree=fiche_structuree,
            date=date_creation
        )

    finally:
        # Nettoyage du fichier temporaire
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

@app.post("/ask", response_model=QuestionResponse)
def ask_question(request: QuestionRequest):
    """
    Répond à une question en utilisant la recherche sémantique dans les fiches.

    Args:
        question: Question de l'utilisateur

    Returns:
        - reponse: Réponse générée par Mistral
        - sources: Liste des fiches utilisées comme contexte
    """
    # Recherche sémantique dans ChromaDB
    fiches_trouvees = vector_store.search_fiches(request.question, n_results=3)

    if not fiches_trouvees:
        return QuestionResponse(
            reponse="Aucune fiche technique n'a été trouvée dans la base de connaissances.",
            sources=[]
        )

    # Génération de la réponse avec Mistral
    reponse = answer_question(request.question, fiches_trouvees)

    return QuestionResponse(
        reponse=reponse,
        sources=fiches_trouvees
    )

@app.get("/stats", response_model=StatsResponse)
def get_stats():
    """
    Retourne les statistiques de la base de connaissances.

    Returns:
        - nombre_fiches: Nombre total de fiches stockées
    """
    count = vector_store.collection.count()
    return StatsResponse(nombre_fiches=count)
