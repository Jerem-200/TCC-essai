import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="Historique", page_icon="📜", layout="wide")

st.title("📜 Historique de vos progrès")

# --- INITIALISATION ---
if "data_beck" not in st.session_state:
    st.session_state.data_beck = pd.DataFrame(columns=["Date", "Situation", "Émotion", "Pensée Auto"])
if "data_echelles" not in st.session_state:
    st.session_state.data_echelles = pd.DataFrame(columns=["Date", "Type", "Score", "Commentaire"])
if "data_activites" not in st.session_state:
    st.session_state.data_activites = pd.DataFrame(columns=["Date", "Heure", "Activité", "Plaisir (0-10)", "Maîtrise (0-10)", "Satisfaction (0-10)"])
if "data_humeur_jour" not in st.session_state:
    st.session_state.data_humeur_jour = pd.DataFrame(columns=["Date", "Humeur Globale (0-10)"])

# --- ONGLETS ---
tab1, tab2, tab3 = st.tabs(["🧩 Colonnes de Beck", "📊 Échelles & Scores", "📝 Registre & Activités"])

# ONGLET 1
with tab1:
    st.header("Restructuration")
    if not st.session_state.data_beck.empty:
        st.dataframe(st.session_state.data_beck, use_container_width=True)
    else:
        st.info("Pas de données.")

# ONGLET 2
with tab2:
    st.header("Suivi des scores (BDI)")
    if not st.session_state.data_echelles.empty:
        st.dataframe(st.session_state.data_echelles, use_container_width=True)
        try:
            st.line_chart(st.session_state.data_echelles.set_index("Date")["Score"])
        except:
            pass
    else:
        st.info("Pas de données.")

# ONGLET 3 : LE REGISTRE
with tab3:
    # 1. HUMEUR GLOBALE
    st.subheader("1. Évolution de l'Humeur Globale")
    if not st.session_state.data_humeur_jour.empty:
        df_humeur = st.session_state.data_humeur_jour.drop_duplicates(subset=["Date"], keep='last')
        st.line_chart(df_humeur.set_index("Date")["Humeur Globale (0-10)"])
    else:
        st.info("Notez votre humeur en fin de journée.")

    st.divider()

    # 2. ACTIVITÉS
    if not st.session_state.data_activites.empty:
        
        # BARRES MOYENNES (Grouped Bar Chart)
        st.subheader("2. Quelles activités vous font du bien ? (Moyenne)")
        
        df_act = st.session_state.data_activites.copy()
        cols_to_mean = ["Plaisir (0-10)", "Maîtrise (0-10)", "Satisfaction (0-10)"]
        for col in cols_to_mean:
            df_act[col] = pd.to_numeric(df_act[col], errors='coerce')
        
        df_mean = df_act.groupby("Activité")[cols_to_mean].mean().reset_index()
        df_long_bar = df_mean.melt("Activité", var_name="Type", value_name="Score")

        chart_bar = alt.Chart(df_long_bar).mark_bar().encode(
            x=alt.X('Activité:N', title=None, axis=alt.Axis(labelAngle=0)),
            y=alt.Y('Score:Q', title='Score Moyen'),
            color=alt.Color('Type:N', legend=alt.Legend(title="Indicateur")),
            xOffset='Type:N',
            tooltip=['Activité', 'Type', alt.Tooltip('Score', format='.1f')]
        ).properties(height=350)
        
        st.altair_chart(chart_bar, use_container_width=True)

        st.divider()

        # -------------------------------------------------------------
        # GRAPHIQUE 3 : ÉVOLUTION CHRONOLOGIQUE (GROS POINTS)
        # -------------------------------------------------------------
        st.subheader("3. Fluctuations au fil du temps")
        st.write("Survolez les points pour voir le détail.")
        
        # Préparation des données
        df_line = st.session_state.data_activites.copy()
        try:
            # On construit une date complète pour l'axe chronologique
            df_line['Full_Date'] = pd.to_datetime(df_line['Date'].astype(str) + ' ' + df_line['Heure'].astype(str), errors='coerce')
        except:
            df_line['Full_Date'] = pd.to_datetime(df_line['Date'])

        # Format long
        df_line_long = df_line.melt(
            id_vars=['Full_Date', 'Activité'], 
            value_vars=["Plaisir (0-10)", "Maîtrise (0-10)", "Satisfaction (0-10)"],
            var_name="Indicateur",
            value_name="Score"
        )

        # Construction du graphique simple mais avec GROS POINTS
        line_chart = alt.Chart(df_line_long).mark_line(
            # C'est ici que ça se joue : size=100 fait des gros points bien visibles
            point=alt.OverlayMarkDef(size=100, filled=True) 
        ).encode(
            x=alt.X('Full_Date:T', title='Heure', axis=alt.Axis(format='%H:%M')),
            y=alt.Y('Score:Q', title='Note (0-10)'),
            color=alt.Color('Indicateur:N', legend=alt.Legend(title="Type")),
            
            # Info-bulle classique (s'affiche quand on touche le gros point)
            tooltip=[
                alt.Tooltip('Full_Date', title='Heure', format='%H:%M'),
                alt.Tooltip('Activité', title='Activité'),
                alt.Tooltip('Indicateur', title='Type'),
                alt.Tooltip('Score', title='Note')
            ]
        ).interactive()
        
        st.altair_chart(line_chart, use_container_width=True)
        
        with st.expander("Voir le tableau détaillé"):
            st.dataframe(df_line.sort_values(by="Full_Date")[["Date", "Heure", "Activité", "Plaisir (0-10)", "Maîtrise (0-10)", "Satisfaction (0-10)"]], use_container_width=True)

    else:
        st.info("Aucune activité enregistrée.")

st.divider()
st.page_link("streamlit_app.py", label="Retour à l'accueil", icon="🏠")