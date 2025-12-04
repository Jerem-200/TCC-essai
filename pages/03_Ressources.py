import streamlit as st
import base64
import os

st.set_page_config(page_title="Fiches & Ressources", page_icon="📚")

st.title("📚 Ressources Psycho-éducatives")

# --- FONCTION AMÉLIORÉE : Affichage + Téléchargement ---
def afficher_pdf(nom_fichier):
    # Vérification que le fichier existe pour éviter les erreurs
    if not os.path.exists(nom_fichier):
        st.error(f"Le fichier '{nom_fichier}' est introuvable. Vérifiez qu'il est bien à la racine du projet GitHub.")
        return

    with open(nom_fichier, "rb") as f:
        pdf_data = f.read()
        
    # 1. LE BOUTON DE TÉLÉCHARGEMENT (La solution pour le mobile)
    st.download_button(
        label=f"📥 Ouvrir / Télécharger le PDF ({nom_fichier})",
        data=pdf_data,
        file_name=nom_fichier,
        mime='application/pdf',
        help="Cliquez ici si le PDF ne s'affiche pas correctement sur votre téléphone."
    )
    
    # 2. L'AFFICHAGE VISUEL (Pour les ordinateurs)
    base64_pdf = base64.b64encode(pdf_data).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)


# --- LES ONGLETS ---
tab1, tab2, tab3 = st.tabs(["Fonctions des Émotions", "Roue des Émotions", "Distorsions"])

with tab1:
    st.header("À quoi servent nos émotions ?")
    st.write("Les émotions sont des messagers essentiels...")
    afficher_pdf("Les fonctions des émotions.pdf") 

with tab2:
    st.header("La Roue de Plutchik")
    st.write("Pour vous aider à identifier précisément ce que vous ressentez.")
    afficher_pdf("Roue des sentiments de Plutchik.pdf")

with tab3:
    st.header("Comprendre les distorsions")
    st.write("Liste des pièges de pensée courants.")
    afficher_pdf("Distorsions cognitives.pdf")

st.divider()
st.page_link("streamlit_app.py", label="Retour à l'accueil", icon="🏠")