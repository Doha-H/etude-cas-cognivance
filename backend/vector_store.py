import chromadb
from mistralai import Mistral
import os
from dotenv import load_dotenv

load_dotenv()

mistral_client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="fiches_techniques")

def get_embedding(text: str) -> list[float]:
    response = mistral_client.embeddings.create(
        model="mistral-embed",
        inputs=[text]
    )
    return response.data[0].embedding

def store_fiche(fiche_id: str, contenu: str, metadata: dict = {}):
    embedding = get_embedding(contenu)
    collection.upsert(
        ids=[fiche_id],
        embeddings=[embedding],
        documents=[contenu],
        metadatas=[metadata]
    )

def search_fiches(question: str, n_results: int = 3) -> list[dict]:
    question_embedding = get_embedding(question)
    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=n_results
    )
    fiches = []
    for i, doc in enumerate(results["documents"][0]):
        fiches.append({
            "id": results["ids"][0][i],
            "contenu": doc,
            "metadata": results["metadatas"][0][i]
        })
    return fiches
