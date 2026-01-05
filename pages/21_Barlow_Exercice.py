import streamlit as st
import json
from datetime import datetime
from connect_db import sauvegarder_reponse_hebdo

st.set_page_config(page_title="Exercice en cours", page_icon="✏️", layout="wide")

# Masquer la sidebar pour le focus
st.markdown("<style>[data-testid='stSidebarNav'] {display: none;}</style>", unsafe_allow_html=True)

if "authentifie" not in st.session_state or not st.session_state.authentifie:
    st.warning("🔒 Connexion requise.")
    st.stop()

# Récupération de l'exercice sélectionné
if "exercice_actif" not in st.session_state or not st.session_state.exercice_actif:
    st.info("Aucun exercice sélectionné.")
    if st.button("⬅️ Retour au parcours"): st.switch_page("pages/00_Mon_Parcours.py")
    st.stop()

data_ctx = st.session_state.exercice_actif
exo_data = data_ctx["exo_data"]
current_user = st.session_state.user_id

# Header
c1, c2 = st.columns([1, 6])
with c1:
    if st.button("⬅️ Retour"): st.switch_page("pages/00_Mon_Parcours.py")
with c2:
    st.header(f"{exo_data['titre']}")

st.info(exo_data['description'])
st.divider()

# =========================================================
# LOGIQUE DES OUTILS (COPIE CONFORME DE VOTRE CODE)
# =========================================================

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
        
        if st.button("💾 Sauvegarder définitivement", type="primary"):
            payload = {"type_exercice": "Objectifs Traitement", "probleme_principal": st.session_state.temp_main_pb, "liste_objectifs": st.session_state.temp_objectives_list}
            if sauvegarder_reponse_hebdo(current_user, f"Exercice - {exo_data['titre']}", "N/A", payload):
                st.session_state.temp_main_pb = ""; st.session_state.temp_objectives_list = []
                st.toast("✅ Sauvegardé !"); st.switch_page("pages/00_Mon_Parcours.py")

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
        for i, arc in enumerate(st.session_state.temp_arc_list):
            with st.expander(f"{arc['date']} - {arc['antecedent'][:30]}..."):
                if st.button("Supprimer", key=f"del_arc_{i}"): st.session_state.temp_arc_list.pop(i); st.rerun()
        if st.button("💾 Sauvegarder ARC", type="primary"):
            payload = {"type_exercice": "ARC Emotionnel", "liste_arc": st.session_state.temp_arc_list}
            if sauvegarder_reponse_hebdo(current_user, f"Exercice - {exo_data['titre']}", "N/A", payload):
                st.session_state.temp_arc_list = []; st.toast("✅ Sauvegardé !"); st.switch_page("pages/00_Mon_Parcours.py")

# --- AJOUTER ICI LES AUTRES TYPES (Flexibilité, Sensations, etc.) EXACTEMENT COMME DANS VOTRE CODE ---
else:
    st.warning("Le formulaire pour ce type d'exercice est en cours de migration ou non reconnu.")