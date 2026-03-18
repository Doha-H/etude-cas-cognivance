# Le scribe du technicien : pipeline IA de maintenance

Ce projet est un prototype de capture de savoir-faire industriel. Il permet de transformer un enregistrement audio brut en une fiche technique structurée et offre un assistant intelligent (**RAG**) pour interroger le contenu.

## Description du pipeline

L'application suit un flux de traitement en trois étapes :

1. **Transcription brute :** Utilisation du modèle **Whisper** pour convertir l'audio bruité en texte.
2. **Structuration par LLM :** Traitement du texte par **Mistral AI** pour corriger les termes techniques et générer une fiche de maintenance propre.
3. **Assistant RAG :** Mise en place d'un système de recherche augmentée pour répondre aux questions spécifiques sur l'intervention.

## Pile technologique

| Composant                 | Technologie        |
| :------------------------ | :----------------- |
| Interface                 | **Streamlit**      |
| Traitement audio          | **FFmpeg**         |
| Transcription             | **OpenAI Whisper** |
| Intelligence artificielle | **Mistral-Large**  |
| Conteneurisation          | **Docker**         |

## Installation et déploiement

Le projet est entièrement dockérisé pour garantir une installation simple et rapide.

### Prérequis

- **Docker** et **Docker Compose** installés sur la machine.
- Une clé **API Mistral AI**.

### Configuration

1. Créez un fichier `.env` à la racine du projet.
2. Ajoutez votre clé comme suit :

   ```text
   MISTRAL_API_KEY=votre_cle_ici
   ```

## Lancement

Pour démarrer l'application, exécutez la commande suivante dans votre terminal :

```bash
docker compose up --build
```

Une fois le conteneur lancé, l'interface est accessible sur votre navigateur à l'adresse : http://localhost:8501.

## Structure du projet

- **app.py** : code principal de l'application Streamlit
- **Dockerfile** : configuration de l'image Docker
- **docker-compose.yml** : orchestration des services et gestion des variables d'environnement
- **requirements.txt** : liste des dépendances Python
- **.env** : fichier contenant la clé API (exclu du suivi Git)
- **.gitignore** : liste des fichiers et dossiers à ignorer par Git
