import streamlit as st
import pandas as pd # N'oubliez pas l'import si ce n'est pas déjà fait

st.set_page_config(page_title="Mon Compagnon TCC", page_icon="🧠", layout="wide")

# --- SYSTÈME D'AUTHENTIFICATION (LE VERROU) ---
if "authentifie" not in st.session_state:
    st.session_state.authentifie = False

def verifier_mot_de_passe():
    # Définissez ici le mot de passe du patient
    if st.session_state.password_input == "TCC2025": 
        st.session_state.authentifie = True
    else:
        st.error("Mot de passe incorrect")

if not st.session_state.authentifie:
    st.title("🔒 Espace Patient Sécurisé")
    st.write("Veuillez entrer votre code d'accès personnel pour continuer.")
    st.text_input("Mot de passe", type="password", key="password_input", on_change=verifier_mot_de_passe)
    st.stop()  # <--- Ceci arrête le chargement du reste de l'app tant que c'est verrouillé

# --- TOUT LE RESTE DE VOTRE CODE COMMENCE ICI ---
# (Initialisation des données, Titre, Tableau de bord...)

import streamlit as st

st.set_page_config(
    page_title="Mon Compagnon TCC",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 Mon Compagnon TCC")
st.subheader("Tableau de bord")

st.markdown("Bienvenue. Choisissez un exercice ci-dessous :")

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.info("### 🧩 Restructuration")
    st.write("Tableau de Beck & Pensées alternatives")
    # Lien vers votre fichier dans le dossier pages
    st.page_link("pages/01_Colonnes_Beck.py", label="Lancer l'exercice", icon="➡️")

with col2:
    st.info("### 📊 Échelles BDI")
    st.write("Auto-évaluation de l'humeur")
    st.page_link("pages/02_Echelles_BDI.py", label="Faire le test", icon="➡️")

st.divider()

with st.expander("📚 Bibliothèque de Fiches"):
    st.write("Documents, Roue des émotions, Distorsions...")
    st.page_link("pages/03_Ressources.py", label="Ouvrir les ressources", icon="📚")

# Menu de secours à gauche
with st.sidebar:
    st.title("Menu Rapide")
    st.page_link("streamlit_app.py", label="Accueil", icon="🏠")
    st.page_link("pages/01_Colonnes_Beck.py", label="Colonnes de Beck", icon="🧩")
    st.page_link("pages/02_Echelles_BDI.py", label="Échelles BDI", icon="📊")
    st.page_link("pages/03_Ressources.py", label="Ressources", icon="📚")


    st.divider()

# Nouveau bouton large pour l'historique
st.info("### 📜 Mon Suivi")
st.write("Consultez vos anciens exercices et l'évolution de vos scores.")
# Attention : vérifiez que le nom du fichier correspond exactement à ce que vous avez créé
st.page_link("pages/04_Historique.py", label="Ouvrir mon Historique", icon="📅")

st.divider()

with st.expander("📚 Voir les Ressources et Fiches"):
    # ... (votre code existant pour les ressources)