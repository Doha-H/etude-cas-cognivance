# Étude de cas Cognivance : Système de transformation d'audio bruité en connaissances techniques interrogeables

Cette étude de cas personnelle explore une problématique terrain rencontrée par la plateforme CoGeo : comment transformer des enregistrements audio issus d'environnements industriels bruités en une base de connaissances techniques structurée et interrogeable.

Ce prototype a été réalisé en amont de ma candidature de stage pour démontrer ma compréhension du sujet et proposer une première approche technique.

---

## Architecture du projet

```
projet/
├── backend/              # API FastAPI
│   ├── main.py          # Points d'entrée API
│   ├── transcribe.py    # Module Whisper (transcription audio)
│   ├── structure.py     # Module Mistral (structuration)
│   ├── vector_store.py  # Module ChromaDB (embeddings + recherche)
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/            # Interface Streamlit
│   ├── app.py          # Application web
│   ├── requirements.txt
│   └── Dockerfile
│
├── chroma_db/          # Base vectorielle (générée automatiquement, persistante)
├── docker-compose.yml  # Orchestration des services
├── .env                # Variables d'environnement
└── .env.example        # Template pour .env
```

---

## Stack technique

| Composant            | Technologie      | Rôle                                       |
| :------------------- | :--------------- | :----------------------------------------- |
| **Backend API**      | FastAPI          | Serveur REST (port 8000)                   |
| **Frontend**         | Streamlit        | Interface utilisateur (port 8501)          |
| **Traitement audio** | FFmpeg           | Dépendance système pour Whisper            |
| **Transcription**    | OpenAI Whisper   | Speech-to-text (modèle `base`)             |
| **LLM**              | Mistral Large    | Correction et structuration des fiches     |
| **Embeddings**       | Mistral Embed    | Vectorisation pour la recherche sémantique |
| **Base vectorielle** | ChromaDB         | Stockage et recherche de similarité        |
| **Conteneurisation** | Docker + Compose | Déploiement multi-services                 |

---

## Lancement (avec Docker)

**Prérequis :** Docker et Docker Compose installés

1. **Configuration** :

   ```bash
   cp .env.example .env
   # Éditez .env et ajoutez : MISTRAL_API_KEY=votre_cle_ici
   ```

2. **Démarrer l'application** :

   ```bash
   docker-compose up --build
   ```

3. **Accéder à l'interface** :
   - Frontend : http://localhost:8501
   - Documentation API : http://localhost:8000/docs

---

## Fonctionnalités

### Onglet 1 : Nouvelle intervention

- **Upload multiple** : Déposez un ou plusieurs fichiers audio (mp3, m4a, wav)
- **Traitement automatique** :
  1. Transcription audio → texte brut (Whisper)
  2. Correction et structuration → fiche technique (Mistral)
  3. Stockage dans ChromaDB avec embeddings vectoriels
- **Affichage** : Transcription brute + fiche structurée + métadonnées (ID, date)
- **Barre de progression** pour les uploads multiples

### Onglet 2 : Base de connaissances

- **Compteur de fiches** : Affiche le nombre total de fiches dans la base
- **Recherche sémantique** : Posez une question en langage naturel
- **Réponse contextuelle** : Le système récupère les 3 fiches les plus pertinentes et génère une réponse via RAG (Retrieval-Augmented Generation)
- **Transparence** : Affiche les fiches sources utilisées pour la réponse

---

## Endpoints API

| Méthode | Endpoint  | Description                                     | Entrée                      | Sortie                              |
| :------ | :-------- | :---------------------------------------------- | :-------------------------- | :---------------------------------- |
| `POST`  | `/fiches` | Créer une fiche technique depuis un audio       | Fichier audio (form-data)   | ID, transcription, fiche structurée |
| `POST`  | `/ask`    | Poser une question sur la base de connaissances | JSON: `{"question": "..."}` | Réponse + sources (top 3 fiches)    |
| `GET`   | `/stats`  | Obtenir le nombre de fiches dans la base        | -                           | JSON: `{"nombre_fiches": int}`      |
| `GET`   | `/`       | Informations sur l'API                          | -                           | Message d'accueil + endpoints       |
| `GET`   | `/docs`   | Documentation interactive Swagger               | -                           | Interface Swagger UI                |

---

## Variables d'environnement

**Fichier `.env` à la racine du projet** :

```bash
MISTRAL_API_KEY=votre_cle_api_mistral
```

**Note sur la persistance :** La base vectorielle ChromaDB est stockée dans `./chroma_db/` et persiste automatiquement entre les redémarrages (montée en volume Docker).
