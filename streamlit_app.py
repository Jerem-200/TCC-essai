import streamlit as st

# --- 1. CONFIGURATION (Doit toujours être la première commande Streamlit) ---
st.set_page_config(page_title="Mon Compagnon TCC", page_icon="🧠", layout="wide")

# --- 2. AUTHENTIFICATION ---
if "authentifie" not in st.session_state:
    st.session_state.authentifie = False

def verifier_mot_de_passe():
    if st.session_state.password_input == "TCC2025": 
        st.session_state.authentifie = True
    else:
        st.error("Mot de passe incorrect")

if not st.session_state.authentifie:
    st.title("🔒 Espace Patient Sécurisé")
    st.write("Veuillez entrer votre code d'accès personnel pour continuer.")
    st.text_input("Mot de passe", type="password", key="password_input", on_change=verifier_mot_de_passe)
    st.stop()

# --- 3. PAGE D'ACCUEIL (Visible uniquement si connecté) ---
st.title("🧠 Mon Compagnon TCC")
st.subheader("Tableau de bord personnel")
st.markdown("Bienvenue. Choisissez un outil ci-dessous pour commencer votre séance du jour.")

st.divider()

# --- LIGNE 1 : Les exercices principaux ---
col1, col2 = st.columns(2)

with col1:
    st.info("### 🧩 Restructuration (Beck)")
    st.write("Analysez une situation difficile et vos pensées.")
    st.page_link("pages/01_Colonnes_Beck.py", label="Lancer l'exercice", icon="➡️")

with col2:
    st.info("### 📊 Échelles (BDI)")
    st.write("Faites le point sur votre humeur actuelle.")
    st.page_link("pages/02_Echelles_BDI.py", label="Faire le test", icon="➡️")

# --- LIGNE 2 : Les nouveaux outils ---
st.divider()
col3, col4 = st.columns(2)

with col3:
    st.warning("### 📝 Registre des Activités")
    st.write("Notez vos activités heure par heure (Plaisir/Maîtrise).")
    st.page_link("pages/05_Registre_Activites.py", label="Ouvrir le Registre", icon="➡️")

with col4:
    st.success("### 📜 Mon Historique")
    st.write("Consultez vos progrès et vos anciens exercices.")
    st.page_link("pages/04_Historique.py", label="Voir mon suivi", icon="📅")

# --- LIGNE 3 : Ressources ---
st.divider()
with st.expander("📚 Bibliothèque de Fiches & Ressources"):
    st.write("Accédez aux documents de référence (Roue des émotions, Liste des distorsions...).")
    st.page_link("pages/03_Ressources.py", label="Ouvrir la bibliothèque", icon="📚")

# --- MENU LATÉRAL (Navigation rapide) ---
with st.sidebar:
    st.write("Connecté en tant que Patient")
    if st.button("Se déconnecter"):
        st.session_state.authentifie = False
        st.rerun()
        
    st.divider()
    st.title("Navigation Rapide")
    st.page_link("streamlit_app.py", label="🏠 Accueil")
    st.page_link("pages/01_Colonnes_Beck.py", label="🧩 Colonnes de Beck")
    st.page_link("pages/02_Echelles_BDI.py", label="📊 Échelles BDI")
    st.page_link("pages/05_Registre_Activites.py", label="📝 Registre Activités")
    st.page_link("pages/04_Historique.py", label="📜 Historique")
    st.page_link("pages/03_Ressources.py", label="📚 Ressources")