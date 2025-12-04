import streamlit as st
import os

st.set_page_config(page_title="Fiches & Ressources", page_icon="📚")

st.title("📚 Ressources Psycho-éducatives")
st.write("Consultez les fiches directement ci-dessous ou téléchargez-les pour les imprimer.")

# --- FONCTION D'AFFICHAGE INTELLIGENTE ---
def afficher_ressource(titre_pdf, nom_fichier_pdf, liste_images):
    """
    Affiche le bouton de téléchargement du PDF + les images en dessous
    """
    # 1. BOUTON DE TÉLÉCHARGEMENT (Si le PDF existe)
    if os.path.exists(nom_fichier_pdf):
        with open(nom_fichier_pdf, "rb") as f:
            st.download_button(
                label=f"📥 Télécharger la fiche '{titre_pdf}' (PDF)",
                data=f,
                file_name=nom_fichier_pdf,
                mime="application/pdf",
                help="Idéal pour l'impression ou la lecture sur grand écran."
            )
    else:
        st.warning(f"Le fichier PDF '{nom_fichier_pdf}' est introuvable sur le serveur.")

    st.divider()

    # 2. GALERIE D'IMAGES (Pour le mobile)
    for image_name in liste_images:
        if os.path.exists(image_name):
            # use_container_width=True permet à l'image de s'adapter parfaitement à l'écran du téléphone
            st.image(image_name, use_container_width=True)
        else:
            st.info(f"Image '{image_name}' non chargée. (Faites une capture d'écran du PDF et nommez-la ainsi).")


# --- LES ONGLETS ---
tab1, tab2, tab3 = st.tabs(["Fonctions des Émotions", "Roue des Émotions", "Distorsions Cognitives"])

# ONGLET 1
with tab1:
    st.header("À quoi servent nos émotions ?")
    st.caption("Comprendre le message caché derrière chaque émotion.")
    
    afficher_ressource(
        titre_pdf="Fonctions des émotions",
        nom_fichier_pdf="Les fonctions des émotions.pdf",  # Nom exact de votre PDF actuel
        liste_images=["fonctions.jpg"]                      # Nom de votre nouvelle image
    )

# ONGLET 2
with tab2:
    st.header("La Roue de Plutchik")
    st.caption("Un outil pour identifier précisément ce que vous ressentez.")
    
    afficher_ressource(
        titre_pdf="Roue des sentiments",
        nom_fichier_pdf="Roue des sentiments de Plutchik.pdf",
        liste_images=["roue.jpg"]
    )

# ONGLET 3
with tab3:
    st.header("Les Distorsions Cognitives")
    st.caption("Les pièges de pensée les plus courants.")
    
    afficher_ressource(
        titre_pdf="Liste des Distorsions",
        nom_fichier_pdf="Distorsions cognitives.pdf",
        liste_images=["disto_1.jpg", "disto_2.jpg", "disto_3.jpg"] # Les 3 pages
    )

st.divider()
st.page_link("streamlit_app.py", label="Retour à l'accueil", icon="🏠")