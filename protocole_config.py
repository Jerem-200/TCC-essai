# ==============================================================================
# CONFIGURATION DU PROTOCOLE UNIFIÉ (BARLOW) - VERSION COMPLÈTE
# ==============================================================================

PROTOCOLE_BARLOW = {
    "module0": {
        "titre": "ModAF: Analyse fonctionnelle et introduction",
        "objectifs": """
        - Mieux comprendre les difficultés de votre patient et le conceptualiser dans un cadre transdiagnostique.
        - Identifier : les expériences d'émotions inconfortables, les réactions aversives/croyances négatives sur les expériences émotionnelles, et les efforts pour éviter ou échapper à des émotions inconfortables.
        - Présenter aux patients le programme et les procédures de traitement.
        """,
        "outils": """
        - Fiche de Conceptualisation de cas
        - Fiche Questions Émotions négatives, Aversion et Comportement
        - Échelles (Anxiété, Dépression, Autres émotions, Émotions positives)
        - Fiche des Progrès
        """,
        "etapes_contenu": [
            {
                "titre": "Examen des plaintes et Analyse fonctionnelle initiale",
                "desc": "Bref examen des préoccupations. Analyse de la nature des symptômes présentés.",
                "pdf": "assets/L'analyse_fonctionnelle.pdf"
            },
            {
                "titre": "Présentation de la justification du traitement",
                "desc": "Identifier émotions fortes, aversion et évitement. Remplir la Fiche de Conceptualisation.",
                "pdf": "assets/MODAF10_Fiche_de_conceptualisation_thérapeute.pdf"
            },
            {
                "titre": "Émotions fréquentes, tendues et indésirables",
                "desc": "Évaluer l'éventail complet des émotions (anxiété, tristesse, colère, etc.) et leur fréquence.",
                "pdf": "assets/ModAF_Fiche_Questions_Emotions_négatives,_aversion_et_Comportement.pdf"
            },
            {
                "titre": "Réactions négatives et Efforts pour éviter",
                "desc": "Explorer l'aversion pour les émotions et les stratégies d'évitement (manifeste, subtil, cognitif, signaux de sécurité).",
                "pdf": None
            },
            {
                "titre": "Objectifs du programme et Format",
                "desc": "Expliquer le but (mieux comprendre et tolérer) et le format (séances, tâches à domicile).",
                "pdf": None
            }
        ],
        "devoirs": [
            {"tache": "Remplir l'échelle d'anxiété", "pdf": "assets/Echelle_d'anxiété.pdf"},
            {"tache": "Remplir l'échelle de dépression", "pdf": "assets/Echelle_de_dépression.pdf"},
            {"tache": "Commencer la Fiche des Progrès", "pdf": "assets/MODAF05_Fiche_des_Progrès.pdf"},
            {"tache": "Échelles optionnelles (Autres émotions / Positives)", "pdf": "assets/Echelle_des_autres_émotions_négatives.pdf"}
        ]
    },

    "module1": {
        "titre": "Module 1 : Fixer des objectifs et maintenir la motivation",
        "objectifs": """
        - Discuter de l'importance de la motivation pour le résultat du traitement.
        - Aider les patients à identifier des objectifs concrets à atteindre.
        - Aider les patients à définir des étapes gérables.
        - Aider les patients à explorer les avantages et les coûts de changer.
        """,
        "outils": """
        - Fiche: Objectifs de traitement
        - Fiche: Balances décisionnelles
        - Échelles (Anxiété, Dépression...)
        """,
        "etapes_contenu": [
            {
                "titre": "Motivation et engagement",
                "desc": "Discuter de l'incertitude et de la capacité à terminer le programme.",
                "pdf": "assets/Module_1_Fixer_des_objectifs_et_maintenir_la_motivation.pdf"
            },
            {
                "titre": "Clarifier les principaux problèmes et fixer des objectifs",
                "desc": "Identifier des objectifs précis, concrets et gérables (ex: 'participer à des réunions' vs 'être moins anxieux').",
                "pdf": "assets/MOD1.10_Fiche_Objectifs_du_traitement.pdf"
            },
            {
                "titre": "Feuille de travail sur la motivation et balance décisionnelle",
                "desc": "Explorer l'ambivalence du changement (avantages/inconvénients).",
                "pdf": "assets/MOD1.20_Fiche_balance_motivationnelle.pdf"
            }
        ],
        "devoirs": [
            {"tache": "Identifier des objectifs supplémentaires", "pdf": "assets/MOD1.10_Fiche_Objectifs_du_traitement.pdf"},
            {"tache": "Surveiller les progrès (Échelles)", "pdf": "assets/MODAF05_Fiche_des_Progrès.pdf"}
        ]
    },

    "module2": {
        "titre": "Module 2 : Comprendre les émotions",
        "objectifs": """
        - Développer une compréhension plus flexible et précise des émotions et de leur fonction.
        - Développer une plus grande conscience des émotions (interactions sensations, pensées, comportements).
        - Identifier les déclencheurs et les conséquences (ARC).
        """,
        "outils": """
        - Fiche: Modèle à Trois Composantes de l'Émotion
        - Fiche: Suivre mon ARC émotionnel
        - Échelles
        """,
        "etapes_contenu": [
            {
                "titre": "Psychoéducation - La nature des émotions",
                "desc": "Expliquer le rôle adaptatif et fonctionnel des émotions.",
                "pdf": "assets/Module_2_Comprendre_les_émotions.pdf"
            },
            {
                "titre": "Le modèle à trois composants",
                "desc": "Décomposer en : Pensées, Sensations physiques, Comportements.",
                "pdf": "assets/MOD2.1 Fiche_Modèle_à_trois_composantes_de_l'Emotion.pdf"
            },
            {
                "titre": "L'ARC des émotions",
                "desc": "Identifier les Antécédents, les Réponses, et les Conséquences (court vs long terme).",
                "pdf": "assets/MOD2.2_Fiche_suivre_mon_ARC_émotionnel.pdf"
            },
            {
                "titre": "Réponses apprises et spirale de l'évitement",
                "desc": "Comprendre comment l'évitement empêche le nouvel apprentissage.",
                "pdf": "assets/Antécédents_émotions.pdf"
            }
        ],
        "devoirs": [
            {"tache": "Remplir Fiche: Modèle à Trois Composantes", "pdf": "assets/MOD2.1 Fiche_Modèle_à_trois_composantes_de_l'Emotion.pdf"},
            {"tache": "Remplir Fiche: Suivre mon ARC émotionnel", "pdf": "assets/MOD2.2_Fiche_suivre_mon_ARC_émotionnel.pdf"},
            {"tache": "Continuer à surveiller les progrès (Échelles)", "pdf": "assets/MODAF05_Fiche_des_Progrès.pdf"}
        ]
    },

    "module3": {
        "titre": "Module 3 : Pleine conscience de l'émotion",
        "objectifs": """
        - Apprendre à observer leurs expériences émotionnelles de manière objective et sans jugement.
        - Développer des compétences pour observer les émotions dans le contexte du moment présent.
        """,
        "outils": """
        - Fichiers audio méditations
        - Fiche Pleine conscience des émotions
        """,
        "etapes_contenu": [
            {
                "titre": "Introduction à la pleine conscience des émotions",
                "desc": "Approcher les émotions d'une manière non critique et centrée sur le présent.",
                "pdf": "assets/Module_3_La_pleine_conscience_des_émotions.pdf"
            },
            {
                "titre": "Méditation consciente des émotions",
                "desc": "Exercice pour observer pensées, sensations et comportements sans jugement.",
                "pdf": "assets/MOD_3_Script_Méditation_d'initiation.pdf"
            },
            {
                "titre": "Induction d'humeur consciente (Musique)",
                "desc": "Utiliser la musique pour évoquer des émotions et pratiquer la conscience.",
                "pdf": None
            },
            {
                "titre": "Ancrage au présent",
                "desc": "Choisir un signal (ex: respiration) pour revenir au présent quand l'émotion monte.",
                "pdf": "assets/MOD_3_Script_Méditation_Ancrage.pdf"
            }
        ],
        "devoirs": [
            {"tache": "Semaine 1: Pratiquer la méditation guidée (Audio)", "pdf": "assets/Audio_Méditation.mp3"},
            {"tache": "Semaine 2: Pratiquer l'induction d'humeur et l'Ancrage", "pdf": "assets/Audio_Ancrage.mp3"},
            {"tache": "Remplir Fiche: Pleine conscience des émotions", "pdf": "assets/MOD3_Fiche_Pleine_Conscience_des_émotions.pdf"}
        ]
    },

    "module4": {
        "titre": "Module 4 : La flexibilité cognitive",
        "objectifs": """
        - Expliquer la relation réciproque entre les pensées et les émotions.
        - Identifier les pensées automatiques et les pièges de pensée.
        - Accroître la flexibilité dans la pensée.
        """,
        "outils": """
        - Fiche: L'Image ambiguë
        - Fiche: Pratiquer la flexibilité cognitive
        - Fiche de la Flèche descendante
        """,
        "etapes_contenu": [
            {
                "titre": "Introduction à la flexibilité cognitive",
                "desc": "Comprendre que nos interprétations influencent nos émotions.",
                "pdf": "assets/Module_4_La_flexibilité_cognitive.pdf"
            },
            {
                "titre": "Exercice d'image ambiguë",
                "desc": "Illustrer la pensée automatique et générer des interprétations alternatives.",
                "pdf": "assets/MOD4.1_Fiche_Exercice_Image_ambiguë.pdf"
            },
            {
                "titre": "Pièges à penser",
                "desc": "Identifier : Inférence arbitraire (sauter aux conclusions) et Penser au pire (catastrophiser).",
                "pdf": None
            },
            {
                "titre": "Pratiquer la flexibilité cognitive",
                "desc": "Générer des alternatives (ex: 'Est-ce que c'est vrai ?', 'Que dirait un ami ?').",
                "pdf": "assets/MOD4.20_Fiche_Pratiquer_la_flexibilité_cognitive.pdf"
            }
        ],
        "devoirs": [
            {"tache": "Surveiller les pensées et pièges (Fiche Flexibilité)", "pdf": "assets/MOD4.20_Fiche_Pratiquer_la_flexibilité_cognitive.pdf"},
            {"tache": "Générer des interprétations alternatives", "pdf": "assets/MOD4.21_Exemple_Fiche_Pratiquer_la_flexibilité_cognitive.pdf"},
            {"tache": "Identifier les pensées fondamentales (Flèche descendante)", "pdf": "assets/MOD4.30_Exemple_Fiche_La_flèche_descendante.pdf"}
        ]
    },

    "module5": {
        "titre": "Module 5 : Contrer les comportements émotionnels",
        "objectifs": """
        - Identifier les comportements émotionnels.
        - Discuter des effets paradoxaux (renforcement négatif).
        - Développer des actions alternatives.
        """,
        "outils": """
        - Fiche: Liste des comportements émotionnels
        - Fiche: Contrer les comportements émotionnels
        """,
        "etapes_contenu": [
            {
                "titre": "Discussion sur les comportements émotionnels",
                "desc": "Comprendre les comportements pour gérer les émotions fortes (Évitement, Comportements subtils, Signaux de sécurité).",
                "pdf": "assets/Module_5_Contrer_les_comportements_émotionnels.pdf"
            },
            {
                "titre": "Nature adaptative vs Inadaptée",
                "desc": "Effets à court terme (soulagement) vs long terme (maintien du trouble).",
                "pdf": "assets/MOD5.10_Fiche_Liste_des_comportements_émotionnels.pdf"
            },
            {
                "titre": "Démonstration d'évitement (Suppression de pensée)",
                "desc": "Exercice montrant que supprimer une pensée la rend plus forte.",
                "pdf": None
            },
            {
                "titre": "Briser le cycle : Actions alternatives",
                "desc": "S'engager dans une action différente et souvent opposée.",
                "pdf": "assets/MOD5.50_Fiche_Contrer_les_comportements_émotionnels.pdf"
            }
        ],
        "devoirs": [
            {"tache": "Identifier les comportements (Fiche Liste)", "pdf": "assets/MOD5.10_Fiche_Liste_des_comportements_émotionnels.pdf"},
            {"tache": "Pratiquer les actions alternatives (Fiche Contrer)", "pdf": "assets/MOD5.50_Fiche_Contrer_les_comportements_émotionnels.pdf"}
        ]
    },

    "module6": {
        "titre": "Module 6 : Comprendre et Affronter Sensations physiques",
        "objectifs": """
        - Comprendre le rôle des sensations physiques.
        - Identifier les sensations internes associées aux émotions.
        - Exposition intéroceptive : augmenter la tolérance.
        """,
        "outils": """
        - Fiche: Exercices pour activer les sensations physiques
        - Paille, Chronomètre...
        """,
        "etapes_contenu": [
            {
                "titre": "Sensations physiques et réponse émotionnelle",
                "desc": "Lien entre interprétation des sensations (danger) et intensification de l'émotion.",
                "pdf": "assets/Module_6_ Comprendre_et_accepter_les_sensations_physiques.pdf"
            },
            {
                "titre": "Évitement des sensations physiques",
                "desc": "Identifier l'évitement (caféine, exercice, émotions fortes).",
                "pdf": None
            },
            {
                "titre": "Exercices d'induction des symptômes",
                "desc": "Identifier les exercices qui reproduisent les sensations (hyperventilation, tourner la tête...).",
                "pdf": "assets/MOD06_Fiche_Exercices_pour_activer_les_sensations_physiques.pdf"
            },
            {
                "titre": "Expositions répétées (Procédure)",
                "desc": "S'engager dans les exercices jusqu'à ce que la détresse diminue ou que les attentes changent.",
                "pdf": None
            }
        ],
        "devoirs": [
            {"tache": "S'engager dans des expositions répétées", "pdf": "assets/MOD06_Fiche_Exercices_pour_activer_les_sensations_physiques.pdf"},
            {"tache": "Attribuer trois brefs exercices à faire à la maison", "pdf": None}
        ]
    },

    "module7": {
        "titre": "Module 7 : Exposition aux émotions",
        "objectifs": """
        - Comprendre le but des expositions émotionnelles.
        - Développer une hiérarchie de peur et d'évitement.
        - Concevoir et réaliser des exercices d'exposition.
        """,
        "outils": """
        - Fiche: Hiérarchie d'exposition aux émotions
        - Fiche: Enregistrement de la pratique
        """,
        "etapes_contenu": [
            {
                "titre": "Introduction aux expositions",
                "desc": "L'objectif est l'émotion elle-même, pas la situation. Nouvel apprentissage.",
                "pdf": "assets/Module_7_Les_expositions_aux_émotions.pdf"
            },
            {
                "titre": "Types d'exposition",
                "desc": "Basée sur la situation, Imaginaire, Sensations physiques.",
                "pdf": "assets/MOD07.01_Fiche_Hiérarchie_d'exposition_aux_émotions.pdf"
            },
            {
                "titre": "Mener des expositions en séance",
                "desc": "Préparation, Exposition (éliminer l'évitement), Debriefing (10 min).",
                "pdf": "assets/MOD07.2_Fiche_Enregistrement_de_la_Pratique_d'Exposition_Émotionnelle.pdf"
            },
            {
                "titre": "Transférer dans le contexte réel",
                "desc": "Concevoir des expositions à pratiquer en dehors de la séance.",
                "pdf": None
            }
        ],
        "devoirs": [
            {"tache": "Pratiquer les expositions (3x/semaine)", "pdf": "assets/MOD07.01_Fiche_Hiérarchie_d'exposition_aux_émotions.pdf"},
            {"tache": "Enregistrer la pratique", "pdf": "assets/MOD07.2_Fiche_Enregistrement_de_la_Pratique_d'Exposition_Émotionnelle.pdf"}
        ]
    },

    "module8": {
        "titre": "Module 8 : Bilan et perspectives futures",
        "objectifs": """
        - Passer en revue les concepts et compétences.
        - Évaluer les progrès.
        - Établir des objectifs à long terme.
        """,
        "outils": """
        - Fiche Objectifs du traitement (Revue)
        - Fiche Plan pour maintenir et continuer à progresser
        """,
        "etapes_contenu": [
            {
                "titre": "Revue des compétences acquises",
                "desc": "Scénario pertinent pour vérifier la capacité à gérer les émotions.",
                "pdf": "assets/Module_8_Bilan_et_perspectives_futures.pdf"
            },
            {
                "titre": "Évaluation des progrès",
                "desc": "Comparer avec les objectifs du début (Mod1).",
                "pdf": "assets/MOD8.1_Fiche_Evaluation_des_Progrès.pdf"
            },
            {
                "titre": "Anticiper les difficultés futures",
                "desc": "Comprendre que la fluctuation des symptômes est normale (pas une rechute).",
                "pdf": None
            },
            {
                "titre": "Poursuite de la pratique et Fin",
                "desc": "Identifier les domaines nécessitant une pratique supplémentaire. Plan de maintien.",
                "pdf": "assets/MOD8.2_Fiche_Plan_pour_maintenir_et_continuer_à_progresser.pdf"
            }
        ],
        "devoirs": [
            {"tache": "Appliquer le plan de maintien", "pdf": "assets/MOD8.2_Fiche_Plan_pour_maintenir_et_continuer_à_progresser.pdf"},
            {"tache": "Continuer à surveiller les progrès (Échelles)", "pdf": "assets/MODAF05_Fiche_des_Progrès.pdf"}
        ]
    }
}