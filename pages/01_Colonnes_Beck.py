import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Colonnes de Beck", page_icon="🧩")

st.title("🧩 Colonnes de Beck")

# --- 1. LE DICTIONNAIRE DES DISTORSIONS (REMIS EN PLACE) ---
# Basé sur votre document PDF "Distorsions cognitives"
distorsions_dict = {
    [cite_start]"Pensée tout ou rien": "Penser de manière extrême : soit c'est parfait, soit c'est terrible[cite: 4].",
    [cite_start]"Filtre mental": "Se focaliser sur un détail négatif en ignorant le reste[cite: 8].",
    [cite_start]"Catastrophisme": "Imaginer le pire scénario possible ('Et si...?')[cite: 11].",
    [cite_start]"Surgénéralisation": "Tirer une conclusion générale d'un seul événement[cite: 14].",
    [cite_start]"Disqualification du positif": "Rejeter les expériences positives ('Ça ne compte pas')[cite: 17].",
    [cite_start]"Culpabilisation": "S'attribuer la faute pour des choses hors de notre contrôle[cite: 20].",
    [cite_start]"Raisonnement émotionnel": "Croire que si on le ressent, c'est que c'est vrai[cite: 23].",
    [cite_start]"Les 'Je dois / Il faut'": "Règles rigides sur comment on devrait se comporter[cite: 26].",
    [cite_start]"Conclusion hâtive": "Juger sans preuves suffisantes (lecture de pensée)[cite: 29].",
    [cite_start]"Étiquetage": "Se coller une étiquette définitive ('Je suis nul')[cite: 32].",
    [cite_start]"Comparaison sociale": "Se comparer aux autres en ne voyant que ses défauts[cite: 36].",
    [cite_start]"Fusion pensée-action": "Croire que penser à une chose équivaut à la faire (pensée magique)[cite: 37, 39]."
}

# --- 2. S'ASSURER QUE LA MÉMOIRE EXISTE ---
if "data_beck" not in st.session_state:
    st.session_state.data_beck = pd.DataFrame(columns=[
        "Date", "Situation", "Émotion", "Intensité (Avant)", "Pensée Auto", 
        "Distorsions", "Croyance (Avant)", "Pensée Rationnelle", 
        "Croyance (Rationnelle)", "Intensité (Après)", "Croyance (Après)"
    ])

# --- 3. LE FORMULAIRE ---
with st.form("beck_form"):
    # Situation
    col1, col2 = st.columns(2)
    with col1:
        date_event = st.date_input("Date", datetime.now())
    with col2:
        lieu = st.text_input("Lieu / Contexte")
    
    situation = st.text_area("Situation (Fait déclencheur)")
    
    st.divider()
    
    # Emotion
    emotion = st.selectbox("Émotion principale", ["Tristesse", "Anxiété", "Colère", "Culpabilité", "Honte", "Joie", "Autre"])
    intensite_avant = st.slider("Intensité de l'émotion (0-10)", 0, 10, 7)
    
    st.divider()
    
    # Pensées & Distorsions
    pensee_auto = st.text_area("Pensée Automatique (Ce qui vous traverse l'esprit)")
    croyance_auto = st.slider("Croyance dans cette pensée (0-10)", 0, 10, 8)
    
    # --- LA SECTION DISTORSIONS EST ICI ---
    with st.expander("🔍 Identifier les Distorsions Cognitives (Cliquez pour ouvrir)"):
        st.write("Cochez les pièges dans lesquels vous pensez être tombé :")
        selected_distorsions = []
        for dist, desc in distorsions_dict.items():
            if st.checkbox(f"**{dist}** : {desc}"):
                selected_distorsions.append(dist)
    
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
        # --- 4. SAUVEGARDE ---
        new_row = {
            "Date": str(date_event),
            "Situation": f"{lieu} - {situation}",
            "Émotion": emotion,
            "Intensité (Avant)": intensite_avant,
            "Pensée Auto": pensee_auto,
            "Distorsions": ", ".join(selected_distorsions), # On enregistre la liste cochée
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