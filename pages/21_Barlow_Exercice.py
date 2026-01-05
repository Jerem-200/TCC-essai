import streamlit as st
import time
from datetime import datetime
# ON RETIRE L'IMPORT DB D'ICI POUR ACCÉLÉRER LE CHARGEMENT INITIAL
# from connect_db import sauvegarder_reponse_hebdo <--- C'est ça qui ralentissait !

# Configuration de la page "Focus"
st.set_page_config(page_title="Exercice en cours", page_icon="✏️", layout="wide")

# Masquer la sidebar
st.markdown("<style>[data-testid='stSidebarNav'] {display: none;}</style>", unsafe_allow_html=True)

# 1. SÉCURITÉ
if "authentifie" not in st.session_state or not st.session_state.authentifie:
    st.warning("🔒 Connexion requise.")
    st.stop()

# 2. RÉCUPÉRATION
if "exercice_actif" not in st.session_state or not st.session_state.exercice_actif:
    st.info("Aucun exercice sélectionné.")
    if st.button("⬅️ Retour"): st.switch_page("pages/00_Mon_Parcours.py")
    st.stop()

data_ctx = st.session_state.exercice_actif
exo_data = data_ctx["exo_data"]
current_user = st.session_state.user_id

# 3. HEADER
c1, c2 = st.columns([1, 6])
with c1:
    if st.button("⬅️ Retour"): 
        # On dit qu'on veut revenir sur l'onglet Protocole
        st.session_state["target_tab"] = "🗺️ Protocole" 
        st.switch_page("streamlit_app.py")
with c2:
    st.header(f"{exo_data['titre']}")

# =========================================================
# LOGIQUE DES OUTILS
# =========================================================

# --- FONCTION DE SAUVEGARDE MODIFIÉE ---
def sauver_et_quitter(payload, nom_exo):
    with st.spinner("Sauvegarde en cours..."):
        from connect_db import sauvegarder_reponse_hebdo
        
        if sauvegarder_reponse_hebdo(current_user, f"Exercice - {nom_exo}", "N/A", payload):
            st.toast("✅ Sauvegardé !", icon='🎉')
            time.sleep(1)
            # On force le retour sur l'onglet Protocole
            st.session_state["target_tab"] = "🗺️ Protocole"
            st.switch_page("streamlit_app.py") # <--- ON RENVOIE VERS L'ACCUEIL GLOBAL

# --- TYPE 1 : FICHE OBJECTIFS ---
if exo_data["type"] == "fiche_objectifs_traitement":
    if "temp_main_pb" not in st.session_state: st.session_state.temp_main_pb = ""
    if "temp_objectives_list" not in st.session_state: st.session_state.temp_objectives_list = []
    
    st.markdown("#### 1️⃣ Le Problème Principal")
    def update_pb(): st.session_state.temp_main_pb = st.session_state.widget_main_pb
    st.text_area("Votre problème principal :", value=st.session_state.temp_main_pb, height=70, key="widget_main_pb", on_change=update_pb)

    st.divider()
    st.markdown("#### 2️⃣ Ajouter des Objectifs")
    with st.form("form_add_obj", clear_on_submit=True):
        c_obj, c_step = st.columns(2)
        with c_obj: new_obj_txt = st.text_input("Nouvel Objectif :")
        with c_step: new_steps_txt = st.text_area("Étapes (une par ligne) :", height=80)
        if st.form_submit_button("➕ Ajouter"):
            if new_obj_txt:
                st.session_state.temp_objectives_list.append({"objectif": new_obj_txt, "etapes": [s.strip() for s in new_steps_txt.split('\n') if s.strip()]})
                st.rerun()
    
    if st.session_state.temp_objectives_list:
        st.markdown("##### 📋 Liste à enregistrer :")
        for i, item in enumerate(st.session_state.temp_objectives_list):
            with st.expander(f"🎯 {item['objectif']}", expanded=False):
                for s in item['etapes']: st.write(f"- {s}")
                if st.button("Supprimer", key=f"del_obj_{i}"):
                    st.session_state.temp_objectives_list.pop(i); st.rerun()
        
        st.divider()
        if st.button("💾 Sauvegarder définitivement", type="primary"):
            payload = {"type_exercice": "Objectifs Traitement", "probleme_principal": st.session_state.temp_main_pb, "liste_objectifs": st.session_state.temp_objectives_list}
            
            # On vide la mémoire locale avant de quitter
            st.session_state.temp_main_pb = ""
            st.session_state.temp_objectives_list = []
            
            # Appel de la sauvegarde optimisée
            sauver_et_quitter(payload, exo_data['titre'])

