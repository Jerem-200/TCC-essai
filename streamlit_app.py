import streamlit as st

st.set_page_config(
    page_title="Mon Compagnon TCC",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 Mon Compagnon TCC")
st.write("""
Bienvenue dans votre espace de travail thérapeutique.
Utilisez le menu à gauche pour naviguer vers les différents exercices :

* **🧩 Colonnes de Beck** : Pour analyser une situation difficile.
* **📊 Échelles (BDI)** : Pour faire le point sur votre état actuel.
* **📚 Ressources** : Pour consulter les fiches explicatives.
""")

st.info("🔒 Rappel : Aucune donnée nominative n'est stockée ici. Utilisez votre identifiant patient.")