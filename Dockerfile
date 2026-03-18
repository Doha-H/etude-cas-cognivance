# image de base légère avec python 3.12
FROM python:3.12-slim

# installation de ffmpeg pour le traitement audio
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# dossier de travail dans le conteneur
WORKDIR /app

# on installe les dépendances en premier pour optimiser le cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# on copie le reste du projet
COPY . .

# port utilisé par streamlit
EXPOSE 8501

# lancement de l'application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]