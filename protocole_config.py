PROTOCOLE_BARLOW = {
    # ... (Module intro, Module 1...)

    "module2": {
        "titre": "Module 2 : Comprendre les émotions",
        "description": "Identifier les composantes de vos réactions.",
        "etapes": [
            {
                "nom": "La vague émotionnelle (Psychoéducation)",
                "type": "text",
                "contenu": "Les émotions sont des signaux..." 
            },
            # 👇 C'EST ICI QUE VOUS AJOUTEZ VOTRE FICHIER 👇
            {
                "nom": "Fiche : Émotions Négatives & Aversion",
                "type": "pdf",
                "fichier": "assets/fiche_emotions_negatives.pdf" # Le chemin exact
            },
            # 👆 FIN DE L'AJOUT 👆
            {
                "nom": "Suivi de l'humeur (PHQ-9)",
                "type": "outil",
                "lien": "pages/15_Echelle_PHQ9.py",
                "icon": "📉"
            }
        ]
    },
    
    # ... (La suite)
}