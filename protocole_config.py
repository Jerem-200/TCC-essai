# ==============================================================================
# CONFIGURATION DU PROTOCOLE UNIFIÉ (BARLOW) - LISTE EXACTE
# ==============================================================================

PROTOCOLE_BARLOW = {
    "module0": {
        "titre": "Module : Analyse fonctionnelle",
        "objectifs": "Comprendre les difficultés et conceptualiser le cas.",
        "outils": "Fiche Conceptualisation, Échelles",
        # Liste brute demandée pour l'onglet "Documents"
        "pdfs_module": [
            "assets/L'analyse_fonctionnelle.pdf",
            "assets/ModAF_Fiche_Questions_Emotions_négatives,_aversion_et_Comportement.pdf",
            "assets/Echelle_d'anxiété.pdf",
            "assets/Echelle_de_dépression.pdf",
            "assets/Echelle_des_autres_émotions_négatives.pdf",
            "assets/Echelle_des_émotions_positives.pdf",
            "assets/MODAF05_Fiche_des_Progrès.pdf",
            "assets/MODAF10_Fiche_de_conceptualisation_thérapeute.pdf",
            "assets/MODAF10_Exemple_de_Fiche_de_conceptualisation_thérapeute.pdf"
        ],
        # On garde la structure pour la procédure (simplifiée ici)
        "examen_devoirs": [],
        "etapes_seance": [{"titre": "Analyse fonctionnelle", "pdf": None}],
        "taches_domicile": []
    },

    "module1": {
        "titre": "Module 1 : Fixer des objectifs et maintenir la motivation",
        "objectifs": "Maximiser la préparation au changement.",
        "outils": "Fiche Objectifs, Balance décisionnelle",
        "pdfs_module": [
            "assets/Module_1_Fixer_des_objectifs_et_maintenir_la_motivation.pdf",
            "assets/MOD1.10_Fiche_Objectifs_du_traitement.pdf",
            "assets/Mod1.11_Fiche_Objectifs_du_traitement_EXEMPLE.pdf",
            "assets/MOD1.20_Fiche_balance_motivationnelle.pdf"
        ],
        "examen_devoirs": [],
        "etapes_seance": [{"titre": "Motivation et Objectifs", "pdf": None}],
        "taches_domicile": [{"titre": "Fiche Objectifs", "pdf": "assets/MOD1.10_Fiche_Objectifs_du_traitement.pdf"}]
    },

    "module2": {
        "titre": "Module 2 : Comprendre les émotions",
        "objectifs": "Psychoéducation et modèle à 3 composantes.",
        "outils": "Fiche Modèle 3 composantes, ARC émotionnel",
        "pdfs_module": [
            "assets/Module_2_Comprendre_les_émotions.pdf",
            "assets/MOD2.1 Fiche_Modèle_à_trois_composantes_de_l'Emotion.pdf",
            "assets/MOD2.2_Fiche_suivre_mon_ARC_émotionnel.pdf",
            "assets/Antécédents_émotions.pdf"
        ],
        "examen_devoirs": [{"titre": "Objectifs", "pdf": None}],
        "etapes_seance": [{"titre": "Psychoéducation", "pdf": None}],
        "taches_domicile": [{"titre": "Modèle 3 composantes", "pdf": "assets/MOD2.1 Fiche_Modèle_à_trois_composantes_de_l'Emotion.pdf"}]
    },

    "module3": {
        "titre": "Module 3 : Pleine conscience de l'émotion",
        "objectifs": "Observer sans jugement et ancrage au présent.",
        "outils": "Audios, Fiche Pleine Conscience",
        "pdfs_module": [
            "assets/Module_3_La_pleine_conscience_des_émotions.pdf",
            "assets/MOD3_Fiche_Pleine_Conscience_des_émotions.pdf",
            "assets/MOD3_Exemple_Fiche_Pleine_Conscience_des_émotions.pdf",
            "assets/MOD_3_Script_Méditation_d'initiation.pdf",
            "assets/MOD_3_Script_Méditation_Ancrage.pdf",
            "assets/Audio_Méditation.mp3",
            "assets/Audio_Ancrage.mp3"
        ],
        "examen_devoirs": [],
        "etapes_seance": [{"titre": "Initiation Méditation", "pdf": None}],
        "taches_domicile": [{"titre": "Pratique audio", "pdf": "assets/Audio_Méditation.mp3"}]
    },

    "module4": {
        "titre": "Module 4 : La flexibilité cognitive",
        "objectifs": "Assouplir les pensées et interprétations.",
        "outils": "Image ambiguë, Flexibilité cognitive",
        "pdfs_module": [
            "assets/Module_4_La_flexibilité_cognitive.pdf",
            "assets/MOD4.1_Fiche_Exercice_Image_ambiguë.pdf",
            "assets/MOD4.20_Fiche_Pratiquer_la_flexibilité_cognitive.pdf",
            "assets/MOD4.21_Exemple_Fiche_Pratiquer_la_flexibilité_cognitive.pdf",
            "assets/MOD4.30_Exemple_Fiche_La_flèche_descendante.pdf",
            "assets/Exemple_flèche_descendante.pdf"
        ],
        "examen_devoirs": [],
        "etapes_seance": [{"titre": "Flexibilité", "pdf": None}],
        "taches_domicile": [{"titre": "Fiche Flexibilité", "pdf": "assets/MOD4.20_Fiche_Pratiquer_la_flexibilité_cognitive.pdf"}]
    },

    "module5": {
        "titre": "Module 5 : Contrer les comportements émotionnels",
        "objectifs": "Identifier et modifier les comportements inadaptés.",
        "outils": "Fiches Comportements",
        "pdfs_module": [
            "assets/Module_5_Contrer_les_comportements_émotionnels.pdf",
            "assets/MOD5.10_Fiche_Liste_des_comportements_émotionnels.pdf",
            "assets/MOD5.11_Exemple_Fiche_Liste_des_comportements_émotionnels.pdf",
            "assets/MOD5.30_Fiche_Exemples_d’émotions,_comportements_émotionnels_et_comportements_alternatifs.pdf",
            "assets/MOD5.40_Fiche_Exemples_de_Comportements_émotionnel_et_conséquences_à_court_et_long_terme.pdf",
            "assets/MOD5.50_Fiche_Contrer_les_comportements_émotionnels.pdf"
        ],
        "examen_devoirs": [],
        "etapes_seance": [{"titre": "Comportements émotionnels", "pdf": None}],
        "taches_domicile": [{"titre": "Contrer les comportements", "pdf": "assets/MOD5.50_Fiche_Contrer_les_comportements_émotionnels.pdf"}]
    },

    "module6": {
        "titre": "Module 6 : Sensations physiques",
        "objectifs": "Exposition intéroceptive.",
        "outils": "Exercices sensations",
        "pdfs_module": [
            "assets/Module_6_ Comprendre_et_accepter_les_sensations_physiques.pdf",
            "assets/MOD06_Fiche_Exercices_pour_activer_les_sensations_physiques.pdf"
        ],
        "examen_devoirs": [],
        "etapes_seance": [{"titre": "Induction symptômes", "pdf": None}],
        "taches_domicile": [{"titre": "Exercices physiques", "pdf": "assets/MOD06_Fiche_Exercices_pour_activer_les_sensations_physiques.pdf"}]
    },

    "module7": {
        "titre": "Module 7 : Expositions aux émotions",
        "objectifs": "Exposition in vivo et imaginaire.",
        "outils": "Hiérarchie d'exposition",
        "pdfs_module": [
            "assets/Module_7_Les_expositions_aux_émotions.pdf",
            "assets/MOD07.01_Fiche_Hiérarchie_d'exposition_aux_émotions.pdf",
            "assets/MOD07.01_Exemple_Fiche_Hiérarchie_d'exposition_aux_émotions.pdf",
            "assets/MOD07.2_Fiche_Enregistrement_de_la_Pratique_d'Exposition_Émotionnelle.pdf",
            "assets/MOD07.2_Exemple_Fiche_Enregistrement_de_la_Pratique_d'Exposition_Émotionnelle.pdf"
        ],
        "examen_devoirs": [],
        "etapes_seance": [{"titre": "Hiérarchie", "pdf": None}],
        "taches_domicile": [{"titre": "Enregistrement Pratique", "pdf": "assets/MOD07.2_Fiche_Enregistrement_de_la_Pratique_d'Exposition_Émotionnelle.pdf"}]
    },

    "module8": {
        "titre": "Module 8 : Bilan et perspectives",
        "objectifs": "Bilan et prévention de la rechute.",
        "outils": "Fiches progrès, Plan de maintien",
        "pdfs_module": [
            "assets/Module_8_Bilan_et_perspectives_futures.pdf",
            "assets/MOD8.1_Fiche_Evaluation_des_Progrès.pdf",
            "assets/MOD8.2_Fiche_Plan_pour_maintenir_et_continuer_à_progresser.pdf"
        ],
        "examen_devoirs": [],
        "etapes_seance": [{"titre": "Bilan", "pdf": None}],
        "taches_domicile": [{"titre": "Plan de maintien", "pdf": "assets/MOD8.2_Fiche_Plan_pour_maintenir_et_continuer_à_progresser.pdf"}]
    }
}