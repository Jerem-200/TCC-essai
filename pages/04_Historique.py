import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="Historique", page_icon="📜", layout="wide")
st.title("📜 Historique de vos progrès")

# --- INITIALISATION ---
if "data_beck" not in st.session_state: st.session_state.data_beck = pd.DataFrame(columns=["Date", "Situation", "Émotion", "Pensée Auto"])
if "data_echelles" not in st.session_state: st.session_state.data_echelles = pd.DataFrame(columns=["Date", "Type", "Score", "Commentaire"])
if "data_activites" not in st.session_state: st.session_state.data_activites = pd.DataFrame(columns=["Date", "Heure", "Activité", "Plaisir (0-10)", "Maîtrise (0-10)", "Satisfaction (0-10)"])
if "data_humeur_jour" not in st.session_state: st.session_state.data_humeur_jour = pd.DataFrame(columns=["Date", "Humeur Globale (0-10)"])
# NOUVEAU
if "data_problemes" not in st.session_state: st.session_state.data_problemes = pd.DataFrame(columns=["Date", "Problème", "Objectif", "Solution Choisie"])

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

with t3: # Onglet Registre (Graphiques)
    st.subheader("Humeur Globale")
    if not st.session_state.data_humeur_jour.empty:
        df_humeur = st.session_state.data_humeur_jour.drop_duplicates(subset=["Date"], keep='last')
        st.line_chart(df_humeur.set_index("Date")["Humeur Globale (0-10)"])
    
    st.divider()
    st.subheader("Activités (Moyennes)")
    if not st.session_state.data_activites.empty:
        df_act = st.session_state.data_activites.copy()
        cols = ["Plaisir (0-10)", "Maîtrise (0-10)", "Satisfaction (0-10)"]
        for c in cols: df_act[c] = pd.to_numeric(df_act[c], errors='coerce')
        
        df_mean = df_act.groupby("Activité")[cols].mean().reset_index()
        df_long = df_mean.melt("Activité", var_name="Type", value_name="Score")
        
        chart = alt.Chart(df_long).mark_bar().encode(
            x=alt.X('Activité:N', axis=alt.Axis(labelAngle=0)), y='Score:Q',
            color='Type:N', xOffset='Type:N', tooltip=['Activité', 'Type', alt.Tooltip('Score', format='.1f')]
        ).properties(height=350)
        st.altair_chart(chart, use_container_width=True)
    else: st.info("Vide")

# NOUVEL ONGLET 4
with t4:
    st.header("Vos Plans d'Action")
    if not st.session_state.data_problemes.empty:
        st.dataframe(st.session_state.data_problemes, use_container_width=True)
    else:
        st.info("Aucun problème enregistré.")

st.divider()
st.page_link("streamlit_app.py", label="Retour à l'accueil", icon="🏠")