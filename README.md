# P12_systeme_reco_agriculture
Système de recommandations pour une agriculture optimisée par les données
[![CI Pipeline](https://github.com/FabParis20/P12_systeme_reco_agriculture/actions/workflows/ci.yml/badge.svg)](https://github.com/FabParis20/P12_systeme_reco_agriculture/actions)

## 🚀 Accès Rapide au Projet

Le projet est entièrement déployé sur le Cloud pour une consultation immédiate sans installation locale.

* **💻 Interface Utilisateur (Frontend) :** [Lien vers ton app Streamlit Cloud](https://share.streamlit.io/...)  
    *Interface intuitive pour tester les prédictions de rendement et les recommandations de cultures.*
* **⚙️ API de Prédiction (Backend) :** [Lien vers ton API Render](https://api-agricole-fab.onrender.com/docs)  
    *Documentation interactive (Swagger) de l'API FastAPI.*

### 🏗️ Architecture du Déploiement
Le système repose sur une architecture découplée pour garantir la scalabilité et la maintenance :
1. **Backend (FastAPI) :** Packagé dans un conteneur **Docker** et hébergé sur **Render**. Il contient le modèle de Machine Learning et la logique métier.
2. **Frontend (Streamlit) :** Hébergé sur **Streamlit Community Cloud**, il communique avec l'API via des requêtes sécurisées.
3. **CI/CD (GitHub Actions) :** Automatisation complète des tests unitaires (Pytest) et de la mise à jour de l'image Docker sur le **GitHub Container Registry (GHCR)**.