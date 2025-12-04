import streamlit as st

st.set_page_config(
    page_title="Mon Compagnon TCC",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 Mon Compagnon TCC")
st.subheader("Bienvenue dans votre espace personnel")

st.markdown("""
Ceci est votre tableau de bord. Cliquez sur un module ci-dessous pour lancer l'exercice.
""")

st.divider()

# --- CRÉATION DU MENU SOUS FORME DE GROS BOUTONS (DASHBOARD) ---

col1, col2 = st.columns(2)

with col1:
    st.info("### 🧩 Restructuration")
    st.write("Analysez vos pensées automatiques et trouvez des alternatives.")
    # C'est ici que la magie opère : on fait le lien vers le fichier physique
    st.page_link("pages/01_Colonnes_Beck.py", label="Ouvrir les Colonnes de Beck", icon="➡️")

with col2:
    st.info("### 📊 Évaluations")
    st.write("Faites le point sur votre état émotionnel (BDI-II, etc.).")
    st.page_link("pages/02_Echelles_BDI.py", label="Ouvrir les Échelles", icon="➡️")

st.divider()

with st.expander("📚 Voir les Ressources et Fiches"):
    st.write("Consultez les documents de référence (Roue des émotions, Distorsions...).")
    st.page_link("pages/03_Ressources.py", label="Accéder à la Bibliothèque", icon="📚")

# --- MENU LATÉRAL DE SECOURS (Juste au cas où) ---
with st.sidebar:
    st.title("Navigation Rapide")
    st.page_link("Home.py", label="Accueil", icon="🏠")
    st.page_link("pages/01_Colonnes_Beck.py", label="Colonnes de Beck", icon="🧩")
    st.page_link("pages/02_Echelles_BDI.py", label="Échelles BDI", icon="📊")
    st.page_link("pages/03_Ressources.py", label="Ressources", icon="📚")