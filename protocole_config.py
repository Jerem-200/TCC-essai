# ==============================================================================
# CONFIGURATION DU PROTOCOLE UNIFIÉ (BARLOW) - STRUCTURE ERGONOMIQUE
# ==============================================================================

PROTOCOLE_BARLOW = {
    "module0": {
        "titre": "Module 0 : Analyse fonctionnelle",
        "objectifs": "Comprendre les difficultés, conceptualiser le cas et présenter le traitement.",
        "outils": "Fiche Conceptualisation, Échelles",
        
        # Liste globale pour l'onglet "Tous les Documents"
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

        "examen_devoirs": [], # Rien au module 0

        "etapes_seance": [
            {"titre": "Examen des plaintes présentées par le patient", "pdfs": []},
            {
                "titre": "Présentation de la justification du traitement (Évaluation)", 
                "details": "A venir",
                "pdfs": [
                    "assets/MODAF10_Fiche_de_conceptualisation_thérapeute.pdf",
                    "assets/MODAF10_Exemple_de_Fiche_de_conceptualisation_thérapeute.pdf"
                ]
            },
            {"titre": "Description de la justification du Protocole Unifié", "details": "A venir", "pdfs": []},
            {
                "titre": "Émotions fréquentes, tendues et indésirables", 
                "details": "A venir",
                "pdfs": ["assets/ModAF_Fiche_Questions_Emotions_négatives,_aversion_et_Comportement.pdf"]
            },
            {
                "titre": "Réactions négatives ou croyances envers les émotions indésirables",
                "details": "A venir",
                "pdfs": []
            },
            {"titre": "Efforts pour éviter, fuir ou contrôler les émotions", "details": "A venir", "pdfs": []},
            {"titre": "Résumé des caractéristiques des troubles émotionnels", "details": "A venir", "pdfs": []},
            {"titre": "Objectifs du programme", "details": "A venir","pdfs": []},
            {
                "titre": "Présenter le format général de traitement (Échelles)", "details": "A venir",
                "pdfs": [
                    "assets/Echelle_d'anxiété.pdf",
                    "assets/Echelle_de_dépression.pdf",
                    "assets/Echelle_des_autres_émotions_négatives.pdf",
                    "assets/Echelle_des_émotions_positives.pdf",
                    "assets/MODAF05_Fiche_des_Progrès.pdf"
                ]
            }
        ],

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

        "etapes_seance": [
            {
                "titre": "Motivation : Clarifier les problèmes et fixer objectifs", "details": "A venir",
                "pdfs": [
                    "assets/MOD1.10_Fiche_Objectifs_du_traitement.pdf",
                    "assets/Mod1.11_Fiche_Objectifs_du_traitement_EXEMPLE.pdf"
                ]
            },
            {
                "titre": "Motivation : Balance décisionnelle", "details": "A venir",
                "pdfs": ["assets/MOD1.20_Fiche_balance_motivationnelle.pdf"]
            }
        ],

        "taches_domicile": [
            {"titre": "Fiche Objectifs du traitement", "pdf": "assets/MOD1.10_Fiche_Objectifs_du_traitement.pdf"}
        ]
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

        "examen_devoirs": [
            {"titre": "Fiche Objectifs du traitement", "pdf": "assets/MOD1.10_Fiche_Objectifs_du_traitement.pdf"},
            {"titre": "Fiche Balance motivationnelle", "pdf": "assets/MOD1.20_Fiche_balance_motivationnelle.pdf"}
        ],

        "etapes_seance": [
            {"titre": "Psychoéducation - La nature des émotions", "details": "A venir", "pdfs": []},
            {"titre": "Le modèle à trois composants des expériences émotionnelles", "details": "A venir", "pdfs": []},
            {
                "titre": "Utilisation du modèle à trois composants", 
                "details": "A venir",
                "pdfs": ["assets/MOD2.1 Fiche_Modèle_à_trois_composantes_de_l'Emotion.pdf"]
            },
            {
                "titre": "L'ARC des émotions (Reconnaître et suivre)", "details": "A venir",
                "pdfs": ["assets/MOD2.2_Fiche_suivre_mon_ARC_émotionnel.pdf"]
            },
            {"titre": "Comprendre les émotions et les comportements", "details": "A venir", "pdfs": []}
        ],

        "taches_domicile": [
            {"titre": "Modèle 3 composantes", "pdf": "assets/MOD2.1 Fiche_Modèle_à_trois_composantes_de_l'Emotion.pdf"},
            {"titre": "ARC émotionnel", "pdf": "assets/MOD2.2_Fiche_suivre_mon_ARC_émotionnel.pdf"}
        ]
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

        "examen_devoirs": [
            {"titre": "Fiche ARC émotionnel", "pdf": "assets/MOD2.2_Fiche_suivre_mon_ARC_émotionnel.pdf"}
        ],

        "etapes_seance": [
            {"titre": "Introduction à la pleine conscience des émotions", "details": "A venir", "pdfs": []},
            {"titre": "Conscience des émotions sans jugement", "details": "A venir","pdfs": []},
            {"titre": "Conscience des émotions centrée sur le présent", "details": "A venir","pdfs": []},
            {
                "titre": "Pratiquer la pleine conscience", "details": "A venir",
                "pdfs": ["assets/MOD_3_Script_Méditation_d'initiation.pdf"]
            },
            {
                "titre": "Méditation consciente des émotions", "details": "A venir",
                "pdfs": [
                    "assets/MOD3_Fiche_Pleine_Conscience_des_émotions.pdf",
                    "assets/MOD3_Exemple_Fiche_Pleine_Conscience_des_émotions.pdf",
                    "assets/Audio_Méditation.mp3"
                ]
            },
            {"titre": "Induction d'humeur consciente", "details": "A venir","pdfs": []},
            {
                "titre": "Ancrage au présent", "details": "A venir",
                "pdfs": [
                    "assets/MOD_3_Script_Méditation_Ancrage.pdf",
                    "assets/Audio_Ancrage.mp3"
                ]
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
        
        "pdfs_module": [
            "assets/Module_4_La_flexibilité_cognitive.pdf",
            "assets/MOD4.1_Fiche_Exercice_Image_ambiguë.pdf",
            "assets/MOD4.20_Fiche_Pratiquer_la_flexibilité_cognitive.pdf",
            "assets/MOD4.21_Exemple_Fiche_Pratiquer_la_flexibilité_cognitive.pdf",
            "assets/MOD4.30_Exemple_Fiche_La_flèche_descendante.pdf",
            "assets/Exemple_flèche_descendante.pdf"
        ],

        "examen_devoirs": [
            {"titre": "Fiche Pleine Conscience", "pdf": "assets/MOD3_Fiche_Pleine_Conscience_des_émotions.pdf"}
        ],

        "etapes_seance": [
            {"titre": "Introduction à la flexibilité cognitive", "details": "A venir","pdfs": []},
            {"titre": "L'importance des pensées", "details": "A venir","pdfs": []},
            {"titre": "Notion de Schémas de pensées automatiques", "details": "A venir","pdfs": []},
            {
                "titre": "Exercice d'image ambiguë", "details": "A venir",
                "pdfs": ["assets/MOD4.1_Fiche_Exercice_Image_ambiguë.pdf"]
            },
            {"titre": "Pièges à penser", "details": "A venir","pdfs": []},
            {
                "titre": "Pratiquer la flexibilité cognitive", "details": "A venir",
                "pdfs": [
                    "assets/MOD4.20_Fiche_Pratiquer_la_flexibilité_cognitive.pdf",
                    "assets/MOD4.21_Exemple_Fiche_Pratiquer_la_flexibilité_cognitive.pdf"
                ]
            }
        ],

        "taches_domicile": [
            {"titre": "Fiche Flexibilité Cognitive", "pdf": "assets/MOD4.20_Fiche_Pratiquer_la_flexibilité_cognitive.pdf"},
            {"titre": "Pleine Conscience (Suite)", "pdf": "assets/MOD3_Fiche_Pleine_Conscience_des_émotions.pdf"}
        ]
    },

    "module5": {
        "titre": "Module 5 : Contrer les comportements émotionnels",
        "objectifs": "Identifier et modifier les comportements inadaptés.",
        "outils": "Fiches Comportements, Contrer les comportements",
        
        "pdfs_module": [
            "assets/Module_5_Contrer_les_comportements_émotionnels.pdf",
            "assets/MOD5.10_Fiche_Liste_des_comportements_émotionnels.pdf",
            "assets/MOD5.11_Exemple_Fiche_Liste_des_comportements_émotionnels.pdf",
            "assets/MOD5.30_Fiche_Exemples_d’émotions,_comportements_émotionnels_et_comportements_alternatifs.pdf",
            "assets/MOD5.40_Fiche_Exemples_de_Comportements_émotionnel_et_conséquences_à_court_et_long_terme.pdf",
            "assets/MOD5.50_Fiche_Contrer_les_comportements_émotionnels.pdf"
        ],

        "examen_devoirs": [
            {"titre": "Fiche Flexibilité Cognitive", "pdf": "assets/MOD4.20_Fiche_Pratiquer_la_flexibilité_cognitive.pdf"}
        ],

        "etapes_seance": [
            {
                "titre": "Discussion sur les comportements émotionnels", "details": "A venir",
                "pdfs": ["assets/MOD5.11_Exemple_Fiche_Liste_des_comportements_émotionnels.pdf"]
            },
            {"titre": "Discussion sur la nature adaptative du comportement", "details": "A venir","pdfs": []},
            {
                "titre": "Examen des différents types de comportement", "details": "A venir",
                "pdfs": ["assets/MOD5.10_Fiche_Liste_des_comportements_émotionnels.pdf"]
            },
            {"titre": "Rôle des comportements dans le maintien des troubles", "details": "A venir","pdfs": []},
            {"titre": "Démonstration d'évitement des émotions", "details": "A venir","pdfs": []},
            {
                "titre": "Briser le cycle (Actions alternatives)", "details": "A venir",
                "pdfs": [
                    "assets/MOD5.50_Fiche_Contrer_les_comportements_émotionnels.pdf",
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
        
        "pdfs_module": [
            "assets/Module_6_ Comprendre_et_accepter_les_sensations_physiques.pdf",
            "assets/MOD06_Fiche_Exercices_pour_activer_les_sensations_physiques.pdf"
        ],

        "examen_devoirs": [
            {"titre": "Contrer les comportements", "pdf": "assets/MOD5.50_Fiche_Contrer_les_comportements_émotionnels.pdf"}
        ],

        "etapes_seance": [
            {"titre": "Sensations physiques et réponse émotionnelle", "details": "A venir","pdfs": []},
            {"titre": "Évitement des sensations physiques", "details": "A venir","pdfs": []},
            {"titre": "Exercices d'induction des symptômes", "details": "A venir", "pdfs": []},
            {"titre": "Expositions répétées", "details": "A venir", "pdfs": []},
            {"titre": "Exposition intéroceptive : procédure", "details": "A venir", "pdfs": []}
        ],

        "taches_domicile": [
            {"titre": "Exercices activer sensations physiques", "pdf": "assets/MOD06_Fiche_Exercices_pour_activer_les_sensations_physiques.pdf"}
        ]
    },

    "module7": {
        "titre": "Module 7 : Expositions aux émotions",
        "objectifs": "Exposition in vivo et imaginaire.",
        "outils": "Hiérarchie d'exposition, Enregistrement",
        
        "pdfs_module": [
            "assets/Module_7_Les_expositions_aux_émotions.pdf",
            "assets/MOD07.01_Fiche_Hiérarchie_d'exposition_aux_émotions.pdf",
            "assets/MOD07.01_Exemple_Fiche_Hiérarchie_d'exposition_aux_émotions.pdf",
            "assets/MOD07.2_Fiche_Enregistrement_de_la_Pratique_d'Exposition_Émotionnelle.pdf",
            "assets/MOD07.2_Exemple_Fiche_Enregistrement_de_la_Pratique_d'Exposition_Émotionnelle.pdf"
        ],

        "examen_devoirs": [
            {"titre": "Exercices sensations physiques", "pdf": "assets/MOD06_Fiche_Exercices_pour_activer_les_sensations_physiques.pdf"}
        ],

        "etapes_seance": [
            {"titre": "Expositions aux émotions", "details": "A venir","pdfs": []},
            {
                "titre": "Introduction aux expositions en séance", "details": "A venir",
                "pdfs": [
                    "assets/MOD07.01_Fiche_Hiérarchie_d'exposition_aux_émotions.pdf",
                    "assets/MOD07.01_Exemple_Fiche_Hiérarchie_d'exposition_aux_émotions.pdf"
                ]
            },
            {"titre": "Expositions basées sur la situation", "details": "A venir","pdfs": []},
            {"titre": "Expositions d'émotions imaginaires", "details": "A venir", "pdfs": []},
            {"titre": "Sensation physique / Emotion Expositions", "details": "A venir", "pdfs": []},
            {"titre": "Mener des expositions en séance", "details": "A venir", "pdfs": []},
            {
                "titre": "Une fois l'exposition terminée... (Debrief)", "details": "A venir",
                "pdfs": [
                    "assets/MOD07.2_Fiche_Enregistrement_de_la_Pratique_d'Exposition_Émotionnelle.pdf",
                    "assets/MOD07.2_Exemple_Fiche_Enregistrement_de_la_Pratique_d'Exposition_Émotionnelle.pdf"
                ]
            },
            {"titre": "Transférer dans le contexte réel", "details": "A venir", "pdfs": []}
        ],

        "taches_domicile": [
            {"titre": "Enregistrement Pratique Exposition", "pdf": "assets/MOD07.2_Fiche_Enregistrement_de_la_Pratique_d'Exposition_Émotionnelle.pdf"}
        ]
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

        "examen_devoirs": [
            {"titre": "Fiche Objectifs", "pdf": "assets/MOD1.10_Fiche_Objectifs_du_traitement.pdf"},
            {"titre": "Balance Motivationnelle", "pdf": "assets/MOD1.20_Fiche_balance_motivationnelle.pdf"},
            {"titre": "Modèle 3 composantes", "pdf": "assets/MOD2.1 Fiche_Modèle_à_trois_composantes_de_l'Emotion.pdf"},
            {"titre": "ARC Emotionnel", "pdf": "assets/MOD2.2_Fiche_suivre_mon_ARC_émotionnel.pdf"},
            {"titre": "Pleine Conscience", "pdf": "assets/MOD3_Fiche_Pleine_Conscience_des_émotions.pdf"},
            {"titre": "Flexibilité Cognitive", "pdf": "assets/MOD4.20_Fiche_Pratiquer_la_flexibilité_cognitive.pdf"},
            {"titre": "Contrer Comportements", "pdf": "assets/MOD5.50_Fiche_Contrer_les_comportements_émotionnels.pdf"},
            {"titre": "Exercices Sensations", "pdf": "assets/MOD06_Fiche_Exercices_pour_activer_les_sensations_physiques.pdf"},
            {"titre": "Enregistrement Exposition", "pdf": "assets/MOD07.2_Fiche_Enregistrement_de_la_Pratique_d'Exposition_Émotionnelle.pdf"},
            {"titre": "Echelles (Anxiété...)", "pdf": "assets/Echelle_d'anxiété.pdf"},
            {"titre": "Echelle Dépression", "pdf": "assets/Echelle_de_dépression.pdf"},
            {"titre": "Autres Emotions", "pdf": "assets/Echelle_des_autres_émotions_négatives.pdf"},
            {"titre": "Emotions Positives", "pdf": "assets/Echelle_des_émotions_positives.pdf"},
            {"titre": "Fiche Progrès", "pdf": "assets/MODAF05_Fiche_des_Progrès.pdf"}
        ],

        "etapes_seance": [
            {"titre": "Revue des compétences acquises", "details": "A venir","pdfs": []},
            {
                "titre": "Évaluation des progrès", "details": "A venir",
                "pdfs": ["assets/MOD8.1_Fiche_Evaluation_des_Progrès.pdf"]
            },
            {"titre": "Anticiper les difficultés futures", "details": "A venir","pdfs": []},
            {"titre": "Poursuite de la pratique", "details": "A venir","pdfs": []},
            {
                "titre": "Établissement d'objectifs à long terme", "details": "A venir",
                "pdfs": ["assets/MOD8.2_Fiche_Plan_pour_maintenir_et_continuer_à_progresser.pdf"]
            },
            {"titre": "Fin du traitement", "pdfs": []}
        ],

        "taches_domicile": []
    }
}