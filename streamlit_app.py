import streamlit as st

st.set_page_config(page_title="Mon Compagnon TCC", page_icon="🧠", layout="wide")

# --- AUTHENTIFICATION ---
if "authentifie" not in st.session_state:
    st.session_state.authentifie = False

def verifier_mot_de_passe():
    if st.session_state.password_input == "TCC2025": 
        st.session_state.authentifie = True
    else:
        st.error("Mot de passe incorrect")

if not st.session_state.authentifie:
    st.title("🔒 Espace Patient Sécurisé")
    st.text_input("Mot de passe", type="password", key="password_input", on_change=verifier_mot_de_passe)
    st.stop()

# --- ACCUEIL ---
st.title("🧠 Mon Compagnon TCC")
st.subheader("Tableau de bord personnel")
st.divider()

# --- LIGNE 1 : ANALYSE ---
c1, c2 = st.columns(2)
with c1:
    st.info("### 🧩 Restructuration")
    st.write("Beck & Pensées alternatives")
    st.page_link("pages/01_Colonnes_Beck.py", label="Lancer", icon="➡️")
with c2:
    st.info("### 📊 Échelles (BDI)")
    st.write("Auto-évaluation de l'humeur")
    st.page_link("pages/02_Echelles_BDI.py", label="Tester", icon="➡️")

st.divider()

# --- LIGNE 2 : ACTION ---
c3, c4 = st.columns(2)
with c3:
    st.warning("### 📝 Registre Activités")
    st.write("Quotidien & Plaisir")
    st.page_link("pages/05_Registre_Activites.py", label="Ouvrir", icon="➡️")
with c4:
    st.error("### 💡 Résolution Problèmes")
    st.write("Trouver des solutions")
    st.page_link("pages/06_Resolution_Probleme.py", label="Lancer", icon="➡️")

st.divider()

# --- LIGNE 3 : BIEN-ÊTRE & SUIVI ---
c5, c6 = st.columns(2)
with c5:
    # Bouton Relaxation (Vert succès pour le calme)
    st.success("### 🧘 Relaxation")
    st.write("Respiration & Détente")
    st.page_link("pages/07_Relaxation.py", label="Se détendre", icon="➡️")
with c6:
    # Bouton Historique (CORRIGÉ ICI : st.success au lieu de st.primary)
    st.success("### 📜 Historique")
    st.write("Voir mes progrès")
    st.page_link("pages/04_Historique.py", label="Consulter", icon="📅")

st.divider()

with st.expander("📚 Bibliothèque de Fiches & Ressources"):
    st.write("Accédez aux documents de référence.")
    st.page_link("pages/03_Ressources.py", label="Ouvrir la bibliothèque", icon="📚")

# --- SIDEBAR ---
with st.sidebar:
    st.write("Connecté en tant que Patient")
    if st.button("Se déconnecter"):
        st.session_state.authentifie = False
        st.rerun()
    st.divider()
    st.title("Navigation Rapide")
    st.page_link("streamlit_app.py", label="🏠 Accueil")
    st.page_link("pages/01_Colonnes_Beck.py", label="🧩 Beck")
    st.page_link("pages/02_Echelles_BDI.py", label="📊 BDI")
    st.page_link("pages/05_Registre_Activites.py", label="📝 Activités")
    st.page_link("pages/06_Resolution_Probleme.py", label="💡 Problèmes")
    st.page_link("pages/07_Relaxation.py", label="🧘 Relaxation")
    st.page_link("pages/04_Historique.py", label="📜 Historique")