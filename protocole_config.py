# ==============================================================================
# CONFIGURATION DU PROTOCOLE UNIFIÉ (BARLOW) - STRUCTURE ERGONOMIQUE
# ==============================================================================
# =========================================================
# CONFIGURATION DES QUESTIONNAIRES HEBDOMADAIRES (BARLOW)
# =========================================================
QUESTIONS_HEBDO = {
    "Anxiété": {
        "titre": "📉 Échelle d'Anxiété (OASIS)",
        "description": "Entourez le numéro correspondant à la réponse qui décrit le mieux votre expérience au cours de la semaine passée.",
        "type": "qcm_oasis",  # <--- NOUVEAU TYPE SPÉCIFIQUE
        "questions": [
            {
                "id": "freq",
                "label": "1. À quelle fréquence vous êtes-vous senti anxieux ?",
                "options": [
                    "0 = Aucune anxiété au cours de la semaine dernière.",
                    "1 = Anxiété peu fréquente. Je me suis senti anxieux à quelques reprises.",
                    "2 = Anxiété occasionnelle. Je me sentais anxieux la plupart du temps. C'était difficile de se détendre.",
                    "3 = Anxiété fréquente. Je me sentais anxieux la plupart du temps. C'était très difficile de se détendre.",
                    "4 = Anxiété constante. Je me sentais anxieux tout le temps et je n'étais jamais vraiment détendu."
                ]
            },
            {
                "id": "intensite",
                "label": "2. Quelle était l'intensité ou la gravité de votre anxiété ?",
                "options": [
                    "0 = Peu ou pas du tout : L'anxiété était absente ou à peine perceptible.",
                    "1 = Légère : L'anxiété était à un niveau bas. Il était possible de se détendre. Symptômes physiques légers.",
                    "2 = Modérée : L'anxiété était parfois pénible. C'était difficile de se détendre ou de se concentrer.",
                    "3 = Sévère : L'anxiété était intense la plupart du temps. Symptômes physiques extrêmement inconfortables.",
                    "4 = Extrême : L'anxiété était envahissante. Il était impossible de se détendre. Symptômes insupportables."
                ]
            },
            {
                "id": "evitement",
                "label": "3. À quelle fréquence avez-vous évité des situations, lieux ou objets ?",
                "options": [
                    "0 = Aucun : Je n'évite pas les lieux, les situations, les activités ou les choses à cause de la peur.",
                    "1 = Peu fréquent : J'évite quelque chose de temps en temps, mais mon style de vie n'est pas affecté.",
                    "2 = Occasionnellement : J'ai une certaine peur, mais cela reste gérable. Mon style de vie n'a changé que de façon mineure.",
                    "3 = Fréquent : J'ai une peur considérable et j'essaie vraiment d'éviter les choses. Changements importants à mon style de vie.",
                    "4 = Tout le temps : Éviter des objets/situations a pris le dessus sur ma vie. Mode de vie largement affecté."
                ]
            },
            {
                "id": "interf_travail",
                "label": "4. Perturbation de la capacité à faire les choses (travail/école/maison) ?",
                "options": [
                    "0 = Aucun : Aucune interférence due à l'anxiété.",
                    "1 = Léger : Mon anxiété a causé des interférences mais tout ce qui doit être fait se fait encore.",
                    "2 = Modéré : Mon anxiété interfère définitivement avec les tâches. La plupart des choses se font encore, mais moins bien.",
                    "3 = Sévère : Mon anxiété a vraiment modifié ma capacité à faire avancer les choses. Ma performance a souffert.",
                    "4 = Extrême : Mon anxiété est devenue invalidante. Incapable d'accomplir des tâches (démission, échec scolaire, etc.)."
                ]
            },
            {
                "id": "interf_social",
                "label": "5. Interférence avec la vie sociale et les relations ?",
                "options": [
                    "0 = Aucun : Mon anxiété n'affecte pas mes relations.",
                    "1 = Léger : Interfère légèrement. Certaines relations ont souffert mais vie sociale épanouissante.",
                    "2 = Modéré : Interférences vécues, mais j'ai encore quelques relations proches. Je socialise encore parfois.",
                    "3 = Sévère : Mes amitiés ont beaucoup souffert. Je n'aime pas les activités sociales. Je socialise très peu.",
                    "4 = Extrême : Mon anxiété a complètement perturbé mes activités sociales. Relations terminées ou famille tendue."
                ]
            }
        ]
    },

    "Dépression": {
        "titre": "☁️ Échelle de Dépression",
        "description": "Évaluez l'intensité moyenne de votre tristesse/dépression cette semaine (0 = Nulle, 8 = Extrême).",
        "type": "scale_0_8",
        "questions": ["À quel point vous êtes-vous senti(e) triste ou déprimé(e) cette semaine ?"]
    },
    "Autres Émotions Négatives": {
        "titre": "😡 Autres Émotions Négatives",
        "description": "Colère, Culpabilité, Honte, etc. (0 = Nulle, 8 = Extrême).",
        "type": "scale_0_8",
        "questions": ["Intensité de la Colère", "Intensité de la Culpabilité", "Intensité de la Honte"]
    },
    "Émotions Positives": {
        "titre": "🌞 Émotions Positives",
        "description": "Joie, Enthousiasme, Fierté, etc. (0 = Nulle, 8 = Extrême).",
        "type": "scale_0_8",
        "questions": ["À quel point avez-vous ressenti de la joie ou du plaisir cette semaine ?"]
    },
    "Fiche de Progrès": {
        "titre": "📈 Fiche des Progrès (Tâches à domicile)",
        "description": "Notez ici vos réussites et difficultés concernant les exercices.",
        "type": "text",
        "questions": [
            "Quelles tâches avez-vous accomplies cette semaine ?",
            "Quelles difficultés avez-vous rencontrées ?",
            "Qu'avez-vous appris ?"
        ]
    }
}

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
            {"titre": "Examen des plaintes présentées par le patient", "details": "A venir","pdfs": []},
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
            {"titre": "Fiche Objectifs du traitement", "pdf": "assets/MOD1.10_Fiche_Objectifs_du_traitement.pdf"},
            {"titre": "Echelle d'anxiété", "pdf": "assets/Echelle_d'anxiété.pdf"},
            {"titre": "Echelle de dépression", "pdf": "Echelle_de_dépression.pdf"},
            {"titre": "Echelle des autres émotions négatives", "pdf": "Echelle_des_autres_émotions_négatives.pdf"},
            {"titre": "Echelle des émotions positives", "pdf": "Echelle_des_émotions_positives.pdf"},
            {"titre": "Fiche des progrès", "pdf": "MODAF05_Fiche_des_Progrès.pdf"}
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
            {"titre": "ARC émotionnel", "pdf": "assets/MOD2.2_Fiche_suivre_mon_ARC_émotionnel.pdf"},
            {"titre": "Echelle d'anxiété", "pdf": "assets/Echelle_d'anxiété.pdf"},
            {"titre": "Echelle de dépression", "pdf": "Echelle_de_dépression.pdf"},
            {"titre": "Echelle des autres émotions négatives", "pdf": "Echelle_des_autres_émotions_négatives.pdf"},
            {"titre": "Echelle des émotions positives", "pdf": "Echelle_des_émotions_positives.pdf"},
            {"titre": "Fiche des progrès", "pdf": "MODAF05_Fiche_des_Progrès.pdf"}
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
            {"titre": "Semaine 2 : Audio Ancrage", "pdf": "assets/Audio_Ancrage.mp3"}, 
            {"titre": "Echelle d'anxiété", "pdf": "assets/Echelle_d'anxiété.pdf"},
            {"titre": "Echelle de dépression", "pdf": "Echelle_de_dépression.pdf"},
            {"titre": "Echelle des autres émotions négatives", "pdf": "Echelle_des_autres_émotions_négatives.pdf"},
            {"titre": "Echelle des émotions positives", "pdf": "Echelle_des_émotions_positives.pdf"},
            {"titre": "Fiche des progrès", "pdf": "MODAF05_Fiche_des_Progrès.pdf"}
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
            {"titre": "Pleine Conscience (Suite)", "pdf": "assets/MOD3_Fiche_Pleine_Conscience_des_émotions.pdf"}, 
            {"titre": "Echelle d'anxiété", "pdf": "assets/Echelle_d'anxiété.pdf"},
            {"titre": "Echelle de dépression", "pdf": "Echelle_de_dépression.pdf"},
            {"titre": "Echelle des autres émotions négatives", "pdf": "Echelle_des_autres_émotions_négatives.pdf"},
            {"titre": "Echelle des émotions positives", "pdf": "Echelle_des_émotions_positives.pdf"},
            {"titre": "Fiche des progrès", "pdf": "MODAF05_Fiche_des_Progrès.pdf"}
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
            {"titre": "Contrer les comportements", "pdf": "assets/MOD5.50_Fiche_Contrer_les_comportements_émotionnels.pdf"}, 
            {"titre": "Echelle d'anxiété", "pdf": "assets/Echelle_d'anxiété.pdf"},
            {"titre": "Echelle de dépression", "pdf": "Echelle_de_dépression.pdf"},
            {"titre": "Echelle des autres émotions négatives", "pdf": "Echelle_des_autres_émotions_négatives.pdf"},
            {"titre": "Echelle des émotions positives", "pdf": "Echelle_des_émotions_positives.pdf"},
            {"titre": "Fiche des progrès", "pdf": "MODAF05_Fiche_des_Progrès.pdf"}
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
            {"titre": "Exercices activer sensations physiques", "pdf": "assets/MOD06_Fiche_Exercices_pour_activer_les_sensations_physiques.pdf"},
            {"titre": "Echelle d'anxiété", "pdf": "assets/Echelle_d'anxiété.pdf"},
            {"titre": "Echelle de dépression", "pdf": "Echelle_de_dépression.pdf"},
            {"titre": "Echelle des autres émotions négatives", "pdf": "Echelle_des_autres_émotions_négatives.pdf"},
            {"titre": "Echelle des émotions positives", "pdf": "Echelle_des_émotions_positives.pdf"},
            {"titre": "Fiche des progrès", "pdf": "MODAF05_Fiche_des_Progrès.pdf"}
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
            {"titre": "Enregistrement Pratique Exposition", "pdf": "assets/MOD07.2_Fiche_Enregistrement_de_la_Pratique_d'Exposition_Émotionnelle.pdf"}, 
            {"titre": "Echelle d'anxiété", "pdf": "assets/Echelle_d'anxiété.pdf"},
            {"titre": "Echelle de dépression", "pdf": "Echelle_de_dépression.pdf"},
            {"titre": "Echelle des autres émotions négatives", "pdf": "Echelle_des_autres_émotions_négatives.pdf"},
            {"titre": "Echelle des émotions positives", "pdf": "Echelle_des_émotions_positives.pdf"},
            {"titre": "Fiche des progrès", "pdf": "MODAF05_Fiche_des_Progrès.pdf"}
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
            {"titre": "Fin du traitement", "details": "A venir", "pdfs": []}
        ],

        "taches_domicile": []
    }
}

