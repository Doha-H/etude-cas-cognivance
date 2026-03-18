import streamlit as st
import whisper
from dotenv import load_dotenv
import os 
from mistralai import Mistral

load_dotenv()
api_key = os.getenv("MISTRAL_API_KEY")
client = Mistral(api_key=api_key)

st.title("Étude de cas Cognivance : Système de transformation d’audio bruité en connaissances techniques interrogeables")

@st.cache_resource
def load_model():
    return whisper.load_model("base")

model = load_model()

# Initialisation de la mémoire de l'application
if 'Fiche_technique' not in st.session_state:
    st.session_state['Fiche_technique'] = None

audio_file = st.file_uploader("Dépose ton enregistrement (mp3, m4a, wav)", type=["m4a", "mp3", "wav"])

if st.button("Lancer l'analyse complète"):
        with st.spinner("Transcription en cours..."):
        
            extension = os.path.splitext(audio_file.name)[1]
            nom_temporaire = f"temp_audio{extension}"

            with open(nom_temporaire, "wb") as f:
                f.write(audio_file.read())
            
            result = model.transcribe(nom_temporaire)
            texte_brut = result["text"]
            
            st.subheader("1. Transcription brute avec erreurs possibles")
            st.info(texte_brut)

        with st.spinner("Génération de la fiche technique..."):
            # Synthèse et correction par l'IA (LLM)
            prompt = f"""
            Tu es un expert en maintenance industrielle pour la plateforme le beau geste.
            Voici une transcription audio brute issue d'un environnement de travail très bruité. 
            
            Ton rôle est de :
            1. Analyser la transcription pour identifier et corriger les erreurs de saisie phonétique en te basant sur ton expertise technique (noms de pièces, modèles, outils et matériaux).
            2. Structurer ces informations pour créer une fiche technique professionnelle avec : titre, problème, matériel utilisé et étapes de l'intervention.
            
            Transcription brute : {texte_brut}
            """
            
            chat_response = client.chat.complete(
                model="mistral-large-latest",
                messages=[{"role": "user", "content": prompt}]
            )
            
            # on sauvegarde le résultat dans la mémoire session_state
            st.session_state['Fiche_technique'] = chat_response.choices[0].message.content

# affichage de la fiche
if st.session_state['Fiche_technique']:
    st.subheader("2. Fiche technique optimisée")
    st.success(st.session_state['Fiche_technique'])

    # 3. partie RAG
    st.divider()
    st.subheader("3. Assistant de maintenance (RAG)")
    question = st.text_input("Pose une question sur cette intervention :")

    if question:
        with st.spinner("Recherche dans la fiche..."):
            prompt_rag = f"""
            Tu es l'assistant intelligent de la plateforme le beau geste.
            utilise uniquement les informations de la fiche technique suivante pour répondre à la question.
            Si l'information n'est pas dans la fiche, dis que tu ne sais pas.
            
            Fiche technique :
            {st.session_state['Fiche_technique']}
            
            Question : {question}
            """
            
            response_rag = client.chat.complete(
                model="mistral-large-latest",
                messages=[{"role": "user", "content": prompt_rag}]
            )
            
            st.write("**Réponse de l'assistant :**")
            st.info(response_rag.choices[0].message.content)