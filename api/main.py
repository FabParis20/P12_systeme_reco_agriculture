from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator
from typing import Literal
import pandas as pd
import joblib
import json
from api.services import predict_single_crop, recommend_best_crop

# 1. Importation de tes chemins absolus (config.paths)
from config.paths import DOSSIER_MODELES, DONNEES_PROCESSED

# 2. Importation de tes fonctions métier (à créer dans un fichier services.py par exemple)
# from services import predict_single_crop, recommend_best_crop

# ==========================================
# INITIALISATION GLOBALE (Au démarrage)
# ==========================================
print("⏳ Démarrage du serveur et chargement des artefacts en mémoire...")

try:
    # Chargement du modèle ML
    path_model = DOSSIER_MODELES / "pipeline_champion_xgb.pkl"
    modele_prod = joblib.load(path_model)

    # Chargement des tables de référence
    path_climat = DOSSIER_MODELES / "reference_climat.csv"
    ref_table = pd.read_csv(path_climat)
    
    path_trend = DOSSIER_MODELES / "trend_reference.csv"
    trend_table = pd.read_csv(path_trend)

    # Chargement des règles métier
    path_rules = DONNEES_PROCESSED / "business_rules.json"
    with open(path_rules, 'r', encoding='utf-8') as f:
        business_rules = json.load(f)

    # Extraction dynamique de la liste des pays valides (La Source de Vérité)
    LISTE_PAYS_VALIDES = ref_table['Area'].unique().tolist()
    
    print(f"✅ Artefacts chargés avec succès. {len(LISTE_PAYS_VALIDES)} pays reconnus.")

except Exception as e:
    print(f"❌ Erreur critique lors du chargement des artefacts : {e}")
    # En production, on arrêterait le serveur ici si les modèles manquent.

# ==========================================
# SCHÉMAS DE VALIDATION (Pydantic)
# ==========================================

class RequeteBase(BaseModel):
    """Schéma de base contenant les caractéristiques communes de la parcelle."""
    Area: str
    Soil_Type: str
    Fertilizer_Used: int  # Attendu: 0 ou 1
    Irrigation_Used: int  # Attendu: 0 ou 1

    @field_validator('Area')
    def verifier_pays(cls, pays_saisi):
        """Vérification validité pays."""
        if pays_saisi not in LISTE_PAYS_VALIDES:
            raise ValueError(f"Pays non reconnu : '{pays_saisi}'. Veuillez choisir un pays supporté par la FAO.")
        return pays_saisi

    @field_validator('Fertilizer_Used', 'Irrigation_Used')
    def verifier_booleen(cls, valeur):
        """S'assure que l'utilisateur n'envoie pas '2' ou '3'."""
        if valeur not in [0, 1]:
            raise ValueError("Cette valeur doit être strictement 0 (Non) ou 1 (Oui).")
        return valeur

class RequetePrediction(RequeteBase):
    """Hérite de la base, mais ajoute la culture (statique)."""
    Item: Literal["Wheat", "Maize", "Rice", "Soybean"]

class RequeteRecommandation(RequeteBase):
    """Hérite de la base. Pas besoin d'ajouter 'Item' ici !"""
    pass

# ==========================================
# CRÉATION DE L'APPLICATION FASTAPI
# ==========================================
app = FastAPI(
    title="AgriTech Predictor API",
    description="API de prédiction et de recommandation de rendements agricoles.",
    version="1.0.0"
)

# ==========================================
# ROUTES (Endpoints)
# ==========================================

@app.get("/")
def health_check():
    """Vérifie que l'API est bien en ligne."""
    return {"status": "success", "message": "L'API AgriTech est opérationnelle 🚜"}

@app.post("/predict")
def predict_yield(requete: RequetePrediction):
    """Endpoint pour estimer le rendement d'une culture spécifique."""
    # Conversion de l'objet Pydantic en dictionnaire pour nos fonctions métier
    dict_user = requete.model_dump()
    
    try:
        resultat = predict_single_crop(dict_user, modele_prod, ref_table, trend_table)
             
        return {"status": "success", "data": resultat}
        
    except Exception as e:
        # On capture l'erreur Python interne et on la renvoie proprement en HTTP 500
        raise HTTPException(status_code=500, detail=f"Erreur interne lors de la prédiction : {str(e)}")

@app.post("/recommend")
def recommend_crops(requete: RequeteRecommandation):
    """Endpoint pour recommander la meilleure culture selon la parcelle."""
    dict_user_base = requete.model_dump()
    
    try:
        resultat_df = recommend_best_crop(dict_user_base, modele_prod, ref_table, trend_table)
        # On transforme le DataFrame Pandas en liste de dictionnaires JSON pour le web
        json_resultat = resultat_df.to_dict(orient='records')
                        
        return {"status": "success", "data": json_resultat}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne lors de la recommandation : {str(e)}")
    
@app.get("/countries")
def get_countries():
    """Endpoint pour fournir la liste des pays supportés au Frontend."""
    try:
        # On renvoie la liste triée par ordre alphabétique pour une meilleure UX
        pays_tries = sorted(LISTE_PAYS_VALIDES)
        return {"status": "success", "data": pays_tries}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Impossible de charger les pays.")