# --- TYPE 2 : ARC ÉMOTIONNEL ---
elif exo_data["type"] == "fiche_arc_emotionnel":
    if "temp_arc_list" not in st.session_state: st.session_state.temp_arc_list = []
    with st.form("form_add_arc", clear_on_submit=True):
        st.markdown("**🅰️ Antécédents**")
        c_a1, c_a2 = st.columns([1, 2])
        with c_a1: date_evt = st.text_input("Date/Heure :")
        with c_a2: antecedent = st.text_area("Déclencheur :", height=70)
        st.markdown("**⚡ Réponses**")
        c_r1, c_r2, c_r3 = st.columns(3)
        with c_r1: pensees = st.text_area("💭 Pensées")
        with c_r2: sensations = st.text_area("💓 Sensations")
        with c_r3: comportements = st.text_area("🏃 Comportements")
        st.markdown("**🏁 Conséquences**")
        c_c1, c_c2 = st.columns(2)
        with c_c1: c_court = st.text_area("Court terme")
        with c_c2: c_long = st.text_area("Long terme")
        if st.form_submit_button("Ajouter"):
            if antecedent:
                st.session_state.temp_arc_list.append({"date": date_evt, "antecedent": antecedent, "pensees": pensees, "sensations": sensations, "comportements": comportements, "c_court": c_court, "c_long": c_long})
                st.rerun()

    if st.session_state.temp_arc_list:
        st.markdown("##### 📋 Situations :")
        for i, arc in enumerate(st.session_state.temp_arc_list):
            with st.expander(f"{arc['date']} - {arc['antecedent'][:30]}..."):
                if st.button("Supprimer", key=f"del_arc_{i}"): st.session_state.temp_arc_list.pop(i); st.rerun()
        
        st.divider()
        if st.button("💾 Sauvegarder ARC", type="primary"):
            payload = {"type_exercice": "ARC Emotionnel", "liste_arc": st.session_state.temp_arc_list}
            st.session_state.temp_arc_list = [] # Reset
            sauver_et_quitter(payload, exo_data['titre'])

# --- TYPE 3 : PLEINE CONSCIENCE ---
elif exo_data["type"] == "fiche_pleine_conscience":
    if "temp_mindfulness_list" not in st.session_state: st.session_state.temp_mindfulness_list = []

    st.markdown("#### ➕ Enregistrer une pratique")
    with st.form("form_add_mindful", clear_on_submit=True):
        c_m1, c_m2 = st.columns([1, 2])
        with c_m1: date_m = st.text_input("Date :", value=datetime.now().strftime("%d/%m"))
        with c_m2: type_exo = st.selectbox("Choix :", ["Initiation", "Induction", "Ancrage"])
        st.divider()
        c_obs1, c_obs2, c_obs3 = st.columns(3)
        with c_obs1: obs_pensees = st.text_area("💭 Pensées")
        with c_obs2: obs_sensations = st.text_area("💓 Sensations")
        with c_obs3: obs_comportements = st.text_area("🏃 Comportements")
        c_s1, c_s2 = st.columns(2)
        with c_s1: score_jugement = st.slider("Non-jugement (0-10)", 0, 10, 5)
        with c_s2: score_ancrage = st.slider("Ancrage (0-10)", 0, 10, 5)

        if st.form_submit_button("Ajouter"):
            st.session_state.temp_mindfulness_list.append({
                "date": date_m, "type_exo": type_exo,
                "pensees": obs_pensees, "sensations": obs_sensations, "comportements": obs_comportements,
                "score_jugement": score_jugement, "score_ancrage": score_ancrage
            })
            st.rerun()
            
    if st.session_state.temp_mindfulness_list:
        st.write(f"Enregistrés : {len(st.session_state.temp_mindfulness_list)}")
        if st.button("💾 Sauvegarder", type="primary"):
             payload = {"type_exercice": "Pleine Conscience", "liste_pratiques": st.session_state.temp_mindfulness_list}
             st.session_state.temp_mindfulness_list = []
             sauver_et_quitter(payload, exo_data['titre'])

