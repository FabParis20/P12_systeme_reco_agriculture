# 1. Image de base officielle Python (légère)
FROM python:3.11-slim

# 2. Définition du dossier de travail dans le conteneur
WORKDIR /app

# 3. Copie du fichier de dépendances (celui que tu viens de générer !)
COPY requirements-api.txt .

# 4. Installation des dépendances
# On utilise no-cache-dir pour que l'image soit la plus légère possible
RUN pip install --no-cache-dir -r requirements-api.txt

# 5. Copie de tout ton code source dans le conteneur
# (On copie les dossiers api, config, data, models...)
COPY . .

# 6. Exposition du port sur lequel l'API va écouter
EXPOSE 8000

# 7. La commande pour lancer le serveur (identique à celle que tu tapes dans ton terminal)
# On utilise 0.0.0.0 pour dire au serveur d'accepter les connexions venant de l'extérieur du conteneur
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]