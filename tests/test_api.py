from fastapi.testclient import TestClient
from api.main import app
# Code de test qui va simuler un user de streamlit, qui lit les dictionnaires Python renvoyés par FastAPI, et qui utilise des assert pour vérifier que chaque variable est exactement à sa place, avec la bonne valeur.

# Création du client de test. Permet de tester des applications FastAPI sans créer de véritable connexion HTTP et socket, en communiquant directement avec le code FastAPI.
client = TestClient(app)

def test_get_countries_success():
    """Test 1 : Vérifier que l'API renvoie bien une liste de pays"""
    response = client.get("/countries")

    print("\n--- CE QUE CONTIENT L'OBJET RESPONSE ---")
    print(response) 
    
    print("\n--- CE QUE CONTIENT LE TEXTE BRUT (JSON) ---")
    print(response.text)
    print("Type de la variable :", type(response.text))
    
    print("\n--- APRES LA TRADUCTION .json() ---")
    data = response.json()
    print(data)
    print("Type de la variable :", type(data))
    print("----------------------------------------\n")

    # On affirme (assert) que le code de statut HTTP est 200 (OK)
    assert response.status_code == 200

    # On affirme que la réponse contient bien la clé "data"
    data = response.json()
    # Cette ligne extrait le corps de la réponse HTTP. Comme les API communiquent universellement via des chaînes de caractères au format JSON, on utilise la méthode .json(). Cette méthode agit comme un parseur (un traducteur) : elle lit ce texte JSON brut et le convertit automatiquement en un objet natif Python, ici un dictionnaire, pour pouvoir ensuite manipuler facilement ses clés avec les asserts.
    assert "data" in data

    # On affirme que "France" est bien dans la base de données
    assert "France" in data["data"]


def test_predict_success():
    """Test 2 : Vérifier qu'une prédiction valide fonctionne et renvoie des rendements"""
    payload = {
        "Area": "France",
        "Item": "Wheat",
        "Soil_Type": "Loam",
        "Fertilizer_Used": 1,
        "Irrigation_Used": 0
    }

    response = client.post("/predict", json=payload)

    assert response.status_code == 200
    resultat = response.json()

    # On vérifie la structure de la réponse du modèle
    assert "data" in resultat
    assert "rendement_macro_t_ha" in resultat["data"]
    assert "rendement_ajuste_t_ha" in resultat["data"]

    # On vérifie que le rendement est bien un chiffre positif (logique métier)
    assert resultat["data"]["rendement_macro_t_ha"] >= 0


def test_predict_invalid_country():
    """Test 3 : Vérifier que Pydantic bloque les données aberrantes"""
    payload = {
        "Area": "PaysImaginaire", # Ce pays n'est pas dans nos règles métiers/FAO
        "Item": "Wheat",
        "Soil_Type": "Loam",
        "Fertilizer_Used": 1,
        "Irrigation_Used": 0
    }

    response = client.post("/predict", json=payload)

    # Le statut attendu n'est PAS 200
    # FastAPI/Pydantic devrait renvoyer une erreur 422 (Unprocessable Entity) ou 400.
    assert response.status_code == 422

def test_recommend_success():
    """Test 4 : Vérifier que le système de recommandation renvoie un classement valide"""
    # 1. Le payload SANS la culture ("Item")
    payload = {
        "Area": "France",
        "Soil_Type": "Loam",
        "Fertilizer_Used": 1,
        "Irrigation_Used": 0
    }
    
    # 2. L'envoi à la bonne route
    response = client.post("/recommend", json=payload)
    
    # 3. Les vérifications (Assserts)
    assert response.status_code == 200
    resultat = response.json()
    
    assert "data" in resultat
    
    # On vérifie que la donnée renvoyée est bien une liste (le top des cultures)
    liste_recommandations = resultat["data"]
    assert isinstance(liste_recommandations, list)
    
    # On vérifie que la liste n'est pas vide
    assert len(liste_recommandations) > 0
    
    # On vérifie que le premier élément du top contient bien la clé attendue par Streamlit
    premier_choix = liste_recommandations[0]
    assert "Culture_Recommandée" in premier_choix
    assert "Rendement_Ajusté_t_ha" in premier_choix