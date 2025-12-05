import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="Historique", page_icon="📜", layout="wide")
st.title("📜 Historique de vos progrès")

# --- INITIALISATION ---
if "data_beck" not in st.session_state: st.session_state.data_beck = pd.DataFrame()
if "data_echelles" not in st.session_state: st.session_state.data_echelles = pd.DataFrame()
if "data_activites" not in st.session_state: st.session_state.data_activites = pd.DataFrame()
if "data_humeur_jour" not in st.session_state: st.session_state.data_humeur_jour = pd.DataFrame()
# NOUVEAU
if "data_problemes" not in st.session_state: st.session_state.data_problemes = pd.DataFrame(columns=["Date", "Problème", "Solution Choisie"])

# --- 4 ONGLETS ---
t1, t2, t3, t4 = st.tabs(["🧩 Beck", "📊 Scores", "📝 Registre", "💡 Problèmes"])

with t1:
    if not st.session_state.data_beck.empty:
        st.dataframe(st.session_state.data_beck, use_container_width=True)
    else: st.info("Vide")

with t2:
    if not st.session_state.data_echelles.empty:
        st.dataframe(st.session_state.data_echelles, use_container_width=True)
    else: st.info("Vide")

with t3:
    if not st.session_state.data_humeur_jour.empty:
        st.write("### Humeur")
        st.line_chart(st.session_state.data_humeur_jour.set_index("Date")["Humeur Globale (0-10)"])
    if not st.session_state.data_activites.empty:
        st.write("### Activités")
        st.dataframe(st.session_state.data_activites, use_container_width=True)
    else: st.info("Vide")

# NOUVEL ONGLET
with t4:
    st.subheader("Plans d'actions générés")
    if not st.session_state.data_problemes.empty:
        st.dataframe(st.session_state.data_problemes, use_container_width=True)
    else:
        st.info("Aucun problème traité pour l'instant.")

st.divider()
st.page_link("streamlit_app.py", label="Retour à l'accueil", icon="🏠")