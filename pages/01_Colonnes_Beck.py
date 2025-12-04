import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Colonnes de Beck", page_icon="🧩")

st.title("🧩 Colonnes de Beck")

# --- 1. S'ASSURER QUE LA MÉMOIRE EXISTE ---
# On enlève la colonne "Distorsions" de la mémoire
if "data_beck" not in st.session_state:
    st.session_state.data_beck = pd.DataFrame(columns=[
        "Date", "Situation", "Émotion", "Intensité (Avant)", "Pensée Auto", 
        "Croyance (Avant)", "Pensée Rationnelle", 
        "Croyance (Rationnelle)", "Intensité (Après)", "Croyance (Après)"
    ])

# --- 2. LE FORMULAIRE ---
with st.form("beck_form"):
    # Situation
    col1, col2 = st.columns(2)
    with col1:
        date_event = st.date_input("Date", datetime.now())
    with col2:
        lieu = st.text_input("Lieu / Contexte")
    
    situation = st.text_area("Situation (Fait déclencheur)")
    
    st.divider()
    
    # Emotion (MODIFIÉ : Champ libre)
    emotion = st.text_input("Émotion (Nommez ce que vous ressentez)")
    intensite_avant = st.slider("Intensité de l'émotion (0-10)", 0, 10, 7)
    
    st.divider()
    
    # Pensées (Simplifié : plus de distorsions)
    pensee_auto = st.text_area("Pensée Automatique (Ce qui vous traverse l'esprit)")
    croyance_auto = st.slider("Croyance dans cette pensée (0-10)", 0, 10, 8)
    
    st.divider()
    
    # Restructuration
    pensee_rat = st.text_area("Pensée Alternative / Rationnelle")
    croyance_rat = st.slider("Croyance dans la pensée rationnelle (0-10)", 0, 10, 5)
    
    st.divider()
    
    # Résultat
    intensite_apres = st.slider("Nouvelle intensité de l'émotion (0-10)", 0, 10, 4)
    croyance_apres = st.slider("Nouvelle croyance pensée auto (0-10)", 0, 10, 4)
    
    submitted = st.form_submit_button("Enregistrer l'exercice")

    if submitted:
        # --- 3. SAUVEGARDE ---
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
        
        st.session_state.data_beck = pd.concat(
            [st.session_state.data_beck, pd.DataFrame([new_row])], 
            ignore_index=True
        )
        
        st.success("Exercice enregistré ! Vous pouvez le voir dans l'Historique.")

st.divider()
st.page_link("streamlit_app.py", label="Retour au Tableau de bord", icon="🏠")