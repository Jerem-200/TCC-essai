# ==============================================================================
# CONFIGURATION DU PROTOCOLE UNIFIÉ (BARLOW) - VERSION FINALE
# ==============================================================================

PROTOCOLE_BARLOW = {
    "module0": {
        "titre": "Module : Analyse fonctionnelle",
        "objectifs": "Comprendre les difficultés, conceptualiser le cas et présenter le traitement.",
        "outils": "Fiche Conceptualisation, Échelles, Fiche Progrès",
        
        # 1. EXAMEN DES TÂCHES (Vide pour le module 0)
        "examen_devoirs": [],

        # 2. ÉTAPES DE LA SÉANCE
        "etapes_seance": [
            {"titre": "Examen des plaintes présentées par le patient", "pdf": None},
            {
                "titre": "Présentation de la justification du traitement (Évaluation)", 
                "pdf": "assets/MODAF10_Fiche_de_conceptualisation_thérapeute.pdf",
                "pdf_2": "assets/MODAF10_Exemple_de_Fiche_de_conceptualisation_thérapeute.pdf" # Astuce pour 2e PDF
            },
            {"titre": "Description de la justification du Protocole Unifié", "pdf": None},
            {
                "titre": "Émotions fréquentes, tendues et indésirables", 
                "pdf": "assets/ModAF_Fiche_Questions_Emotions_négatives,_aversion_et_Comportement.pdf"
            },
            {"titre": "Réactions négatives ou croyances envers les émotions", "pdf": None},
            {"titre": "Efforts pour éviter, fuir ou contrôler les émotions", "pdf": None},
            {"titre": "Résumé des caractéristiques des troubles émotionnels", "pdf": None},
            {"titre": "Objectifs du programme", "pdf": None},
            {
                "titre": "Présenter le format général de traitement (Échelles)", 
                "pdf": "assets/Echelle_d'anxiété.pdf",
                "extras": [
                    "assets/Echelle_de_dépression.pdf",
                    "assets/Echelle_des_autres_émotions_négatives.pdf",
                    "assets/Echelle_des_émotions_positives.pdf",
                    "assets/MODAF05_Fiche_des_Progrès.pdf"
                ]
            }
        ],

        # 3. TÂCHES À DOMICILE
        "taches_domicile": []
    },

    "module1": {
        "titre": "Module 1 : Fixer des objectifs et maintenir la motivation",
        "objectifs": "Maximiser la préparation au changement.",
        "outils": "Fiche Objectifs, Balance décisionnelle",

        "examen_devoirs": [],

        "etapes_seance": [
            {
                "titre": "Motivation : Clarifier les problèmes et fixer objectifs", 
                "pdf": "assets/MOD1.10_Fiche_Objectifs_du_traitement.pdf",
                "pdf_2": "assets/Mod1.11_Fiche_Objectifs_du_traitement_EXEMPLE.pdf"
            },
            {
                "titre": "Motivation : Balance décisionnelle", 
                "pdf": "assets/MOD1.20_Fiche_balance_motivationnelle.pdf"
            }
        ],

        "taches_domicile": [
            {"titre": "Compléter Fiche Objectifs", "pdf": "assets/MOD1.10_Fiche_Objectifs_du_traitement.pdf"}
        ]
    },

    "module2": {
        "titre": "Module 2 : Comprendre les émotions",
        "objectifs": "Psychoéducation et modèle à 3 composantes.",
        "outils": "Fiche Modèle 3 composantes, ARC émotionnel",

        "examen_devoirs": [
            {"titre": "Fiche Objectifs du traitement", "pdf": "assets/MOD1.10_Fiche_Objectifs_du_traitement.pdf"},
            {"titre": "Fiche Balance motivationnelle", "pdf": "assets/MOD1.20_Fiche_balance_motivationnelle.pdf"}
        ],

        "etapes_seance": [
            {"titre": "Psychoéducation - La nature des émotions (Adaptatives)", "pdf": None},
            {"titre": "Le modèle à trois composants des expériences émotionnelles", "pdf": None},
            {
                "titre": "Utilisation du modèle à trois composants", 
                "pdf": "assets/MOD2.1 Fiche_Modèle_à_trois_composantes_de_l'Emotion.pdf"
            },
            {
                "titre": "L'ARC des émotions (Reconnaître et suivre)", 
                "pdf": "assets/MOD2.2_Fiche_suivre_mon_ARC_émotionnel.pdf"
            },
            {"titre": "Réponses apprises (Émotions et comportements)", "pdf": None}
        ],

        "taches_domicile": [
            {"titre": "Remplir Fiche Modèle à 3 composantes", "pdf": "assets/MOD2.1 Fiche_Modèle_à_trois_composantes_de_l'Emotion.pdf"},
            {"titre": "Remplir Fiche ARC émotionnel", "pdf": "assets/MOD2.2_Fiche_suivre_mon_ARC_émotionnel.pdf"}
        ]
    },

    "module3": {
        "titre": "Module 3 : Pleine conscience de l'émotion",
        "objectifs": "Observer sans jugement et ancrage au présent.",
        "outils": "Audios, Fiche Pleine Conscience",

        "examen_devoirs": [
            {"titre": "Fiche ARC émotionnel", "pdf": "assets/MOD2.2_Fiche_suivre_mon_ARC_émotionnel.pdf"}
        ],

        "etapes_seance": [
            {"titre": "Introduction à la pleine conscience des émotions", "pdf": None},
            {"titre": "Conscience sans jugement", "pdf": None},
            {"titre": "Conscience centrée sur le présent", "pdf": None},
            {
                "titre": "Pratiquer la pleine conscience", 
                "pdf": "assets/MOD_3_Script_Méditation_d'initiation.pdf"
            },
            {
                "titre": "Méditation consciente des émotions", 
                "pdf": "assets/MOD3_Fiche_Pleine_Conscience_des_émotions.pdf",
                "extras": [
                    "assets/MOD3_Exemple_Fiche_Pleine_Conscience_des_émotions.pdf",
                    "assets/Audio_Méditation.mp3"
                ]
            },
            {"titre": "Induction d'humeur consciente", "pdf": None},
            {
                "titre": "Ancrage au présent", 
                "pdf": "assets/MOD_3_Script_Méditation_Ancrage.pdf",
                "pdf_2": "assets/Audio_Ancrage.mp3"
            }
        ],

        "taches_domicile": [
            {"titre": "Fiche Pleine Conscience", "pdf": "assets/MOD3_Fiche_Pleine_Conscience_des_émotions.pdf"},
            {"titre": "Semaine 1 : Audio Méditation", "pdf": "assets/Audio_Méditation.mp3"},
            {"titre": "Semaine 2 : Audio Ancrage", "pdf": "assets/Audio_Ancrage.mp3"}
        ]
    },

    "module4": {
        "titre": "Module 4 : La flexibilité cognitive",
        "objectifs": "Assouplir les pensées et interprétations.",
        "outils": "Image ambiguë, Flexibilité cognitive",

        "examen_devoirs": [
            {"titre": "Fiche Pleine Conscience", "pdf": "assets/MOD3_Fiche_Pleine_Conscience_des_émotions.pdf"}
        ],

        "etapes_seance": [
            {"titre": "Introduction à la flexibilité cognitive", "pdf": None},
            {"titre": "L'importance des pensées", "pdf": None},
            {"titre": "Notion de Schémas de pensées automatiques", "pdf": None},
            {
                "titre": "Exercice d'image ambiguë", 
                "pdf": "assets/MOD4.1_Fiche_Exercice_Image_ambiguë.pdf"
            },
            {"titre": "Pièges à penser", "pdf": None},
            {
                "titre": "Pratiquer la flexibilité cognitive", 
                "pdf": "assets/MOD4.20_Fiche_Pratiquer_la_flexibilité_cognitive.pdf",
                "pdf_2": "assets/MOD4.21_Exemple_Fiche_Pratiquer_la_flexibilité_cognitive.pdf"
            }
        ],

        "taches_domicile": [
            {"titre": "Fiche Flexibilité Cognitive", "pdf": "assets/MOD4.20_Fiche_Pratiquer_la_flexibilité_cognitive.pdf"},
            {"titre": "Continuer Pleine Conscience", "pdf": "assets/MOD3_Fiche_Pleine_Conscience_des_émotions.pdf"}
        ]
    },

    "module5": {
        "titre": "Module 5 : Contrer les comportements émotionnels",
        "objectifs": "Identifier et modifier les comportements inadaptés.",
        "outils": "Fiches Comportements, Contrer les comportements",

        "examen_devoirs": [
            {"titre": "Fiche Flexibilité Cognitive", "pdf": "assets/MOD4.20_Fiche_Pratiquer_la_flexibilité_cognitive.pdf"}
        ],

        "etapes_seance": [
            {
                "titre": "Discussion sur les comportements émotionnels", 
                "pdf": "assets/MOD5.11_Exemple_Fiche_Liste_des_comportements_émotionnels.pdf"
            },
            {"titre": "Nature adaptative du comportement", "pdf": None},
            {
                "titre": "Examen des différents types de comportement", 
                "pdf": "assets/MOD5.10_Fiche_Liste_des_comportements_émotionnels.pdf"
            },
            {"titre": "Rôle des comportements dans le maintien des troubles", "pdf": None},
            {"titre": "Démonstration d'évitement des émotions", "pdf": None},
            {
                "titre": "Briser le cycle (Actions alternatives)", 
                "pdf": "assets/MOD5.50_Fiche_Contrer_les_comportements_émotionnels.pdf",
                "extras": [
                    "assets/MOD5.51_Exemple_Fiche_Contrer_les_comportements_émotionnels.pdf",
                    "assets/MOD5.30_Fiche_Exemples_d’émotions,_comportements_émotionnels_et_comportements_alternatifs.pdf",
                    "assets/MOD5.40_Fiche_Exemples_de_Comportements_émotionnel_et_conséquences_à_court_et_long_terme.pdf"
                ]
            }
        ],

        "taches_domicile": [
            {"titre": "Liste des comportements émotionnels", "pdf": "assets/MOD5.10_Fiche_Liste_des_comportements_émotionnels.pdf"},
            {"titre": "Contrer les comportements", "pdf": "assets/MOD5.50_Fiche_Contrer_les_comportements_émotionnels.pdf"}
        ]
    },

    "module6": {
        "titre": "Module 6 : Sensations physiques",
        "objectifs": "Exposition intéroceptive.",
        "outils": "Exercices sensations, Chronomètre",

        "examen_devoirs": [
            {"titre": "Contrer les comportements", "pdf": "assets/MOD5.50_Fiche_Contrer_les_comportements_émotionnels.pdf"}
        ],

        "etapes_seance": [
            {"titre": "Sensations physiques et réponse émotionnelle", "pdf": None},
            {"titre": "Évitement des sensations physiques", "pdf": None},
            {"titre": "Exercices d'induction des symptômes", "pdf": None},
            {"titre": "Expositions répétées", "pdf": None},
            {"titre": "Exposition intéroceptive : procédure", "pdf": None}
        ],

        "taches_domicile": [
            {"titre": "Exercices activer sensations physiques", "pdf": "assets/MOD06_Fiche_Exercices_pour_activer_les_sensations_physiques.pdf"}
        ]
    },

    "module7": {
        "titre": "Module 7 : Expositions aux émotions",
        "objectifs": "Exposition in vivo et imaginaire.",
        "outils": "Hiérarchie d'exposition, Enregistrement",

        "examen_devoirs": [
            {"titre": "Exercices sensations physiques", "pdf": "assets/MOD06_Fiche_Exercices_pour_activer_les_sensations_physiques.pdf"}
        ],

        "etapes_seance": [
            {"titre": "Expositions aux émotions", "pdf": None},
            {
                "titre": "Introduction aux expositions en séance", 
                "pdf": "assets/MOD07.01_Fiche_Hiérarchie_d'exposition_aux_émotions.pdf",
                "pdf_2": "assets/MOD07.01_Exemple_Fiche_Hiérarchie_d'exposition_aux_émotions.pdf"
            },
            {"titre": "Expositions basées sur la situation", "pdf": None},
            {"titre": "Expositions d'émotions imaginaires", "pdf": None},
            {"titre": "Sensation physique / Emotion Expositions", "pdf": None},
            {"titre": "Mener des expositions en séance", "pdf": None},
            {
                "titre": "Une fois l'exposition terminée... (Debrief)", 
                "pdf": "assets/MOD07.2_Fiche_Enregistrement_de_la_Pratique_d'Exposition_Émotionnelle.pdf",
                "pdf_2": "assets/MOD07.2_Exemple_Fiche_Enregistrement_de_la_Pratique_d'Exposition_Émotionnelle.pdf"
            },
            {"titre": "Transférer dans le contexte réel", "pdf": None}
        ],

        "taches_domicile": [
            {"titre": "Enregistrement Pratique Exposition", "pdf": "assets/MOD07.2_Fiche_Enregistrement_de_la_Pratique_d'Exposition_Émotionnelle.pdf"}
        ]
    },

    "module8": {
        "titre": "Module 8 : Bilan et perspectives",
        "objectifs": "Bilan et prévention de la rechute.",
        "outils": "Fiches progrès, Plan de maintien",

        "examen_devoirs": [
            {"titre": "Enregistrement Pratique Exposition", "pdf": "assets/MOD07.2_Fiche_Enregistrement_de_la_Pratique_d'Exposition_Émotionnelle.pdf"},
            {"titre": "Bilan de toutes les fiches (Objectifs, Balance, ARC, etc.)", "pdf": "assets/MODAF05_Fiche_des_Progrès.pdf"}
        ],

        "etapes_seance": [
            {"titre": "Revue des compétences acquises", "pdf": None},
            {
                "titre": "Évaluation des progrès", 
                "pdf": "assets/MOD8.1_Fiche_Evaluation_des_Progrès.pdf"
            },
            {"titre": "Anticiper les difficultés futures", "pdf": None},
            {"titre": "Poursuite de la pratique", "pdf": None},
            {
                "titre": "Établissement d'objectifs à long terme", 
                "pdf": "assets/MOD8.2_Fiche_Plan_pour_maintenir_et_continuer_à_progresser.pdf"
            },
            {"titre": "Fin du traitement", "pdf": None}
        ],

        "taches_domicile": []
    }
}