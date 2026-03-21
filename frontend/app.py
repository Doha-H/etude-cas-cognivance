import streamlit as st
import requests
import os

# Configuration de la page
st.set_page_config(
    page_title="Audio-to-Knowledge",
    page_icon="A",
    layout="wide"
)

# Récupération de l'URL du backend
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# ========== SIDEBAR ==========
with st.sidebar:
    st.title("A propos de ce projet")

    st.markdown("""
    Cette application permet de :
    - Transcrire des enregistrements audio bruites
    - Corriger automatiquement les erreurs de transcription
    - Generer des fiches techniques structurees
    - Stocker et rechercher semantiquement dans une base vectorielle
    - Interroger la base de connaissances en langage naturel
    """)

    st.subheader("Technologies utilisees")
    technologies = [
        "Whisper (Transcription)",
        "Mistral AI (LLM)",
        "ChromaDB (Base vectorielle)",
        "FastAPI + Streamlit"
    ]
    for tech in technologies:
        st.markdown(f"- {tech}")

    st.markdown("---")

    # Vérification de l'état du backend
    st.subheader("Etat du backend")
    try:
        response = requests.get(f"{BACKEND_URL}/", timeout=2)
        if response.status_code == 200:
            st.success("Backend operationnel")
            data = response.json()
        else:
            st.error("Backend inaccessible")
    except Exception as e:
        st.error("Backend inaccessible")
        st.caption(f"Erreur : {str(e)}")

# ========== PAGE PRINCIPALE ==========
st.title("RAG Audio-to-Knowledge - Etude de cas Cognivance ")
st.markdown("Transformez vos enregistrements audio de maintenance industrielle en fiches techniques structurees et interrogeables.")

# Création des onglets
tab1, tab2 = st.tabs(["Creer une fiche technique", "Base de connaissances"])

# ========== ONGLET 1  ==========
with tab1:
    st.header("Creer une fiche technique depuis un enregistrement audio")
    st.markdown("Deposez un ou plusieurs enregistrements audio pour generer automatiquement des fiches techniques")

    # Upload de fichiers (multiple)
    audio_files = st.file_uploader(
        "Selectionnez vos fichiers audio",
        type=["mp3", "m4a", "wav"],
        accept_multiple_files=True,
        help="Formats acceptes : MP3, M4A, WAV (max 200MB par fichier)"
    )

    if audio_files:
        st.info(f"{len(audio_files)} fichier(s) selectionne(s)")

        if st.button("Analyser"):
            # Barre de progression
            progress_bar = st.progress(0)
            status_text = st.empty()

            results = []

            for i, audio_file in enumerate(audio_files):
                status_text.text(f"Traitement de {audio_file.name}... ({i+1}/{len(audio_files)})")

                try:
                    # Appel à l'API backend
                    files = {"audio": (audio_file.name, audio_file.getvalue(), audio_file.type)}
                    response = requests.post(f"{BACKEND_URL}/fiches", files=files, timeout=300)

                    if response.status_code == 200:
                        data = response.json()
                        results.append({
                            "filename": audio_file.name,
                            "success": True,
                            "data": data
                        })
                    else:
                        results.append({
                            "filename": audio_file.name,
                            "success": False,
                            "error": response.json().get("detail", "Erreur inconnue")
                        })

                except Exception as e:
                    results.append({
                        "filename": audio_file.name,
                        "success": False,
                        "error": str(e)
                    })

                # Mise à jour de la progression
                progress_bar.progress((i + 1) / len(audio_files))

            status_text.text("Traitement termine !")

            # Affichage des résultats
            st.markdown("---")
            st.subheader("Resultats")

            for result in results:
                if result["success"]:
                    with st.expander(f"[OK] {result['filename']}", expanded=True):
                        data = result["data"]

                        col1, col2 = st.columns([2, 1])
                        with col1:
                            st.markdown(f"**ID:** `{data['id']}`")
                        with col2:
                            st.markdown(f"**Date:** {data['date'][:19].replace('T', ' ')}")

                        st.markdown("### 1. Transcription brute")
                        st.info(data["transcription"])

                        st.markdown("### 2. Fiche technique structuree")
                        st.success(data["fiche_structuree"])
                else:
                    with st.expander(f"[ERREUR] {result['filename']}", expanded=False):
                        st.error(f"Erreur : {result['error']}")

# ========== ONGLET 2 : BASE DE CONNAISSANCES ==========
with tab2:
    st.header("Base de connaissances")

    # Affichage du nombre de fiches
    try:
        stats_response = requests.get(f"{BACKEND_URL}/stats", timeout=5)
        if stats_response.status_code == 200:
            stats = stats_response.json()
            nombre_fiches = stats["nombre_fiches"]

            st.success(f"""
            Contient {nombre_fiches} fiche(s) technique(s)
            """)
        else:
            st.warning("Impossible de recuperer les statistiques")
            nombre_fiches = 0
    except Exception as e:
        st.error(f"Erreur de connexion : {str(e)}")
        nombre_fiches = 0

    st.markdown("---")

    if nombre_fiches > 0:
        st.subheader("Assistant de maintenance (RAG)")
        st.markdown("Posez une question sur vos interventions passees")

        # Champ de question
        question = st.text_input(
            "Votre question",
            placeholder="Ex: Quels sont les outils necessaires pour changer un roulement ?",
            label_visibility="collapsed"
        )

        if question:
            with st.spinner("Recherche dans la base de connaissances..."):
                try:
                    # Appel à l'endpoint /ask
                    payload = {"question": question}
                    response = requests.post(f"{BACKEND_URL}/ask", json=payload, timeout=30)

                    if response.status_code == 200:
                        data = response.json()

                        st.markdown("### Reponse de l'assistant")
                        st.info(data["reponse"])

                        if data["sources"]:
                            st.markdown("### Sources utilisees")
                            for i, source in enumerate(data["sources"], 1):
                                with st.expander(f"Source {i} - ID: {source['id']}", expanded=False):
                                    st.markdown(source["contenu"])
                                    if "metadata" in source and source["metadata"]:
                                        st.caption(f"Metadonnees : {source['metadata']}")
                    else:
                        st.error("Erreur lors de la recherche")

                except Exception as e:
                    st.error(f"Erreur : {str(e)}")
    else:
        st.info("Commencez par ajouter des fiches dans l'onglet 'Creer une fiche technique depuis un enregistrement audio'")