# --- TYPE 4 : FLEXIBILITÉ ---
elif exo_data["type"] == "fiche_flexibilite_cognitive":
    if "temp_flex_list" not in st.session_state: st.session_state.temp_flex_list = []
    
    st.markdown("#### ➕ Analyser une pensée")
    with st.form("form_add_flex", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1: declencheur = st.text_area("Situation :")
        with c2: pensee = st.text_area("Pensée Automatique :")
        c3, c4 = st.columns(2)
        with c3: croyance = st.slider("Croyance (%)", 0, 100, 80)
        with c4: alternative = st.text_area("Alternative :")

        if st.form_submit_button("Ajouter"):
            if pensee:
                st.session_state.temp_flex_list.append({
                    "declencheur": declencheur, "pensee": pensee,
                    "croyance": croyance, "alternative": alternative
                })
                st.rerun()

    if st.session_state.temp_flex_list:
        st.write(f"Analyses prêtes : {len(st.session_state.temp_flex_list)}")
        for i, item in enumerate(st.session_state.temp_flex_list):
             st.caption(f"- {item['pensee']}")
             
        if st.button("💾 Sauvegarder", type="primary"):
             payload = {"type_exercice": "Flexibilité", "liste_flexibilite": st.session_state.temp_flex_list}
             st.session_state.temp_flex_list = []
             sauver_et_quitter(payload, exo_data['titre'])

# --- TYPE 5 : CONTRER COMPORTEMENTS ---
elif exo_data["type"] == "fiche_contrer_comportements":
    if "temp_behavior_list" not in st.session_state: st.session_state.temp_behavior_list = []
    
    st.markdown("#### ➕ Analyser un comportement")
    with st.form("form_add_beh", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1: situation = st.text_area("Situation :")
        with c2: emotion = st.text_input("Emotion :")
        c3, c4 = st.columns(2)
        with c3: comp_habituel = st.text_area("🔴 Habitude :")
        with c4: comp_alternatif = st.text_area("🟢 Alternative :")

        if st.form_submit_button("Ajouter"):
            st.session_state.temp_behavior_list.append({
                "situation": situation, "emotion": emotion,
                "comp_habituel": comp_habituel, "comp_alternatif": comp_alternatif
            })
            st.rerun()

    if st.session_state.temp_behavior_list:
        if st.button("💾 Sauvegarder", type="primary"):
             payload = {"type_exercice": "Contrer Comportements", "liste_comportements": st.session_state.temp_behavior_list}
             st.session_state.temp_behavior_list = []
             sauver_et_quitter(payload, exo_data['titre'])

# --- TYPE 6 : SENSATIONS ---
elif exo_data["type"] == "fiche_sensations_physiques":
    if "temp_sensations_list" not in st.session_state: st.session_state.temp_sensations_list = []
    
    with st.form("form_add_sens", clear_on_submit=True):
        type_induction = st.selectbox("Exercice :", ["Hyperventilation", "Paille", "Tourner", "Courir"])
        symptomes = st.text_area("Symptômes :")
        c1, c2 = st.columns(2)
        with c1: score_malaise = st.slider("Malaise", 0, 10, 0)
        with c2: score_resemblance = st.slider("Ressemblance", 0, 10, 0)

        if st.form_submit_button("Ajouter"):
            st.session_state.temp_sensations_list.append({
                "exercice": type_induction, "symptomes": symptomes,
                "score_malaise": score_malaise, "score_resemblance": score_resemblance
            })
            st.rerun()

    if st.session_state.temp_sensations_list:
        if st.button("💾 Sauvegarder", type="primary"):
             payload = {"type_exercice": "Sensations", "liste_tests": st.session_state.temp_sensations_list}
             st.session_state.temp_sensations_list = []
             sauver_et_quitter(payload, exo_data['titre'])

# --- TYPE 7 : HIÉRARCHIE ---
elif exo_data["type"] == "fiche_hierarchie_exposition":
    if "temp_hierarchy_list" not in st.session_state: st.session_state.temp_hierarchy_list = []
    
    with st.form("form_hier", clear_on_submit=True):
        col_h1, col_h2 = st.columns([1, 3])
        with col_h1: rang = st.number_input("Rang", min_value=1, value=1)
        with col_h2: situation = st.text_area("Situation :")
        c1, c2 = st.columns(2)
        with c1: s_evit = st.slider("Évitement", 0, 10, 5)
        with c2: s_detr = st.slider("Détresse", 0, 10, 5)

        if st.form_submit_button("Ajouter"):
            st.session_state.temp_hierarchy_list.append({
                "rang": rang, "situation": situation, "score_evit": s_evit, "score_detr": s_detr
            })
            st.rerun()

    if st.session_state.temp_hierarchy_list:
        st.markdown("##### 📋 Ma liste :")
        for i, item in enumerate(st.session_state.temp_hierarchy_list):
             st.caption(f"{item['rang']}. {item['situation']}")
             
        if st.button("💾 Sauvegarder", type="primary"):
             st.session_state.temp_hierarchy_list.sort(key=lambda x: x["rang"])
             payload = {"type_exercice": "Hiérarchie", "liste_hierarchie": st.session_state.temp_hierarchy_list}
             st.session_state.temp_hierarchy_list = []
             sauver_et_quitter(payload, exo_data['titre'])

# --- TYPE 8 : EXPOSITION ---
elif exo_data["type"] == "fiche_enregistrement_exposition":
    st.markdown("#### 🎬 Nouvelle séance d'exposition")
    with st.form("form_expo"):
        activite = st.text_area("Exercice :", placeholder="Ex: Aller au centre commercial")
        st.caption("AVANT")
        pens_auto = st.text_area("Pensées Négatives :", height=60)
        pens_alt = st.text_area("Pensées Alternatives :", height=60)
        st.divider()
        st.caption("APRÈS")
        emotions = st.text_input("Emotions ressenties :")
        appris = st.text_area("Qu'avez-vous appris ?", height=60)
        
        if st.form_submit_button("💾 Enregistrer", type="primary"):
            if activite:
                payload = {
                    "type_exercice": "Enregistrement Exposition",
                    "date": datetime.now().strftime("%d/%m/%Y"),
                    "activite": activite,
                    "preparation": {"pens_auto": pens_auto, "pens_alt": pens_alt},
                    "debrief": {"emotions": emotions, "appris_capa": appris}
                }
                sauver_et_quitter(payload, exo_data['titre'])

# --- TYPE 9 : ÉVALUATION PROGRÈS ---
elif exo_data["type"] == "fiche_evaluation_progres":
    st.markdown("#### 🏆 Bilan de fin de module")
    with st.form("form_bilan_progres"):
        st.markdown("##### 🧘 1. Pleine Conscience")
        pc_p = st.text_area("Progrès :", key="pc_p"); pc_f = st.text_area("Futur :", key="pc_f")
        st.markdown("##### 🧠 2. Flexibilité")
        fl_p = st.text_area("Progrès :", key="fl_p"); fl_f = st.text_area("Futur :", key="fl_f")
        
        if st.form_submit_button("💾 Enregistrer", type="primary"):
            payload = {
                "type_exercice": "Evaluation Progres",
                "pleine_conscience": {"progres": pc_p, "futur": pc_f},
                "flexibilite": {"progres": fl_p, "futur": fl_f}
            }
            sauver_et_quitter(payload, exo_data['titre'])

# --- TYPE 10 : PLAN MAINTIEN ---
elif exo_data["type"] == "fiche_plan_maintien":
    st.markdown("#### 📅 Mon plan pour continuer")
    with st.form("form_plan_maintien"):
        txt_plan = st.text_area("Votre plan détaillé :", height=200)
        if st.form_submit_button("💾 Enregistrer", type="primary"):
            payload = {"type_exercice": "Plan Maintien", "contenu": txt_plan}
            sauver_et_quitter(payload, exo_data['titre'])

else:
    st.warning("Formulaire non trouvé.")