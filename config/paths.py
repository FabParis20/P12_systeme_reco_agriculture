from pathlib import Path

RACINE_PROJET = Path(__file__).resolve().parent.parent
DONNEES_HISTORIQUES = RACINE_PROJET / "data" / "raw" / "agriculture_crop_yield"
DONNEES_AGRO_CLIMATIQUES = RACINE_PROJET / "data" / "raw" / "crop_yield_prediction_dataset"
