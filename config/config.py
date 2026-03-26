
RANDOM_STATE = 54

# --- PARAMÈTRES DE FUSION (MATCHING FLOU) ---
# Ces seuils ont été déterminés dans le notebook '01_Preparation_Donnees.ipynb'.
# Ils sont basés sur la variabilité intra-groupe (écart-type) du dataset historique.

# Tolérance Pluie : Basée sur la règle 1/2 Sigma (Variabilité naturelle acceptée)
# Valeur calculée : ~260mm / 2
RAINFALL_TOLERANCE = 130  # mm

# Tolérance Température : Basée sur la règle 1/3 Sigma (Approche conservatrice pour stress thermique)
# Valeur calculée : ~7.2°C / 3
TEMP_TOLERANCE = 2.4      # °C