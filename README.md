# P12_systeme_reco_agriculture
Système de recommandations pour une agriculture optimisée par les données
[![CI Pipeline](https://github.com/FabParis20/P12_systeme_reco_agriculture/actions/workflows/ci.yml/badge.svg)](https://github.com/FabParis20/P12_systeme_reco_agriculture/actions)

## 🚜 Système de Recommandation Agricole (P12)

Ce projet propose une solution industrialisée pour l'optimisation des rendements agricoles. Il s'appuie sur une **architecture hybride "Coupling"** (inspirée de *Shahhosseini et al., 2021*) pour prédire les rendements et recommander les cultures les plus adaptées selon des contraintes pédoclimatiques.

---

## 🌐 Accès aux Services Déployés

Le projet est disponible en ligne sans aucune installation requise. L'architecture est scindée en deux entités distinctes pour respecter les bonnes pratiques de développement logiciel.

* **💻 Interface Utilisateur (Frontend) :** [Interface de prédiction (Streamlit)](https://p12systemerecoagriculture-3nk8c55ydyym5mebpp98cr.streamlit.app/)  
    *Interface intuitive pour tester les prédictions de rendement et les recommandations de cultures.*
* **⚙️ API de Prédiction (Backend) :** [Moteur de calcul & Modèles (FastAPI)](https://api-agricole-fab.onrender.com/docs)  
    *Documentation interactive (Swagger) de l'API FastAPI.*
# 🚜 Système de Recommandation Agricole (Projet 12)

---

## 🏗️ Architecture Technique

Le système est conçu pour être robuste, testable et reproductible grâce à une stack MLOps moderne :

### 1. Intelligence Artificielle (Modèle Hybride)
La méthodologie repose sur l'intégration de simulations biophysiques dans l'apprentissage automatique :
* **Modèle "Teacher" (Random Forest) :** Prédit des indicateurs de stress intermédiaires ($Potential\_Yield$, indices de stress thermique et hydrique).
* **Modèle "Student" (XGBoost) :** Utilise les sorties du "Teacher" ainsi que les données historiques FAO pour fournir la prédiction finale de rendement.

### 2. Stack Logicielle
* **Backend :** FastAPI (Python 3.11).
* **Frontend :** Streamlit.
* **Conteneurisation :** Docker (image optimisée avec l'installateur `uv`).
* **CI/CD :** GitHub Actions (Tests unitaires `pytest` + Build Docker + Push vers GHCR).

---

## 🧪 Utilisation & Tests

### Mode Utilisateur (Web)
1.  Connectez-vous à l'interface **Streamlit**.
2.  Vérifiez le statut de l'API (Volet latéral : **Connecté 🟢**).
3.  Renseignez les paramètres de la parcelle (Pays, type de sol, culture).
4.  Consultez les résultats de rendement et les recommandations alternatives.

### Mode Développeur (Local)
Pour lancer l'ensemble de l'écosystème sur votre machine :

```bash
# 1. Récupérer l'image Docker de l'API (Backend)
docker pull ghcr.io/fabparis20/p12_systeme_reco_agriculture:latest

# 2. Lancer le conteneur Backend
docker run -p 8000:8000 ghcr.io/fabparis20/p12_systeme_reco_agriculture:latest

# 3. Lancer l'interface Frontend (nécessite Python)
pip install -r requirements.txt
streamlit run app.py
```
## 🛠️ Pipeline CI/CD

Le workflow **GitHub Actions** assure l'intégrité et la qualité du code à chaque modification poussée sur la branche `main` :

1.  **🧪 Linter & Tests :** Exécution automatisée des tests unitaires via `pytest` pour valider la logique métier et les endpoints de l'API.
2.  **🏗️ Build :** Si les tests sont au vert, construction d'une nouvelle image **Docker** optimisée (utilisant `uv` pour une gestion rapide des dépendances).
3.  **🚀 Deploy :** * **Registry :** Publication de l'image sur le **GitHub Container Registry (GHCR)**.
    * **Cloud :** Déploiement automatique du nouveau conteneur sur **Render** via un Webhook, assurant une mise à jour transparente du backend.