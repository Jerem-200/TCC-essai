import streamlit as st
import time

# Imports DB
from connect_db import (
    verifier_therapeute, verifier_code_patient, recuperer_mes_patients,
    charger_outils_autorises, sauvegarder_outils_autorises, 
    load_data, generer_code_securise
)
# IMPORT DE LA VUE PATIENT CRÉÉE JUSTE AVANT
from vue_patient import afficher_vue_patient

# CONFIGURATION PAGE
st.set_page_config(page_title="Compagnon TCC", page_icon="🧠", layout="wide")
st.markdown("<style>[data-testid='stSidebarNav'] {display: none;}</style>", unsafe_allow_html=True)

# GESTION SESSION
if "authentifie" not in st.session_state: st.session_state.authentifie = False
if "user_type" not in st.session_state: st.session_state.user_type = None 
if "user_id" not in st.session_state: st.session_state.user_id = "" 

# =========================================================
# 1. ÉCRAN DE CONNEXION
# =========================================================
if not st.session_state.authentifie:
    st.title("🧠 Compagnon TCC")
    t_pat, t_pro = st.tabs(["👤 Accès Patient", "🩺 Accès Thérapeute"])
    
    with t_pat:
        with st.form("login_p"):
            code = st.text_input("Code Patient :", type="password")
            if st.form_submit_button("Entrer"):
                if verifier_code_patient(code):
                    st.session_state.authentifie = True
                    st.session_state.user_type = "patient"
                    st.session_state.user_id = code # Ou logique d'ID réel
                    st.rerun()
                else: st.error("Code inconnu")
                
    with t_pro:
        with st.form("login_t"):
            u = st.text_input("Identifiant")
            p = st.text_input("Mot de passe", type="password")
            if st.form_submit_button("Connexion Pro"):
                tid = verifier_therapeute(u, p)
                if tid:
                    st.session_state.authentifie = True
                    st.session_state.user_type = "therapeute"
                    st.session_state.user_id = tid
                    st.rerun()
                else: st.error("Erreur d'identification")
    st.stop()

# =========================================================
# 2. AFFICHAGE DIRECT SELON LE RÔLE
# =========================================================
if st.session_state.user_type == "patient":
    # On masque la sidebar native pour avoir le plein écran
    # et on appelle directement la vue complète
    afficher_vue_patient(st.session_state.user_id)
    
    # Bouton déconnexion discret en bas de sidebar si besoin
    with st.sidebar:
        st.write(f"Connecté : {st.session_state.user_id}")
        if st.button("Se déconnecter"):
            st.session_state.authentifie = False
            st.rerun()

elif st.session_state.user_type == "therapeute":
    # Ton code thérapeute existant ici...
    st.title("Espace Thérapeute")
    st.write("Tableau de bord thérapeute à insérer ici.")
    if st.button("Déconnexion"):
        st.session_state.authentifie = False
        st.rerun()