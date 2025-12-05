import streamlit as st
import os

st.set_page_config(page_title="Fiches & Ressources", page_icon="📚")

st.title("📚 Ressources Psycho-éducatives")
st.write("Consultez les fiches directement ci-dessous ou téléchargez-les pour les imprimer.")

# --- FONCTION D'AFFICHAGE ---
def afficher_ressource(titre_pdf, nom_fichier_pdf, liste_images):
    # 1. BOUTON DE TÉLÉCHARGEMENT
    if os.path.exists(nom_fichier_pdf):
        with open(nom_fichier_pdf, "rb") as f:
            st.download_button(
                label=f"📥 Télécharger la fiche '{titre_pdf}' (PDF)",
                data=f,
                file_name=os.path.basename(nom_fichier_pdf), # Astuce pour garder un nom propre au téléchargement
                mime="application/pdf",
                help="Idéal pour l'impression."
            )
    else:
        st.warning(f"Fichier '{nom_fichier_pdf}' introuvable (Vérifiez le dossier assets).")

    st.divider()

    # 2. GALERIE D'IMAGES
    for image_name in liste_images:
        if os.path.exists(image_name):
            st.image(image_name, use_container_width=True)
        else:
            st.info(f"Image '{image_name}' introuvable.")


# --- LES ONGLETS (C'EST ICI QU'ON CHANGE LES CHEMINS) ---
tab1, tab2, tab3 = st.tabs(["Fonctions des Émotions", "Roue des Émotions", "Distorsions Cognitives"])

# On ajoute "assets/" devant tous les noms de fichiers

with tab1:
    st.header("À quoi servent nos émotions ?")
    st.caption("Comprendre le message caché derrière chaque émotion.")
    
    afficher_ressource(
        titre_pdf="Fonctions des émotions",
        nom_fichier_pdf="assets/Les fonctions des émotions.pdf",  # <--- CHANGEMENT ICI
        liste_images=["assets/fonctions.jpg"]                     # <--- ET ICI
    )

with tab2:
    st.header("La Roue de Plutchik")
    st.caption("Un outil pour identifier précisément ce que vous ressentez.")
    
    afficher_ressource(
        titre_pdf="Roue des sentiments",
        nom_fichier_pdf="assets/Roue des sentiments de Plutchik.pdf", # <--- ET LÀ
        liste_images=["assets/roue.jpg"]
    )

with tab3:
    st.header("Les Distorsions Cognitives")
    st.caption("Les pièges de pensée les plus courants.")
    
    afficher_ressource(
        titre_pdf="Liste des Distorsions",
        nom_fichier_pdf="assets/Distorsions cognitives.pdf",          # <--- ET LÀ
        liste_images=[
            "assets/disto_1.jpg", 
            "assets/disto_2.jpg", 
            "assets/disto_3.jpg"
        ]
    )

st.divider()
st.page_link("streamlit_app.py", label="Retour à l'accueil", icon="🏠")