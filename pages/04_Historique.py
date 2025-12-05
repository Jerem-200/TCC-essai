import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="Historique", page_icon="📜", layout="wide")
st.title("📜 Historique")

# Init mémoires
if "data_beck" not in st.session_state: st.session_state.data_beck = pd.DataFrame()
if "data_echelles" not in st.session_state: st.session_state.data_echelles = pd.DataFrame()
if "data_activites" not in st.session_state: st.session_state.data_activites = pd.DataFrame()
if "data_humeur_jour" not in st.session_state: st.session_state.data_humeur_jour = pd.DataFrame()
if "data_problemes" not in st.session_state: st.session_state.data_problemes = pd.DataFrame()

# 4 Onglets
t1, t2, t3, t4 = st.tabs(["🧩 Beck", "📊 Scores", "📝 Activités", "💡 Problèmes"])

with t1:
    if not st.session_state.data_beck.empty:
        st.dataframe(st.session_state.data_beck)
    else: st.info("Vide")

with t2:
    if not st.session_state.data_echelles.empty:
        st.dataframe(st.session_state.data_echelles)
    else: st.info("Vide")

with t3:
    if not st.session_state.data_humeur_jour.empty:
        st.write("### Humeur")
        st.line_chart(st.session_state.data_humeur_jour.set_index("Date")["Humeur Globale (0-10)"])
    if not st.session_state.data_activites.empty:
        st.write("### Activités")
        st.dataframe(st.session_state.data_activites)
    else: st.info("Vide")

with t4:
    st.subheader("Plans d'actions")
    if not st.session_state.data_problemes.empty:
        st.dataframe(st.session_state.data_problemes)
    else:
        st.info("Aucun problème traité pour l'instant.")

st.divider()
if st.button("Retour Accueil"):
    st.switch_page("streamlit_app.py")