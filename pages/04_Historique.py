import streamlit as st
import pandas as pd

st.set_page_config(page_title="Historique", page_icon="📜", layout="wide")

st.title("📜 Historique de vos progrès")
st.write("Retrouvez ici l'ensemble de vos exercices et suivis.")

# Initialisation de sécurité
if "data_beck" not in st.session_state:
    st.session_state.data_beck = pd.DataFrame(columns=["Date", "Situation", "Émotion", "Pensée Auto"])
if "data_echelles" not in st.session_state:
    st.session_state.data_echelles = pd.DataFrame(columns=["Date", "Type", "Score", "Commentaire"])
# NOUVEAU : Initialisation Registre
if "data_activites" not in st.session_state:
    st.session_state.data_activites = pd.DataFrame(columns=["Date", "Heure", "Activité", "Plaisir (0-10)", "Maîtrise (0-10)", "Satisfaction (0-10)"])

# Ajout du 3ème onglet
tab1, tab2, tab3 = st.tabs(["🧩 Colonnes de Beck", "📊 Échelles & Scores", "📝 Registre Activités"])

with tab1:
    st.header("Restructuration")
    if not st.session_state.data_beck.empty:
        st.dataframe(st.session_state.data_beck, use_container_width=True)
    else:
        st.info("Pas de données.")

with tab2:
    st.header("Suivi des scores")
    if not st.session_state.data_echelles.empty:
        st.dataframe(st.session_state.data_echelles, use_container_width=True)
        try:
            st.line_chart(st.session_state.data_echelles.set_index("Date")["Score"])
        except:
            pass
    else:
        st.info("Pas de données.")

# NOUVEL ONGLET
with tab3:
    st.header("Journal des Activités")
    if not st.session_state.data_activites.empty:
        st.dataframe(st.session_state.data_activites, use_container_width=True)
        
        # Petit graphique sympa : Plaisir vs Satisfaction
        try:
            st.caption("Évolution du Plaisir et de la Satisfaction par activité")
            st.line_chart(st.session_state.data_activites[["Plaisir (0-10)", "Satisfaction (0-10)"]])
        except:
            pass
    else:
        st.info("Votre registre est vide pour le moment.")

st.divider()
st.page_link("streamlit_app.py", label="Retour à l'accueil", icon="🏠")