import streamlit as st
import os
import time
import pandas as pd
import altair as alt
import json
from datetime import datetime

from protocole_config import PROTOCOLE_BARLOW, QUESTIONS_HEBDO 
from connect_db import load_data, sauvegarder_reponse_hebdo, supprimer_reponse

st.set_page_config(page_title="Mon Espace Santé", page_icon="🧘", layout="wide")

# CSS et Sidebar (inchangé)
st.markdown("<style>[data-testid='stSidebarNav'] {display: none;} .stExpander {border: 1px solid #ddd; border-radius: 5px;}</style>", unsafe_allow_html=True)
with st.sidebar:
    st.page_link("streamlit_app.py", label="🏠 Accueil")
    st.divider()

if "authentifie" not in st.session_state or not st.session_state.authentifie:
    st.warning("🔒 Connexion requise.")
    st.stop()

current_user = st.session_state.user_id

# Fonctions utilitaires (inchangées)
def charger_historique_complet(uid):
    try:
        raw = load_data("Reponses_Hebdo")
        if raw:
            df = pd.DataFrame(raw)
            df = df[df["Patient"] == uid].copy()
            if not df.empty:
                df["Date"] = pd.to_datetime(df["Date"])
                df["Score_Global"] = pd.to_numeric(df["Score_Global"], errors='coerce')
                df["Type"] = df["Questionnaire"].apply(lambda x: str(x).split(" - ")[1].split(" (")[0] if " - " in str(x) else str(x))
                return df
    except: pass
    return pd.DataFrame()

from streamlit_app import charger_progression, charger_etat_devoirs

# Chargement données
modules_debloques = charger_progression(current_user)
devoirs_exclus = charger_etat_devoirs(current_user)
df_history = charger_historique_complet(current_user)

st.title(f"Espace Patient - {current_user}")

tab_parcours, tab_outils, tab_bilan, tab_historique = st.tabs([
    "🗺️ Ma Progression", "🛠️ Mes Outils", "📝 Bilan Hebdo", "📜 Mon Historique"
])

# --- 1. MA PROGRESSION (Inchangé) ---
with tab_parcours:
    st.markdown("### 📍 Mon cheminement")
    for code_mod, data in PROTOCOLE_BARLOW.items():
        if code_mod in modules_debloques:
            with st.expander(f"✅ {data['titre']}", expanded=False):
                # ... (Remettre ici votre code d'affichage des étapes et téléchargement PDF)
                st.write(data['objectifs'])
        else:
            st.markdown(f"🔒 **{data['titre']}** _(Verrouillé)_")

# --- 2. MES OUTILS (ALLÉGÉ - LE LANCEUR) ---
with tab_outils:
    liste_exos_dispos = []
    for m in modules_debloques:
        if m in PROTOCOLE_BARLOW and "exercices" in PROTOCOLE_BARLOW[m]:
            for exo in PROTOCOLE_BARLOW[m]["exercices"]:
                liste_exos_dispos.append({"mod_code": m, "exo_data": exo})
    
    liste_exos_dispos.sort(key=lambda x: x['mod_code'])
    
    if not liste_exos_dispos:
        st.info("Débloquez des modules pour voir les outils.")
    else:
        st.subheader("Choisissez un outil pour commencer")
        for item in liste_exos_dispos:
            with st.container(border=True):
                c1, c2 = st.columns([4, 1])
                with c1:
                    st.markdown(f"**{item['exo_data']['titre']}**")
                    st.caption(item['exo_data']['description'])
                with c2:
                    if st.button("Lancer", key=f"launch_{item['exo_data']['id']}", use_container_width=True):
                        st.session_state["exercice_actif"] = item
                        st.switch_page("pages/21_Barlow_Exercice.py")

# --- 3. BILAN HEBDO (Inchangé) ---
with tab_bilan:
    choix_q = st.radio("Questionnaire :", list(QUESTIONS_HEBDO.keys()))
    if choix_q:
        config = QUESTIONS_HEBDO[choix_q]
        with st.form(f"form_sante_{choix_q}"):
            # ... (Remettre ici votre logique de formulaire Bilan Hebdo)
            st.form_submit_button("Enregistrer")

# --- 4. MON HISTORIQUE (Inchangé) ---
with tab_historique:
    if not df_history.empty:
        # ... (Remettre ici votre code de graphiques Altair et journal des exercices)
        st.dataframe(df_history[["Date", "Questionnaire", "Score_Global"]], use_container_width=True)
    else:
        st.info("Historique vide.")