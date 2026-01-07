# Configuration pour le futur protocole Estime de Soi

# 1. Questionnaire Hebdo spécifique (ou vide si pas encore défini)
QUESTIONS_HEBDO = {
    "Estime": {
        "titre": "Échelle d'Estime de Soi (Rosenberg)",
        "description": "Évaluez votre accord avec les affirmations suivantes.",
        "type": "scale_0_8", # Exemple
        "questions": [
            "Je suis satisfait de moi-même.",
            "Je pense que j'ai un certain nombre de qualités."
        ]
    }
}

# 2. Le contenu des modules
PROTOCOLE_ESTIME = {
    "module0": {
        "titre": "Module 0 : Introduction à l'Estime de Soi",
        "objectifs": "Comprendre les piliers de l'estime de soi.",
        "outils": "Fiche piliers",
        "pdfs_module": [],
        "examen_devoirs": [],
        "etapes_seance": [
            {"titre": "Accueil et présentation", "details": "...", "pdfs": []}
        ],
        "exercices": [],
        "taches_domicile": []
    },
    "module1": {
        "titre": "Module 1 : L'autocritique",
        "objectifs": "Identifier le critique intérieur.",
        "outils": "Journal autocritique",
        "pdfs_module": [],
        "examen_devoirs": [],
        "etapes_seance": [],
        "taches_domicile": []
    }
}