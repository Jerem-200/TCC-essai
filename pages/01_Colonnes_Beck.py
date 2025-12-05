import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Colonnes de Beck", page_icon="🧩")

st.title("🧩 Colonnes de Beck")

# --- 1. S'ASSURER QUE LA MÉMOIRE EXISTE ---
if "data_beck" not in st.session_state:
    st.session_state.data_beck = pd.DataFrame(columns=[
        "Date", "Situation", "Émotion", "Intensité (Avant)", "Pensée Auto", 
        "Croyance (Avant)", "Pensée Rationnelle", 
        "Croyance (Rationnelle)", "Intensité (Après)", "Croyance (Après)"
    ])

# --- 2. LE FORMULAIRE ---
with st.form("beck_form"):
    # --- SITUATION ---
    col1, col2 = st.columns(2)
    with col1:
        date_event = st.date_input("Date", datetime.now())
    with col2:
        lieu = st.text_input("Lieu / Contexte")
    
    # Info-bulle Situation
    help_situation = """C'est le contexte dans lequel vous vous trouvez (horaire, lieu, personnes autour de toi...). Il est constitué d'éléments factuels, les plus précis possible.\n\nEx : Entretien d'embauche non concluant."""
    
    situation = st.text_area("Situation (Fait déclencheur)", help=help_situation)
    
    st.divider()
    
    # --- EMOTION ---
    # Info-bulle Emotion
    help_emotion = """Vous observez l'émotion que vous ressentez dans cette situation. En complément, prenez le temps d'évaluer l'intensité de votre émotion sur une échelle de 0 à 10.\n\nEx : Tristesse avec une intensité de 7/10."""
    
    emotion = st.text_input("Émotion (Nommez ce que vous ressentez)", help=help_emotion)
    intensite_avant = st.slider("Intensité de l'émotion (0-10)", 0, 10, 7)
    
    st.divider()
    
    # --- PENSÉE AUTOMATIQUE ---
    # Info-bulle Pensée Auto
    help_pensee = """Une pensée automatique est comme une petite voix dans votre tête, qui commente tout ce que vous faites.\nIdentifiez-la puis prenez le temps d'évaluer votre niveau de croyance en cette pensée sur une échelle de 0 à 10.\n\nEx: "Je n'arrive jamais à rien." avec un degré de croyance de 7/10."""
    
    pensee_auto = st.text_area("Pensée Automatique (Ce qui vous traverse l'esprit)", help=help_pensee)
    
    # Changement du titre ici
    croyance_auto = st.slider("Degré de croyance en la pensée automatique (0-10)", 0, 10, 8)
    
    st.divider()
    
    # --- PENSÉE RATIONNELLE ---
    # Info-bulle Rationnelle
    help_rationnel = """Essayez d'observer la situation sous un autre angle. Posez-vous par exemples les questions suivantes :\n• Si un-e proche s'était retrouvé-e dans cette situation, quelle aurait été sa réaction ?\n• Dans une période de ma vie où je me sentais mieux, qu'aurais-je pensé de cette situation ?\n\nÉvaluez le degré de croyance en cette pensée automatique de 0 à 10.\nEx : "J'ai déjà réussi des entretiens d'embauche par le passé." avec un degré de croyance de 8/10."""
    
    pensee_rat = st.text_area("Pensée Alternative / Rationnelle", help=help_rationnel)
    croyance_rat = st.slider("Croyance dans la pensée rationnelle (0-10)", 0, 10, 5)
    
    st.divider()
    
    # --- RÉSULTATS ---
    st.subheader("5. Ré-évaluation")
    
    # Info-bulle Résultats
    help_resultat = """Réévaluez les émotions ressenties et votre degré de croyance vis-à-vis de la pensée automatique.\n\nEx :\nNouveau degré de croyance : 4/10\nNouvelle intensité de mon émotion: 5/10."""
    
    # Changement du titre ici
    croyance_apres = st.slider("Nouveau degré de croyance en la pensée automatique (0-10)", 0, 10, 4, help=help_resultat)
    intensite_apres = st.slider("Nouvelle intensité de l'émotion (0-10)", 0, 10, 4)
    
    submitted = st.form_submit_button("Enregistrer l'exercice")

# ... (le code d'avant reste pareil)

    if submitted:
        # 1. Sauvegarde Locale (Session) - On garde pour l'affichage immédiat
        new_row = {
            "Date": str(date_event),
            "Situation": f"{lieu} - {situation}",
            "Émotion": emotion,
            "Intensité (Avant)": intensite_avant,
            "Pensée Auto": pensee_auto,
            "Croyance (Avant)": croyance_auto,
            "Pensée Rationnelle": pensee_rat,
            "Croyance (Rationnelle)": croyance_rat,
            "Intensité (Après)": intensite_apres,
            "Croyance (Après)": croyance_apres
        }
        st.session_state.data_beck = pd.concat([st.session_state.data_beck, pd.DataFrame([new_row])], ignore_index=True)
        
        # 2. SAUVEGARDE CLOUD (GOOGLE SHEETS) --- NOUVEAU !
        from connect_db import save_data
        
        # On récupère l'ID du patient (ou "Anonyme" s'il y a un bug)
        patient = st.session_state.get("patient_id", "Anonyme")

        # On prépare la liste simple pour Excel (l'ordre compte !)
        liste_excel = [
            patient,              # <--- ON AJOUTE L'ID EN PREMIER
            str(date_event), 
            f"{lieu} - {situation}", 
            emotion, 
            intensite_avant, 
            pensee_auto, 
            croyance_auto, 
            pensee_rat, 
            croyance_rat, 
            intensite_apres, 
            croyance_apres
        ]
        
        # On envoie vers l'onglet "Beck"
        if save_data("Beck", liste_excel):
            st.success("✅ Exercice enregistré dans le Cloud et l'Historique !")
        else:
            st.warning("⚠️ Enregistré en local seulement (Erreur connexion).")

st.divider()
st.page_link("streamlit_app.py", label="Retour à l'accueil", icon="🏠")