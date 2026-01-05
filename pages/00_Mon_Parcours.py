import streamlit as st
import pandas as pd
import json
from protocole_config import PROTOCOLE_BARLOW, QUESTIONS_HEBDO
from connect_db import load_data, sauvegarder_reponse_hebdo

st.set_page_config(page_title="Mon Espace Santé", page_icon="🧘", layout="wide")

st.markdown("""
    <style>
        [data-testid="stSidebarNav"] {display: none;}
        .stExpander {border: 1px solid #ddd; border-radius: 5px;}
    </style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.page_link("streamlit_app.py", label="🏠 Accueil")
    st.divider()

if "authentifie" not in st.session_state or not st.session_state.authentifie:
    st.warning("🔒 Connexion requise.")
    st.stop()

current_user = st.session_state.user_id

# --- CHARGEMENT ---
try:
    from streamlit_app import charger_progression, charger_etat_devoirs
except ImportError:
    def charger_progression(uid): return ["module0"] 
    def charger_etat_devoirs(uid): return {}

modules_debloques = charger_progression(current_user)
devoirs_exclus = charger_etat_devoirs(current_user)

st.title(f"Espace Patient - {current_user}")

tab_parcours, tab_outils, tab_bilan = st.tabs(["🗺️ Ma Progression", "🛠️ Mes Outils", "📝 Bilan Hebdo"])

# 1. PROGRESSION
with tab_parcours:
    st.markdown("### 📍 Mon cheminement")
    for code_mod, data in PROTOCOLE_BARLOW.items():
        if code_mod in modules_debloques:
            with st.expander(f"✅ {data['titre']}", expanded=False):
                st.info(f"**Objectifs :** {data['objectifs']}")
                st.write("Retrouvez les documents PDF dans l'onglet 'Tous les Documents' de l'accueil ou ci-dessous.")
                if data.get('pdfs_module'):
                    for p in data['pdfs_module']:
                        st.caption(f"📄 {p.split('/')[-1]}")
        else:
            with st.container():
                st.markdown(f"🔒 **{data['titre']}** _(Verrouillé)_")
                st.divider()

# 2. OUTILS (GRILLE DE LANCEMENT)
with tab_outils:
    st.subheader("🚀 Lancer un outil")
    
    exos_dispos = []
    for m in modules_debloques:
        if m in PROTOCOLE_BARLOW and "exercices" in PROTOCOLE_BARLOW[m]:
            for exo in PROTOCOLE_BARLOW[m]["exercices"]:
                exos_dispos.append((m, exo))
    
    if not exos_dispos:
        st.warning("Aucun outil débloqué.")
    
    cols = st.columns(3)
    for i, (mod_code, exo_data) in enumerate(exos_dispos):
        col = cols[i % 3]
        with col:
            with st.container(border=True):
                st.markdown(f"**{exo_data['titre']}**")
                st.caption(exo_data['description'])
                if st.button("Ouvrir", key=f"btn_{exo_data['id']}", use_container_width=True):
                    st.session_state["exercice_actif"] = {"mod_code": mod_code, "exo_data": exo_data}
                    st.switch_page("pages/99_Barlow_Work.py")

# 3. BILAN HEBDO (On peut laisser léger ici ou déplacer aussi)
with tab_bilan:
    st.subheader("📝 Bilan Hebdo")
    choix_q = st.radio("Questionnaire :", list(QUESTIONS_HEBDO.keys()))
    if choix_q:
        config = QUESTIONS_HEBDO[choix_q]
        with st.form(f"form_sante_{choix_q}"):
            st.markdown(f"**{config['titre']}**")
            st.caption(config['description'])
            # ... (Code du formulaire Bilan identique à avant, il est léger car simple QCM)
            # Pour faire court, je ne le remets pas tout, mais tu peux garder ton bloc existant ici.
            if st.form_submit_button("Enregistrer"):
                st.success("Sauvegardé (Simulation)")