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
if "data_problemes" not in st.session_state: st.session_state.data_problemes = pd.DataFrame(columns=["Date", "Problème", "Objectif", "Solution Choisie"])

# --- 4 ONGLETS ---
t1, t2, t3, t4 = st.tabs(["🧩 Beck", "📊 Scores", "📝 Registre", "💡 Problèmes"])

# 1. BECK
with t1:
    if not st.session_state.data_beck.empty:
        st.dataframe(st.session_state.data_beck, use_container_width=True)
    else: st.info("Vide")

# 2. SCORES
with t2:
    if not st.session_state.data_echelles.empty:
        st.dataframe(st.session_state.data_echelles, use_container_width=True)
    else: st.info("Vide")

# 3. REGISTRE (AVEC LES 3 GRAPHIQUES)
with t3:
    # --- A. HUMEUR GLOBALE ---
    st.subheader("1. Humeur Globale")
    if not st.session_state.data_humeur_jour.empty:
        df_humeur = st.session_state.data_humeur_jour.drop_duplicates(subset=["Date"], keep='last')
        st.line_chart(df_humeur.set_index("Date")["Humeur Globale (0-10)"])
    else:
        st.info("Pas de données d'humeur.")
    
    st.divider()
    
    # Vérification s'il y a des activités pour les graphiques suivants
    if not st.session_state.data_activites.empty:
        # Préparation des données (Conversion numérique)
        df_act = st.session_state.data_activites.copy()
        cols = ["Plaisir (0-10)", "Maîtrise (0-10)", "Satisfaction (0-10)"]
        for c in cols: df_act[c] = pd.to_numeric(df_act[c], errors='coerce')

        # --- B. ACTIVITÉS (MOYENNES / BARRES) ---
        st.subheader("2. Comparatif par Activité (Moyenne)")
        df_mean = df_act.groupby("Activité")[cols].mean().reset_index()
        df_long_bar = df_mean.melt("Activité", var_name="Type", value_name="Score")
        
        chart_bar = alt.Chart(df_long_bar).mark_bar().encode(
            x=alt.X('Activité:N', axis=alt.Axis(labelAngle=0)), 
            y='Score:Q',
            color='Type:N', 
            xOffset='Type:N', 
            tooltip=['Activité', 'Type', alt.Tooltip('Score', format='.1f')]
        ).properties(height=350)
        st.altair_chart(chart_bar, use_container_width=True)

        st.divider()

        # --- C. ÉVOLUTION CHRONOLOGIQUE (LIGNE + POINTS) ---
        # C'est celui-ci qui manquait !
        st.subheader("3. Fluctuations au fil du temps")
        st.write("Détail chronologique précis.")

        # Création de la date complète pour l'axe X
        try:
            df_act['Full_Date'] = pd.to_datetime(df_act['Date'].astype(str) + ' ' + df_act['Heure'].astype(str), errors='coerce')
        except:
            df_act['Full_Date'] = pd.to_datetime(df_act['Date'])

        # Format long pour la ligne
        df_line_long = df_act.melt(
            id_vars=['Full_Date', 'Activité'], 
            value_vars=cols,
            var_name="Indicateur",
            value_name="Score"
        )

        # Graphique Ligne avec Gros Points
        line_chart = alt.Chart(df_line_long).mark_line(
            point=alt.OverlayMarkDef(size=100, filled=True) # Gros points visibles
        ).encode(
            x=alt.X('Full_Date:T', title='Temps', axis=alt.Axis(format='%d/%m %H:%M')), 
            y=alt.Y('Score:Q', title='Note (0-10)'),
            color='Indicateur:N',
            tooltip=[
                alt.Tooltip('Full_Date', title='Date', format='%d/%m %H:%M'),
                alt.Tooltip('Activité', title='Activité'),
                alt.Tooltip('Indicateur', title='Type'),
                alt.Tooltip('Score', title='Note')
            ]
        ).interactive()
        
        st.altair_chart(line_chart, use_container_width=True)

    else: 
        st.info("Pas d'activités enregistrées.")

# 4. PROBLÈMES
with t4:
    st.header("Vos Plans d'Action")
    if not st.session_state.data_problemes.empty:
        st.dataframe(st.session_state.data_problemes, use_container_width=True)
    else:
        st.info("Aucun problème enregistré.")

st.divider()
st.page_link("streamlit_app.py", label="Retour à l'accueil", icon="🏠")