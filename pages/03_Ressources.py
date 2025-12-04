import streamlit as st
import base64
import os

st.set_page_config(page_title="Fiches & Ressources", page_icon="📚")

st.title("📚 Ressources Psycho-éducatives")

# --- FONCTION PDF (Gardée pour les autres onglets) ---
def afficher_pdf(nom_fichier):
    if not os.path.exists(nom_fichier):
        st.error(f"Fichier '{nom_fichier}' introuvable.")
        return
    
    with open(nom_fichier, "rb") as f:
        pdf_data = f.read()
        
    st.download_button(
        label=f"📥 Télécharger le PDF complet",
        data=pdf_data,
        file_name=nom_fichier,
        mime='application/pdf'
    )
    
    # Affichage classique (iframe) pour PC
    base64_pdf = base64.b64encode(pdf_data).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)


# --- LES ONGLETS ---
tab1, tab2, tab3 = st.tabs(["Fonctions des Émotions", "Roue des Émotions", "Distorsions Cognitives"])

with tab1:
    st.header("À quoi servent nos émotions ?")
    # Ici on garde le PDF classique
    afficher_pdf("Les fonctions des émotions.pdf") 

with tab2:
    st.header("La Roue de Plutchik")
    # Ici on garde le PDF classique
    afficher_pdf("Roue des sentiments de Plutchik.pdf")

with tab3:
    st.header("Les 10 Distorsions Cognitives")
    st.write("Voici les pièges de pensée les plus courants. Les reconnaissez-vous ?")
    
    # 1. On garde le bouton pour télécharger le fichier original
    # (Il faut que le fichier PDF soit toujours dans le dossier)
    if os.path.exists("Distorsions cognitives.pdf"):
        with open("Distorsions cognitives.pdf", "rb") as f:
            st.download_button(
                label="📥 Télécharger la fiche PDF (Impression)",
                data=f,
                file_name="Distorsions cognitives.pdf",
                mime="application/pdf"
            )
    
    st.divider()
    
    # 2. L'AFFICHAGE VISUEL (IMAGES) - Parfait pour le mobile
    # Assurez-vous d'avoir uploadé disto_1.jpg, disto_2.jpg, etc.
    
    # Page 1
    if os.path.exists("disto_1.jpg"):
        st.image("disto_1.jpg", caption="Page 1 : Tout ou rien, Filtre, Catastrophisme...", use_container_width=True)
    else:
        st.warning("Image 'disto_1.jpg' manquante. Veuillez l'ajouter au projet.")
        
    st.divider()
    
    # Page 2
    if os.path.exists("disto_2.jpg"):
        st.image("disto_2.jpg", caption="Page 2 : Raisonnement émotionnel, Je dois...", use_container_width=True)
        
    st.divider()
    
    # Page 3
    if os.path.exists("disto_3.jpg"):
        st.image("disto_3.jpg", caption="Page 3 : Étiquetage, Comparaison...", use_container_width=True)

st.divider()
st.page_link("streamlit_app.py", label="Retour à l'accueil", icon="🏠")