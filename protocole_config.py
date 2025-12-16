# Ce fichier contient la STRUCTURE du protocole. 
# C'est le seul fichier à modifier si vous changez de méthode plus tard.

PROTOCOLE_BARLOW = {
    "intro": {
        "titre": "0. Introduction & Analyse",
        "description": "Comprendre le fonctionnement de vos émotions.",
        "etapes": [
            {
                "nom": "Démarche qualité",
                "type": "pdf", 
                "fichier": "assets/demarche_qualite.pdf"
            },
            {
                "nom": "L'analyse fonctionnelle (SORC)",
                "type": "outil",
                "lien": "pages/12_Analyse_SORC.py",
                "icon": "🔍"
            }
        ]
    },
    "module1": {
        "titre": "Module 1 : Motivation",
        "description": "Fixer des objectifs et maintenir la motivation.",
        "etapes": [
            {
                "nom": "Comprendre l'ambivalence",
                "type": "pdf",
                "fichier": "assets/module1_fiche.pdf"
            },
            {
                "nom": "Balance Décisionnelle",
                "type": "outil",
                "lien": "pages/11_Balance_Decisionnelle.py",
                "icon": "⚖️"
            }
        ]
    },
    "module2": {
        "titre": "Module 2 : Comprendre les émotions",
        "description": "Identifier les composantes de vos réactions émotionnelles.",
        "etapes": [
            {
                "nom": "La vague émotionnelle (Psychoéducation)",
                "type": "text",
                "contenu": "Les émotions sont comme des vagues..." # Vous pourrez mettre le texte de Graziani ici
            },
            {
                "nom": "Suivi de l'humeur (BDI/PHQ-9)",
                "type": "outil",
                "lien": "pages/15_Echelle_PHQ9.py",
                "icon": "📉"
            }
        ]
    },
    "module3": {
        "titre": "Module 3 : Pleine Conscience",
        "description": "Observer sans juger.",
        "etapes": [
            {
                "nom": "Exercice de Relaxation",
                "type": "outil",
                "lien": "pages/07_Relaxation.py",
                "icon": "🧘"
            }
        ]
    },
    "module4": {
        "titre": "Module 4 : Flexibilité Cognitive",
        "description": "Assouplir nos pensées rigides.",
        "etapes": [
            {
                "nom": "Les distorsions cognitives (Fiche)",
                "type": "pdf",
                "fichier": "assets/module4_distorsions.pdf"
            },
            {
                "nom": "Colonnes de Beck",
                "type": "outil",
                "lien": "pages/01_Colonnes_Beck.py",
                "icon": "🧩"
            }
        ]
    },
    "module7": {
        "titre": "Module 7 : Expositions",
        "description": "Affronter pour mieux vivre.",
        "etapes": [
             {
                "nom": "Planifier une exposition",
                "type": "outil",
                "lien": "pages/09_Exposition.py",
                "icon": "🧗"
            }
        ]
    }
    # ... Vous pourrez ajouter les modules 5, 6 et 8 sur le même modèle
}