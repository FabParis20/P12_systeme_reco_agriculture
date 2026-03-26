import pandas as pd
import json
import numpy as np # (Par sécurité, souvent utile avec Pandas)
from config.paths import DONNEES_PROCESSED

# 1. PARAMÈTRES AGRONOMIQUES FAO
CROP_PARAMS = {
    'Wheat':   {'rain_opt': 550,  'temp_opt_min': 15, 'temp_opt_max': 25, 'temp_crit': 30},
    'Maize':   {'rain_opt': 650,  'temp_opt_min': 20, 'temp_opt_max': 30, 'temp_crit': 35},
    'Rice':    {'rain_opt': 1000, 'temp_opt_min': 22, 'temp_opt_max': 32, 'temp_crit': 36},
    'Soybean': {'rain_opt': 500,  'temp_opt_min': 20, 'temp_opt_max': 30, 'temp_crit': 35}
}

# 2. FONCTION DE CALCUL DES STRESS
def calculate_agronomic_stress(row):
    """Calcule le Water Stress et Heat Stress pour une ligne donnée."""
    crop = row.get('Item')
    rain = row.get('average_rain_fall_mm_per_year')
    temp = row.get('avg_temp')

    if pd.isna(rain) or pd.isna(temp) or crop not in CROP_PARAMS:
        return pd.Series([0.0, 0.0], index=['Water_Stress', 'Heat_Stress'])

    params = CROP_PARAMS[crop]

    # Water Stress
    delta_rain = rain - params['rain_opt']
    if delta_rain < 0:
        w_stress = abs(delta_rain) / params['rain_opt']
    else:
        w_stress = (delta_rain / params['rain_opt']) * 0.5
    w_stress = min(w_stress, 1.0)

    # Heat Stress
    h_stress = 0.0
    if temp < params['temp_opt_min']:
        h_stress = (params['temp_opt_min'] - temp) / 10
    elif temp > params['temp_opt_max']:
        h_stress = (temp - params['temp_opt_max']) / 10
        if temp > params['temp_crit']:
            h_stress *= 2.0
    h_stress = min(h_stress, 1.0)

    return pd.Series([w_stress, h_stress], index=['Water_Stress', 'Heat_Stress'])

# 1. Chargement de l'artefact généré dans le Notebook 02
chemin_regles = DONNEES_PROCESSED / 'business_rules.json'
with open(chemin_regles, 'r', encoding='utf-8') as f:
    business_rules = json.load(f)

print("✅ Règles métier (business_rules.json) chargées avec succès.")

# 3. La nouvelle fonction hybride
def appliquer_bonus_malus_retro(rendement_base_hg_ha, type_sol, irrigation_used, fertilizer_used):
    """
    Applique les coefficients additifs issus de la rétro-ingénierie (Notebook 02).
    """
    # Étape A : Conversion de la prédiction FAO (hg/ha) en Tonnes/ha
    rendement_final_t_ha = rendement_base_hg_ha / 10000
    # Étape B : Application des pratiques agricoles
    if fertilizer_used == 1:
        rendement_final_t_ha += business_rules.get('Fertilizer_Used', 0)
    if irrigation_used == 1:
        rendement_final_t_ha += business_rules.get('Irrigation_Used', 0)

    # Étape C : Application de l'impact du sol
    # Le JSON contient des clés du type "Soil_Type_Clay"
    cle_sol = f"Soil_Type_{type_sol}"
    if cle_sol in business_rules:
        rendement_final_t_ha += business_rules[cle_sol]
    return round(rendement_final_t_ha, 2)

# 4. Fonction de prédiction
ANNEE_SIMULATION = 2014

