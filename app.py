import streamlit as st
import requests
import pandas as pd
import os

# --- CONFIGURATION ---
# Une seule variable pour tout le projet
# On cherche "API_URL" dans le système (Cloud). Si on ne trouve rien, on prend le localhost.
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

# Listes de choix pour nos menus déroulants
LISTE_CULTURES = ["Wheat", "Maize", "Rice", "Soybean"]
LISTE_SOLS = ["Sand", "Clay", "Loam", "Silt", "Peat"]

# Fonction pour récupérer dynamiquement les pays depuis l'API
@st.cache_data
def charger_pays():
    try:
        reponse = requests.get(f"{API_URL}/countries")
        if reponse.status_code == 200:
            return reponse.json()["data"]
    except requests.exceptions.ConnectionError:
        pass
    # Sécurité (Fallback) si l'API est éteinte au moment de lancer la page
    return ["Erreur de connexion à l'API"]

# On génère la liste dynamiquement
LISTE_PAYS = charger_pays()

st.set_page_config(page_title="AgriTech AI", page_icon="🌾", layout="centered")

# --- NAVIGATION ---
with st.sidebar:
    st.title("🚜 AgriTech AI")
    st.write("Outil d'Aide à la Décision")
    mode = st.radio("Choisissez votre mode :", ["🔮 Mode Prédiction", "🏆 Mode Recommandation"])
    st.markdown("---")
    st.info("API Status : Connectée 🟢")

# ==========================================
# ECRAN 1 : MODE PRÉDICTION
# ==========================================
if mode == "🔮 Mode Prédiction":
    st.title("Estimez votre rendement")
    st.write("Renseignez les caractéristiques de votre parcelle pour simuler la récolte.")

    # Création d'un formulaire pour regrouper les saisies
    with st.form("form_prediction"):
        col1, col2 = st.columns(2)
        with col1:
            pays = st.selectbox("Pays de la parcelle", LISTE_PAYS)
            culture = st.selectbox("Culture envisagée", LISTE_CULTURES)
        with col2:
            sol = st.selectbox("Type de sol", LISTE_SOLS)
            
        st.write("Pratiques agricoles :")
        # Les checkboxes renvoient True/False. En Python, int(True) = 1 et int(False) = 0 !
        engrais = st.checkbox("Utilisation d'engrais (Fertilizer)")
        irrigation = st.checkbox("Parcelle irriguée (Irrigation)")

        # Le bouton d'envoi du formulaire
        submit = st.form_submit_button("Lancer la simulation 🚀")

    if submit:
        # 1. Préparation du colis (Dictionnaire Python)
        payload = {
            "Area": pays,
            "Item": culture,
            "Soil_Type": sol,
            "Fertilizer_Used": int(engrais),
            "Irrigation_Used": int(irrigation)
        }
        # =======================================================================
        # 2. Envoi au serveur (API)
        with st.spinner("Analyse agronomique en cours..."):
            try:
                response = requests.post(f"{API_URL}/predict", json=payload)
                
                if response.status_code == 200:
                    json_res = response.json()
                    
                    # --- NOUVELLE LOGIQUE DE STATUT ---
                    if json_res.get("status") == "success":
                        resultat = json_res["data"]
                        st.success("Analyse terminée avec succès !")
                        
                        macro = resultat['rendement_macro_t_ha']
                        micro = resultat['rendement_ajuste_t_ha']
                        impact_pratiques = micro - macro
                        
                        col_res1, col_res2 = st.columns(2)
                        col_res1.metric(label="Rendement Base (Macro)", value=f"{macro:.2f} t/ha")
                        col_res2.metric(label="Rendement Ajusté (Micro)", value=f"{micro:.2f} t/ha", delta=f"{impact_pratiques:+.2f} t/ha")
                        
                        with st.expander("ℹ️ Comment interpréter ces chiffres ?"):

                            st.markdown("""
                            **🌍 Rendement Base (Macro) :** C'est le potentiel régional calculé par notre Intelligence Artificielle. Il se base sur le climat historique et la tendance technologique de votre pays.
                            
                            **🌱 Rendement Ajusté (Micro) :** C'est l'estimation finale sur-mesure pour votre parcelle. Notre système a appliqué des bonus ou malus agronomiques selon *vos* pratiques (qualité du sol, apport d'eau et de nutriments).
                            """)
                    elif json_res.get("status") == "no_data":
                        # Gestion propre du cas "Riz en Albanie"
                        st.warning("⚠️ Données insuffisantes")
                        st.info(f"**Message de l'expert :** {json_res.get('message')}")
                        st.write("Ce pays est répertorié, mais l'historique FAO pour cette culture spécifique est trop partiel pour permettre une prédiction fiable.")
                else:
                    st.error(f"Erreur API : {response.json().get('detail', 'Erreur inconnue')}")
            
            except requests.exceptions.ConnectionError:
                st.error("Impossible de contacter l'API. Vérifiez que Uvicorn tourne bien !")


# ==========================================
# ECRAN 2 : MODE RECOMMANDATION
# ==========================================
elif mode == "🏆 Mode Recommandation":
    st.title("Optimisez votre assolement")
    st.write("Décrivez votre parcelle, notre IA classera les cultures par rentabilité.")

    with st.form("form_recommandation"):
        col1, col2 = st.columns(2)
        with col1:
            pays = st.selectbox("Pays de la parcelle", LISTE_PAYS)
        with col2:
            sol = st.selectbox("Type de sol", LISTE_SOLS)
            
        st.write("Pratiques agricoles disponibles :")
        engrais = st.checkbox("Je peux utiliser de l'engrais")
        irrigation = st.checkbox("Ma parcelle est irrigable")

        submit = st.form_submit_button("Trouver la meilleure culture 🏆")

    if submit:
        # 1. Préparation du colis (SANS la culture !)
        payload = {
            "Area": pays,
            "Soil_Type": sol,
            "Fertilizer_Used": int(engrais),
            "Irrigation_Used": int(irrigation)
        }

        # 2. Envoi au serveur (API)
        with st.spinner("Simulation des scénarios en cours..."):
            try:
                response = requests.post(f"{API_URL}/recommend", json=payload)
                
                if response.status_code == 200:
                    json_res = response.json()

                    if json_res.get("status") == "success":
                        data = json_res["data"]
                        df_resultats = pd.DataFrame(data)
                        df_resultats.index += 1 
                        
                        st.success(f"La culture recommandée est le {df_resultats.iloc[0]['Culture_Recommandée']} !")
                        st.bar_chart(data=df_resultats, x="Culture_Recommandée", y="Rendement_Ajusté_t_ha", color="#2e7b32")
                        st.dataframe(df_resultats, use_container_width=True)
                        
                        # Petit conseil bonus si le tableau fait moins de 4 lignes
                        if len(df_resultats) < 4:
                            st.caption("Note : Certaines cultures ont été écartées par manque d'historique fiable pour ce pays.")

                    elif json_res.get("status") == "no_data":
                        st.error("❌ Recommandation impossible")
                        st.warning(json_res.get("message"))
                
                else:
                    st.error("Erreur serveur lors de la simulation.")
                    
            except requests.exceptions.ConnectionError:
                st.error("Impossible de contacter l'API. Vérifiez que Uvicorn tourne bien !")