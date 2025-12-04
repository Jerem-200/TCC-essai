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