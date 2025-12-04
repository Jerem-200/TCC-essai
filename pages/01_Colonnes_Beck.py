import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Colonnes de Beck", page_icon="🧩", layout="wide")

st.title("🧩 Colonnes de Beck - Restructuration Cognitive")

# --- Dictionnaire des Distorsions (Basé sur votre PDF) ---
distorsions_dict = {
    "Pensée tout ou rien": "Penser de manière extrême (soit parfait, soit terrible). [cite: 125-127]",
    "Filtre mental": "Se focaliser sur un détail négatif en ignorant le reste. [cite: 130-131]",
    "Catastrophisme": "Imaginer le pire scénario possible ('Et si...?'). [cite: 133-134]",
    "Surgénéralisation": "Tirer une conclusion générale d'un seul événement. [cite: 136-137]",
    "Disqualification du positif": "Rejeter les expériences positives ('Ça ne compte pas'). [cite: 139-140]",
    "Culpabilisation": "S'attribuer la faute pour des choses hors de notre contrôle. [cite: 142-143]",
    "Raisonnement émotionnel": "Croire que si on le ressent, c'est que c'est vrai. [cite: 146]",
    "Les 'Je dois / Il faut'": "Règles rigides sur comment on devrait se comporter. [cite: 148-149]",
    "Conclusion hâtive": "Juger sans preuves suffisantes (lecture de pensée). [cite: 151-152]",
    "Étiquetage": "Se coller une étiquette définitive ('Je suis nul'). [cite: 154-155]",
    "Comparaison sociale": "Se comparer aux autres en ne voyant que ses défauts. [cite: 159]",
    "Fusion pensée-action": "Croire que penser à une chose équivaut à la faire. [cite: 160]"
}

# --- ÉTAPE 1 : LA SITUATION ---
st.header("1. La Situation")
col1, col2 = st.columns(2)
with col1:
    date_event = st.date_input("Date", datetime.now())
    heure_event = st.time_input("Heure", datetime.now())
with col2:
    lieu = st.text_input("Lieu (Où étiez-vous ? Avec qui ?)")

situation = st.text_area("Description factuelle (Que s'est-il passé ? Comme une caméra)", height=100)

# --- ÉTAPE 2 : ÉMOTION INITIALE ---
st.header("2. L'Émotion")
st.markdown("Aidez-vous de la liste ci-dessous si besoin (inspirée de la roue des émotions).")

# Liste simplifiée basée sur Plutchik [cite: 22, 39, 57, 70, 6, 14, 121]
choix_emotions = ["", "Tristesse", "Anxiété / Peur", "Colère", "Culpabilité", "Honte", "Joie", "Surprise", "Dégoût", "Autre..."]
emotion_select = st.selectbox("Quelle émotion ressentez-vous ?", choix_emotions)

if emotion_select == "Autre...":
    emotion_input = st.text_input("Précisez votre émotion :")
else:
    emotion_input = emotion_select

intensite_1 = st.slider("Intensité de l'émotion (0 = Nulle, 100 = Maximale)", 0, 100, 70, key="int1")

# --- ÉTAPE 3 : PENSÉE AUTOMATIQUE ---
st.header("3. Pensée Automatique & Distorsions")
pensee_auto = st.text_area("Qu'est-ce qui vous traverse l'esprit ?", placeholder="Ex: Je n'y arriverai jamais...")
croyance_1 = st.slider("À quel point croyez-vous cette pensée ? (0-100%)", 0, 100, 80, key="croy1")

with st.expander("🔍 Voir la liste des Distorsions Cognitives (Aide)"):
    st.write("Cochez les pièges dans lesquels vous tombez :")
    distorsions_check = []
    for dist, desc in distorsions_dict.items():
        if st.checkbox(f"**{dist}** : {desc}"):
            distorsions_check.append(dist)

# --- ÉTAPE 4 : RESTRUCTURATION ---
st.header("4. Pensée Alternative / Rationnelle")
pensee_alt = st.text_area("Que diriez-vous à un ami dans la même situation ? Quelle est une vision plus réaliste ?", height=100)
croyance_alt = st.slider("À quel point croyez-vous cette nouvelle pensée ? (0-100%)", 0, 100, 50, key="croy_alt")

# --- ÉTAPE 5 : RÉSULTAT ---
st.header("5. Ré-évaluation")
col_res1, col_res2 = st.columns(2)
with col_res1:
    croyance_2 = st.slider("Nouveau degré de croyance en la pensée automatique initiale :", 0, 100, 40, key="croy2")
with col_res2:
    intensite_2 = st.slider("Nouvelle intensité de l'émotion :", 0, 100, 40, key="int2")

# --- BOUTON DE SAUVEGARDE (Simulation pour l'instant) ---
if st.button("Enregistrer l'exercice"):
    st.success("Exercice enregistré ! (Simulation - Code à connecter à Google Sheets plus tard)")
    # Ici, nous mettrons plus tard le code 'row = [...] worksheet.append_row(row)'
    resultats = {
        "Date": str(date_event),
        "Situation": situation,
        "Emotion": emotion_input,
        "Intensité Avant": intensite_1,
        "Pensée Auto": pensee_auto,
        "Distorsions": ", ".join(distorsions_check),
        "Pensée Rationnelle": pensee_alt,
        "Intensité Après": intensite_2
    }
    st.json(resultats) # Affiche ce qui serait envoyé à la base de données