import streamlit as st
import base64

st.set_page_config(page_title="Fiches & Ressources", page_icon="📚")

st.title("📚 Ressources Psycho-éducatives")

def afficher_pdf(nom_fichier):
    try:
        with open(nom_fichier, "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode('utf-8')
        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"Le fichier {nom_fichier} est introuvable. Vérifiez qu'il est bien chargé dans GitHub.")

tab1, tab2, tab3 = st.tabs(["Fonctions des Émotions", "Roue des Émotions", "Distorsions Cognitives"])

with tab1:
    st.header("À quoi servent nos émotions ?")
    st.write("Les émotions sont des messagers essentiels...")
    # Remplacez par le nom EXACT de votre fichier PDF chargé sur GitHub
    afficher_pdf("Les fonctions des émotions.pdf") 

with tab2:
    st.header("La Roue de Plutchik")
    afficher_pdf("Roue des sentiments de Plutchik.pdf")

with tab3:
    st.header("Comprendre les distorsions")
    afficher_pdf("Distorsions cognitives.pdf")