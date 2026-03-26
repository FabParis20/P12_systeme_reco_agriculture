# ==========================================
# 1. IMPORTATIONS ET INITIALISATION GLOBALE
# ==========================================
IMPORTER FastAPI
IMPORTER Pydantic (pour la validation des données)
IMPORTER pandas, joblib (pour lire les modèles)
IMPORTER tes_fonctions_metier (predict_single_crop, recommend_best_crop)

# CHARGEMENT EN MÉMOIRE (La règle d'or de performance)
# Exécuté UNE SEULE FOIS au démarrage du serveur
modele_prod <- CHARGER "modele_xgboost.pkl"
ref_table <- CHARGER "reference_climat.csv"
trend_table <- CHARGER "trend_reference.csv"
regles_metier <- CHARGER "business_rules.json"
# On extrait la liste des pays valides depuis notre table chargée en mémoire
LISTE_PAYS_VALIDES <- EXTRAIRE_PAYS(ref_table)


# ==========================================
# 2. LES SCHÉMAS DE VALIDATION (Pydantic)
# ==========================================
# C'est le "videur de la boîte de nuit". Il filtre automatiquement
# les mauvaises requêtes avant même qu'elles ne touchent ton modèle.

CLASSE RequetePrediction(Pydantic BaseModel):
    Area: Chaîne de caractères (Ex: "France")
    Item: Chaîne de caractères (Doit être limité à : "Wheat", "Maize", "Rice", "Soybean")
    Soil_Type: Chaîne de caractères
    Fertilizer_Used: Entier (0 ou 1)
    Irrigation_Used: Entier (0 ou 1)

    # Le garde du corps dynamique pour les pays
    VALIDATEUR_POUR(Area):
        SI Area N'EST PAS DANS LISTE_PAYS_VALIDES:
            DÉCLENCHER ERREUR ("Pays inconnu ou non supporté par le modèle")
        RETOURNER Area

CLASSE RequeteRecommandation(Pydantic BaseModel):
    # Identique à la prédiction, MAIS SANS LA CULTURE !
    Area: Chaîne de caractères
    Soil_Type: Chaîne de caractères
    Fertilizer_Used: Entier (0 ou 1)
    Irrigation_Used: Entier (0 ou 1)


# ==========================================
# 3. CRÉATION DE L'APPLICATION
# ==========================================
app <- INITIALISER FastAPI(titre="API AgriTech MVP")


# ==========================================
# 4. LES ROUTES (Endpoints)
# ==========================================

# --- Route de test (Health Check) ---
ROUTE GET "/":
    RETOURNER {"message": "L'API AgriTech est en ligne et le modèle est chargé."}

# --- Route 1 : La Prédiction ---
ROUTE POST "/predict":
    PARAMÈTRE D'ENTRÉE : requete de type RequetePrediction
    
    // Si le code arrive ici, c'est que Pydantic a déjà validé que les données sont parfaites !
    dict_user <- CONVERTIR requete EN dictionnaire Python
    
    ESSAYER :
        resultat <- APPELER predict_single_crop(dict_user, modele_prod, ref_table, trend_table)
        RETOURNER resultat (format JSON)
        
    EN CAS D'ERREUR INTERNE :
        RETOURNER Erreur HTTP 500 ("Erreur lors du calcul du rendement")

# --- Route 2 : La Recommandation ---
ROUTE POST "/recommend":
    PARAMÈTRE D'ENTRÉE : requete de type RequeteRecommandation
    
    dict_user_base <- CONVERTIR requete EN dictionnaire Python
    
    ESSAYER :
        dataframe_resultat <- APPELER recommend_best_crop(dict_user_base, modele_prod, ref_table, trend_table)
        
        # Les API web communiquent en JSON, pas en DataFrame Pandas
        json_resultat <- CONVERTIR dataframe_resultat EN dictionnaire
        RETOURNER json_resultat
        
    EN CAS D'ERREUR INTERNE :
        RETOURNER Erreur HTTP 500 ("Erreur lors de la génération des recommandations")