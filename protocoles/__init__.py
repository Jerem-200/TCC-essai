# Import des données depuis les fichiers voisins
from .barlow import PROTOCOLE_BARLOW, QUESTIONS_HEBDO as Q_BARLOW
from .estime import PROTOCOLE_ESTIME, QUESTIONS_HEBDO as Q_ESTIME

# CATALOGUE CENTRALISÉ
# La clé (ex: "barlow") est celle qui sera stockée dans Google Sheet et la Base de données
CATALOGUE = {
    "barlow": {
        "nom": "TCC Troubles Émotionnels (Barlow)",
        "description": "Protocole unifié pour la prise en charge de l'anxiété et des troubles de l'humeur.",
        "modules": PROTOCOLE_BARLOW,
        "questions": Q_BARLOW
    },
    "estime": {
        "nom": "Thérapie Estime de Soi",
        "description": "Programme cognitif pour renforcer l'estime de soi et réduire l'autocritique.",
        "modules": PROTOCOLE_ESTIME,
        "questions": Q_ESTIME
    }
}

def get_liste_protocoles():
    """Retourne la liste des codes disponibles (ex: ['barlow', 'estime'])"""
    return list(CATALOGUE.keys())

def get_info_protocole(code):
    """Retourne les infos générales (Nom, Description)"""
    if code in CATALOGUE:
        return CATALOGUE[code]
    return CATALOGUE["barlow"] # Fallback par défaut