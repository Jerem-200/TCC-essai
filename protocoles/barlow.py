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
        "titre": "☁️ Échelle de Dépression (ODSIS)",
        "description": "Entourez le numéro correspondant à la réponse qui décrit le mieux votre expérience de cette dernière semaine.",
        "type": "qcm_oasis",  # On réutilise le type QCM
        "questions": [
            {
                "id": "freq_dep",
                "label": "1. Au cours de la dernière semaine, combien de fois vous êtes-vous senti déprimé ?",
                "options": [
                    "0 = Aucune dépression au cours de la dernière semaine.",
                    "1 = Dépression peu fréquente. Je me suis senti(e) déprimé(e) à quelques reprises.",
                    "2 = Dépression occasionnelle. Je me sentais déprimé(e) la plupart du temps.",
                    "3 = Dépression fréquente. Je me sentais déprimé(e) la plupart du temps.",
                    "4 = Dépression constante. Je me sentais déprimé(e) tout le temps."
                ]
            },
            {
                "id": "intensite_dep",
                "label": "2. Lorsque vous vous êtes senti déprimé, quelle était l'intensité ou la gravité ?",
                "options": [
                    "0 = Peu ou Aucune : La dépression était absente ou à peine perceptible.",
                    "1 = Léger : La dépression était à un niveau bas.",
                    "2 = Modéré : La dépression était parfois intense.",
                    "3 = Sévère : La dépression était intense la plupart du temps.",
                    "4 = Extrême : La dépression était écrasante."
                ]
            },
            {
                "id": "interet_dep",
                "label": "3. À quelle fréquence avez-vous eu des difficultés à vous intéresser à des activités ?",
                "options": [
                    "0 = Aucun : Je n'ai eu aucune difficulté à m'engager ou à m'intéresser à des activités.",
                    "1 = Peu fréquent : Quelques fois j'ai eu de la difficulté... Mon style de vie n'a pas été affecté.",
                    "2 = Occasionnel : J'ai eu de la difficulté... Mon style de vie n'a changé que de façon mineure.",
                    "3 = Fréquent : J'ai beaucoup de difficulté... J'ai apporté des changements importants à mon style de vie.",
                    "4 = Tout le temps : J'ai été incapable de participer... Mon mode de vie a été largement affecté."
                ]
            },
            {
                "id": "interf_travail_dep",
                "label": "4. Perturbation de la capacité à faire les choses (travail/école/maison) ?",
                "options": [
                    "0 = Aucun : Aucune interférence due à la dépression.",
                    "1 = Léger : Ma dépression a causé des interférences... mais tout ce qui doit être fait se fait encore.",
                    "2 = Modéré : Ma dépression interfère définitivement avec les tâches. Peu de choses se font aussi bien que par le passé.",
                    "3 = Sévère : Ma dépression a vraiment changé ma capacité à faire avancer les choses. Beaucoup de choses ne sont pas faites.",
                    "4 = Extrême : Ma dépression est devenue invalidante. Incapable d'accomplir des tâches (démission, dettes, etc.)."
                ]
            },
            {
                "id": "interf_social_dep",
                "label": "5. Interférence avec la vie sociale et les relations ?",
                "options": [
                    "0 = Aucun : Ma dépression n'affecte pas mes relations.",
                    "1 = Léger : Interfère légèrement. Certaines relations ont souffert mais vie sociale épanouie.",
                    "2 = Modéré : Quelques interférences. Je ne dépense pas autant de temps avec les autres mais je socialise encore.",
                    "3 = Sévère : Mes amitiés ont beaucoup souffert. Je n'aime pas les activités sociales. Je socialise très peu.",
                    "4 = Extrême : Ma dépression a complètement perturbé mes activités sociales. Relations terminées ou famille tendue."
                ]
            }
        ]
    },

    "Autres Émotions Négatives": {
        "titre": "Autres Émotions Négatives (Facultatif)",
        "description": "Identifiez une émotion avec laquelle vous avez lutté (ex: colère, honte, jalousie). Répondez ensuite aux questions pour cette émotion spécifique.",
        "type": "qcm_oasis",
        "ask_emotion": True, # <--- SIGNAL POUR AFFICHER LE CHAMP TEXTE
        "questions": [
            {
                "id": "freq_other",
                "label": "1. Au cours de la dernière semaine, combien de fois vous êtes-vous senti(e) ainsi ?",
                "options": [
                    "0 = Non : Je n'ai pas ressenti cette émotion la semaine dernière.",
                    "1 = Peu fréquent : J'ai ressenti cette émotion plusieurs fois.",
                    "2 = Occasionnel : J'ai ressenti cette émotion la plupart du temps.",
                    "3 = Fréquent : J'ai ressenti cette émotion la plupart du temps (intensité plus forte).",
                    "4 = Constante : J'ai ressenti cette émotion tout le temps."
                ]
            },
            {
                "id": "intensite_other",
                "label": "2. Lorsque vous avez ressenti cette émotion, quelle était son intensité ?",
                "options": [
                    "0 = Peu ou Aucune : Cette émotion était absente ou à peine perceptible.",
                    "1 = Léger : Cette émotion était à un niveau bas.",
                    "2 = Modéré : Cette émotion était parfois intense.",
                    "3 = Sévère : Cette émotion était intense la plupart du temps.",
                    "4 = Extrême : Cette émotion était écrasante."
                ]
            },
            {
                "id": "interf_activites_other",
                "label": "3. À quelle fréquence avez-vous eu du mal à vous intéresser à des activités à cause de cette émotion ?",
                "options": [
                    "0 = Aucune : Je n'ai eu aucune difficulté à m'engager ou à m'intéresser.",
                    "1 = Peu fréquent : À quelques reprises, j'ai eu de la difficulté. Mon style de vie n'a pas été affecté.",
                    "2 = Occasionnel : J'ai eu de la difficulté. Mon style de vie n'a changé que de façon mineure.",
                    "3 = Fréquent : J'ai beaucoup de difficulté. J'ai apporté des changements importants à mon style de vie.",
                    "4 = Tout le temps : J'ai été incapable de participer. Mon mode de vie a été largement affecté."
                ]
            },
            {
                "id": "interf_travail_other",
                "label": "4. Dans quelle mesure cette émotion a-t-elle gêné votre capacité à faire les choses (travail/école/maison) ?",
                "options": [
                    "0 = Aucune : Aucune interférence due à cette émotion.",
                    "1 = Léger : Cette émotion a causé des interférences, mais tout ce qui doit être fait se fait encore.",
                    "2 = Modéré : Cette émotion interfère définitivement avec les tâches. La plupart des choses se font encore.",
                    "3 = Sévère : Cette émotion a vraiment changé ma capacité à faire avancer les choses.",
                    "4 = Extrême : Cette émotion est devenue invalidante. Incapable d'accomplir des tâches."
                ]
            },
            {
                "id": "interf_social_other",
                "label": "5. Dans quelle mesure cette émotion a-t-elle gêné votre vie sociale et vos relations ?",
                "options": [
                    "0 = Aucune : Cette émotion n'affecte pas mes relations.",
                    "1 = Léger : Cette émotion interfère légèrement avec mes relations.",
                    "2 = Modéré : J'ai vécu quelques interférences avec ma vie sociale, mais je socialise encore.",
                    "3 = Sévère : Mes amitiés et autres relations ont beaucoup souffert à cause de cette émotion.",
                    "4 = Extrême : Cette émotion a complètement perturbé mes activités sociales."
                ]
            }
        ]
    },

