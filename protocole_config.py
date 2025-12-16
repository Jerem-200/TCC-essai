# ==============================================================================
# CONFIGURATION DU PROTOCOLE UNIFIÉ (BARLOW)
# ==============================================================================

PROTOCOLE_BARLOW = {
    "module0": {
        "titre": "Module 0 : Analyse fonctionnelle",
        "description": "Comprendre l'anxiété et conceptualiser le problème.",
        "fichiers_patient": [
            {"nom": "Échelle d'anxiété", "fichier": "assets/Echelle_d'anxiété.pdf"},
            {"nom": "Échelle de dépression", "fichier": "assets/Echelle_de_dépression.pdf"},
            {"nom": "Fiche des Progrès", "fichier": "assets/MODAF05_Fiche_des_Progrès.pdf"},
        ],
        "taches_therapeute": [
            "Faire en séance : Questions Émotions négatives & Aversion (ModAF)",
            "Après séance : Remplir la Fiche de conceptualisation (MODAF10)"
        ],
        "fichiers_therapeute": [
            "assets/L'analyse_fonctionnelle.pdf",
            "assets/MODAF10_Exemple_de_Fiche_de_conceptualisation_thérapeute.pdf"
        ]
    },

    "module1": {
        "titre": "Module 1 : Motivation & Objectifs",
        "description": "Fixer des objectifs et maintenir la motivation.",
        "fichiers_patient": [
            {"nom": "Fiche Objectifs du traitement", "fichier": "assets/MOD1.10_Fiche_Objectifs_du_traitement.pdf"},
            {"nom": "Exemple Objectifs", "fichier": "assets/Mod1.11_Fiche_Objectifs_du_traitement_EXEMPLE.pdf"},
            {"nom": "Balance Motivationnelle", "fichier": "assets/MOD1.20_Fiche_balance_motivationnelle.pdf"},
        ],
        "taches_therapeute": [
            "En séance : Remplir Fiche Objectifs (MOD1.10)",
            "En séance : Remplir Balance Motivationnelle (MOD1.20)"
        ],
        "devoirs_patient": [
            "Relire les objectifs et la balance",
            "Remplir les échelles (Anxiété, Dépression, Émotions)"
        ],
        "fichiers_therapeute": [
            "assets/Module_1_Fixer_des_objectifs_et_maintenir_la_motivation.pdf"
        ]
    },

    "module2": {
        "titre": "Module 2 : Comprendre les émotions",
        "description": "Le modèle à 3 composantes et l'ARC émotionnel.",
        "fichiers_patient": [
            {"nom": "Modèle à 3 composantes", "fichier": "assets/MOD2.1 Fiche_Modèle_à_trois_composantes_de_l'Emotion.pdf"},
            {"nom": "Suivre mon ARC émotionnel", "fichier": "assets/MOD2.2_Fiche_suivre_mon_ARC_émotionnel.pdf"},
        ],
        "taches_therapeute": [
            "Revoir : Objectifs et Balance (Module 1)",
            "En séance : Expliquer le modèle à 3 composantes",
            "En séance : Pratiquer l'ARC émotionnel"
        ],
        "devoirs_patient": [
            "Remplir fiche ARC émotionnel",
            "Remplir les échelles hebdomadaires"
        ],
        "fichiers_therapeute": [
            "assets/Antécédents_émotions.pdf"
        ]
    },

    "module3": {
        "titre": "Module 3 : Pleine Conscience",
        "description": "Observer ses émotions sans juger.",
        "fichiers_patient": [
            {"nom": "Fiche Pleine Conscience", "fichier": "assets/MOD3_Fiche_Pleine_Conscience_des_émotions.pdf"},
            {"nom": "Exemple Pleine Conscience", "fichier": "assets/MOD3_Exemple_Fiche_Pleine_Conscience_des_émotions.pdf"},
            {"nom": "🎧 Audio Méditation (MP3)", "fichier": "assets/Audio_Méditation.mp3", "type": "audio"},
            {"nom": "🎧 Audio Ancrage (MP3)", "fichier": "assets/Audio_Ancrage.mp3", "type": "audio"},
        ],
        "taches_therapeute": [
            "Revoir : ARC émotionnel (Module 2)",
            "En séance : Faire l'initiation à la méditation",
            "En séance : Faire l'exercice d'Ancrage"
        ],
        "devoirs_patient": [
            "Pratiquer avec les audios MP3",
            "Remplir fiche Pleine Conscience",
            "Semaine 2 : Focus sur l'Ancrage"
        ],
        "fichiers_therapeute": [
            "assets/MOD_3_Script_Méditation_d'initiation.pdf",
            "assets/MOD_3_Script_Méditation_Ancrage.pdf"
        ]
    },

    "module4": {
        "titre": "Module 4 : Flexibilité Cognitive",
        "description": "Assouplir ses pensées (Image ambiguë, Flèche descendante).",
        "fichiers_patient": [
            {"nom": "Exercice Image Ambiguë", "fichier": "assets/MOD4.1_Fiche_Exercice_Image_ambiguë.pdf"},
            {"nom": "Pratiquer la flexibilité", "fichier": "assets/MOD4.20_Fiche_Pratiquer_la_flexibilité_cognitive.pdf"},
            {"nom": "Exemple Flexibilité", "fichier": "assets/MOD4.21_Exemple_Fiche_Pratiquer_la_flexibilité_cognitive.pdf"},
        ],
        "taches_therapeute": [
            "En séance : Exercice Image Ambiguë",
            "En séance : Introduction à la flexibilité cognitive"
        ],
        "devoirs_patient": [
            "Fiche Pratiquer la flexibilité",
            "Continuer Pleine Conscience + Audios"
        ],
        "fichiers_therapeute": [
            "assets/Exemple_flèche_descendante.pdf",
            "assets/MOD4.30_Exemple_Fiche_La_flèche_descendante.pdf"
        ]
    },

    "module5": {
        "titre": "Module 5 : Comportements Émotionnels",
        "description": "Contrer les évitements et comportements inadaptés.",
        "fichiers_patient": [
            {"nom": "Liste comportements", "fichier": "assets/MOD5.10_Fiche_Liste_des_comportements_émotionnels.pdf"},
            {"nom": "Exemples Comportements", "fichier": "assets/MOD5.30_Fiche_Exemples_d’émotions,_comportements_émotionnels_et_comportements_alternatifs.pdf"},
            {"nom": "Fiche Contrer les comportements", "fichier": "assets/MOD5.50_Fiche_Contrer_les_comportements_émotionnels.pdf"},
        ],
        "taches_therapeute": [
            "Revoir : Flexibilité cognitive (Module 4)",
            "En séance : Lister les comportements émotionnels",
            "En séance : Stratégie pour contrer les comportements"
        ],
        "devoirs_patient": [
            "Identifier et noter les comportements",
            "Appliquer les stratégies contraires"
        ],
        "fichiers_therapeute": []
    },

    "module6": {
        "titre": "Module 6 : Sensations Physiques",
        "description": "Exposition intéroceptive : comprendre et accepter.",
        "fichiers_patient": [
            {"nom": "Exercices sensations physiques", "fichier": "assets/MOD06_Fiche_Exercices_pour_activer_les_sensations_physiques.pdf"},
        ],
        "taches_therapeute": [
            "Revoir : Contrer les comportements (Module 5)",
            "En séance : Réaliser les exercices d'activation physique"
        ],
        "devoirs_patient": [
            "Pratiquer les exercices d'activation à la maison",
            "Continuer le suivi hebdomadaire"
        ],
        "fichiers_therapeute": []
    },

    "module7": {
        "titre": "Module 7 : Expositions",
        "description": "Affronter les situations redoutées.",
        "fichiers_patient": [
            {"nom": "Hiérarchie d'exposition", "fichier": "assets/MOD07.01_Fiche_Hiérarchie_d'exposition_aux_émotions.pdf"},
            {"nom": "Enregistrement Pratique Expo", "fichier": "assets/MOD07.2_Fiche_Enregistrement_de_la_Pratique_d'Exposition_Émotionnelle.pdf"},
        ],
        "taches_therapeute": [
            "En séance : Construire la hiérarchie d'exposition",
            "En séance : Planifier la première exposition"
        ],
        "devoirs_patient": [
            "Réaliser les expositions planifiées",
            "Remplir la fiche d'enregistrement"
        ],
        "fichiers_therapeute": []
    },

    "module8": {
        "titre": "Module 8 : Bilan & Avenir",
        "description": "Maintenir les progrès et prévenir la rechute.",
        "fichiers_patient": [
            {"nom": "Évaluation des Progrès", "fichier": "assets/MOD8.1_Fiche_Evaluation_des_Progrès.pdf"},
            {"nom": "Plan de maintien", "fichier": "assets/MOD8.2_Fiche_Plan_pour_maintenir_et_continuer_à_progresser.pdf"},
        ],
        "taches_therapeute": [
            "Revoir : L'ensemble du parcours et les progrès",
            "En séance : Établir le plan de maintien"
        ],
        "devoirs_patient": [
            "Appliquer le plan de maintien",
            "Continuer les bonnes pratiques"
        ],
        "fichiers_therapeute": []
    }
}