def predict_single_crop(dict_user, modele, ref_table, trend_table):
    """Pipeline complet d'inférence (Data Prep -> ML -> Post-Processing)."""
    
    # --- 1. ENRICHISSEMENT MACRO ---
    pays = dict_user["Area"]
    culture = dict_user["Item"]
    
    # Récupération météo
    meteo_pays = ref_table[ref_table['Area'] == pays].iloc[0]
    
    # Récupération de la tendance technologique (2013 pour simuler 2014)
    filtre_trend = (trend_table['Area'] == pays) & (trend_table['Item'] == culture)
    tendance_tech = trend_table[filtre_trend]['yield_trend'].values[0]
    
    # Création du dictionnaire compatible avec l'entraînement
    dict_ml = {
        'Area': pays,
        'Item': culture,
        'Year': ANNEE_SIMULATION,
        'average_rain_fall_mm_per_year': meteo_pays['average_rain_fall_mm_per_year'],
        'avg_temp': meteo_pays['avg_temp'],
        'pesticides_tonnes': meteo_pays['pesticides_tonnes'],
        'yield_trend': tendance_tech # Ajout de la variable manquante !
    }
    
    # --- 2. TRANSFORMATION ---
    X_data_user = pd.DataFrame([dict_ml])
    
    # --- 3. FEATURE ENGINEERING ---
    # A. Ajout des stress agronomiques
    stress_cols = X_data_user.apply(calculate_agronomic_stress, axis=1)
    X_data_user = pd.concat([X_data_user, stress_cols], axis=1)
    
    # B. Ajout de l'Indice d'Aridité de De Martonne (manquant !)
    X_data_user['Aridity_Index'] = X_data_user['average_rain_fall_mm_per_year'] / (X_data_user['avg_temp'] + 10)
    
    # --- 4. PRÉDICTION ML (Macro) ---
    rendement_base_hg_ha = modele.predict(X_data_user)[0]
    
    # --- 5. POST-PROCESSING (Micro) ---
    rendement_final_t_ha = appliquer_bonus_malus_retro(
        rendement_base_hg_ha=rendement_base_hg_ha,
        type_sol=dict_user["Soil_Type"],
        irrigation_used=dict_user["Irrigation_Used"],
        fertilizer_used=dict_user["Fertilizer_Used"]
    )
    
    return {
        "rendement_macro_t_ha": float(round(rendement_base_hg_ha / 10000, 2)),
        "rendement_ajuste_t_ha": float(rendement_final_t_ha)
    }

# 5. Fonction de recommandation
def recommend_best_crop(dict_user_base, modele, ref_table, trend_table):
    """
    Simule le rendement pour toutes les cultures et recommande la plus performante.
    """
    # 1. Définition de l'espace de recherche
    liste_cultures = ['Wheat', 'Maize', 'Rice', 'Soybean']
    
    # 2. Création d'une LISTE vide (et non d'un DataFrame) pour les performances
    resultats_simulation = []
    
    # 3. La boucle d'évaluation
    for culture in liste_cultures:
        # On fait une copie du dictionnaire utilisateur pour ne pas écraser l'original
        dict_simulation = dict_user_base.copy()
        
        # On injecte la culture en cours de test
        dict_simulation["Item"] = culture
        
        # On appelle notre orchestrateur
        prediction = predict_single_crop(
            dict_user=dict_simulation,
            modele=modele,
            ref_table=ref_table,
            trend_table=trend_table
        )
        
        # On stocke le résultat dans un dictionnaire temporaire
        resultats_simulation.append({
            "Culture_Recommandée": culture,
            "Rendement_Macro_t_ha": prediction["rendement_macro_t_ha"],
            "Rendement_Ajusté_t_ha": prediction["rendement_ajuste_t_ha"]
        })
        
    # 4. Conversion finale en DataFrame et Tri décroissant
    df_recommandations = pd.DataFrame(resultats_simulation)
    df_recommandations = df_recommandations.sort_values(by="Rendement_Ajusté_t_ha", ascending=False)
    
    # On reset l'index pour que le classement soit propre (1er, 2ème, etc.)
    df_recommandations = df_recommandations.reset_index(drop=True)
    df_recommandations.index += 1 # Pour que l'index commence à 1
    
    return df_recommandations