"Émotions Positives": {
        "titre": "🌞 Émotions Positives (ModAF - Facultatif)",
        "description": "Pour chaque élément, sélectionnez la réponse qui décrit le mieux votre expérience au cours de la semaine écoulée concernant les émotions positives (bonheur, excitation, joie, etc.).",
        "type": "qcm_oasis",
        "questions": [
            {
                "id": "freq_pos",
                "label": "1. Au cours de la dernière semaine, à quelle fréquence avez-vous ressenti des émotions positives ?",
                "options": [
                    "0 = Aucune émotion positive au cours de la dernière semaine.",
                    "1 = Émotions positives peu fréquentes. Ressentir des émotions positives à quelques reprises.",
                    "2 = Émotions positives occasionnelles. Ressentir des émotions positives la plupart du temps.",
                    "3 = Émotions positives fréquentes. A ressenti des émotions positives la plupart du temps.",
                    "4 = Émotions positives constantes. Ressentir des émotions positives tout le temps."
                ]
            },
            {
                "id": "intensite_pos",
                "label": "2. Au cours de la dernière semaine, lorsque vous avez ressenti des émotions positives, quelle était leur intensité ?",
                "options": [
                    "0 = Peu ou Aucune : Les émotions positives étaient absentes ou à peine perceptibles.",
                    "1 = Léger : Les émotions positives étaient à un niveau bas.",
                    "2 = Bon : Les émotions positives étaient parfois fortes.",
                    "3 = Excellent : Les émotions positives étaient fortes la plupart du temps.",
                    "4 = Excellent : Les émotions positives étaient fortes la plupart du temps."
                ]
            },
            {
                "id": "interet_pos",
                "label": "3. À quelle fréquence vous êtes-vous engagé ou avez-vous maintenu votre intérêt pour des activités grâce à des émotions positives ?",
                "options": [
                    "0 = Aucune : J'ai eu de la difficulté à m'engager ou à m'intéresser à des activités... en raison de très peu d'émotions positives.",
                    "1 = Peu fréquent : J'ai participé ou maintenu, à quelques reprises, mon intérêt pour des activités grâce à des émotions positives.",
                    "2 = Occasionnel : Je me suis engagé ou j'ai maintenu de temps en temps mon intérêt pour des activités en raison d'émotions positives.",
                    "3 = Fréquent : Je m'engage fréquemment ou maintiens mon intérêt pour des activités en raison d'émotions positives.",
                    "4 = Tout le temps : Les émotions positives m'aident à m'engager ou à maintenir mon intérêt pour presque toutes mes activités."
                ]
            },
            {
                "id": "capacite_pos",
                "label": "4. Dans quelle mesure vos émotions positives ont-elles amélioré votre capacité à faire les choses (travail, école, maison) ?",
                "options": [
                    "0 = Aucun : Aucune amélioration au travail/à la maison/à l'école grâce aux émotions positives.",
                    "1 = Léger : Mes émotions positives ont amélioré certains aspects du travail/de la maison/de l'école.",
                    "2 = Bien : Mes émotions positives augmentent définitivement le plaisir dans mes tâches.",
                    "3 = Excellent : Mes émotions positives ont vraiment changé ma capacité à faire avancer les choses pour le mieux.",
                    "4 = Excellent : Mes émotions positives ont amélioré ma qualité de vie de la meilleure façon possible."
                ]
            },
            {
                "id": "social_pos",
                "label": "5. Dans quelle mesure les émotions positives ont-elles amélioré votre vie sociale et vos relations ?",
                "options": [
                    "0 = Aucun : Mes émotions positives n'ont pas affecté mes relations.",
                    "1 = Léger : Mes émotions positives améliorent légèrement mes relations.",
                    "2 = Bon : J'ai ressenti une certaine amélioration dans ma vie sociale grâce à des émotions positives.",
                    "3 = Excellent : Mes amitiés et autres relations se sont beaucoup améliorées grâce à mes émotions positives.",
                    "4 = Excellent : Mes émotions positives ont complètement amélioré mes activités sociales et mes relations."
                ]
            }
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

        "exercices": [
            {
                "id": "fiche_objectifs",
                "titre": "🎯 Fiche : Objectifs du Traitement",
                "type": "fiche_objectifs_traitement", # Type spécial
                "description": "Définissez vos problèmes principaux et transformez-les en objectifs concrets."
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

        "exercices": [
            {
                "id": "fiche_arc",
                "titre": "🌈 Fiche : Suivre mon ARC émotionnel",
                "type": "fiche_arc_emotionnel", # Nouveau type technique
                "description": "Analysez vos expériences émotionnelles : Antécédents (Déclencheurs) -> Réponses -> Conséquences."
            }
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

        "exercices": [
            {
                "id": "fiche_pleine_conscience",
                "titre": "🧘 Fiche : Pleine conscience des émotions",
                "type": "fiche_pleine_conscience", # Type technique unique
                "description": "Enregistrez votre expérience après vos exercices (Initiation, Induction d'humeur, Ancrage)."
            }
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

        "exercices": [
            {
                "id": "fiche_flexibilite",
                "titre": "🧠 Fiche : Flexibilité Cognitive",
                "type": "fiche_flexibilite_cognitive", # Nouveau type
                "description": "Identifiez vos pensées pièges et trouvez des interprétations alternatives plus réalistes."
            }
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

        "exercices": [
            {
                "id": "fiche_contrer_comportements",
                "titre": "🛡️ Fiche : Contrer les comportements",
                "type": "fiche_contrer_comportements", 
                "description": "Identifiez vos comportements émotionnels habituels et planifiez des actions alternatives (Actions opposées)."
            }
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

        "exercices": [
            {
                "id": "fiche_sensations",
                "titre": "🌪️ Fiche : Activer les sensations physiques",
                "type": "fiche_sensations_physiques", 
                "description": "Réalisez les exercices d'induction (Hyperventilation, Tourner...) et notez vos réactions."
            }
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

        "exercices": [
            {
                "id": "fiche_hierarchie",
                "titre": "📈 Fiche : Hiérarchie d'exposition",
                "type": "fiche_hierarchie_exposition", 
                "description": "Listez les situations que vous évitez et classez-les par ordre de difficulté (1 = La pire)."
            },

            {
                "id": "fiche_pratique_expo",
                "titre": "🎬 Fiche : Enregistrement d'Exposition",
                "type": "fiche_enregistrement_exposition", 
                "description": "Préparez votre exposition (Pensées, Comportements) et faites le bilan après l'exercice."
            }
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

        "exercices": [
            {
                "id": "fiche_evaluation_progres",
                "titre": "🏆 Fiche : Évaluation des progrès",
                "type": "fiche_evaluation_progres", # Nouveau type
                "description": "Faites le bilan de vos compétences (Pleine conscience, Flexibilité...) et identifiez vos axes de progrès."
            },

            {
                "id": "fiche_plan_maintien",
                "titre": "📅 Fiche : Plan de maintien",
                "type": "fiche_plan_maintien", # Nouveau type
                "description": "Définissez votre plan d'action concret pour continuer à pratiquer après le programme."
            }
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

