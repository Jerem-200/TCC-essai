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

# --- LES ONGLETS ---
tab1, tab2, tab3 = st.tabs(["🧩 Colonnes de Beck", "📊 Échelles & Scores", "📝 Registre & Activités"])

# ONGLET 1 : BECK
with tab1:
    st.header("Restructuration")
    if not st.session_state.data_beck.empty:
        st.dataframe(st.session_state.data_beck, use_container_width=True)
    else:
        st.info("Pas de données.")

# ONGLET 2 : BDI
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
        
        # BARRES MOYENNES
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

        # GRAPHIQUE 3 : ÉVOLUTION CHRONOLOGIQUE PRÉCISE
        st.subheader("3. Fluctuations au fil du temps")
        st.write("Chronologie précise des activités.")
        
        # Préparation des données avec date précise
        df_line = st.session_state.data_activites.copy()
        
        # On combine Date + Heure (HH:MM) proprement
        # Ex: "2023-12-05" + "14:30" -> Timestamp complet
        df_line['Full_Date'] = pd.to_datetime(df_line['Date'].astype(str) + ' ' + df_line['Heure'].astype(str), errors='coerce')

        # Format long pour Altair
        df_line_long = df_line.melt(
            id_vars=['Full_Date', 'Activité'], 
            value_vars=["Plaisir (0-10)", "Maîtrise (0-10)", "Satisfaction (0-10)"],
            var_name="Indicateur",
            value_name="Score"
        )

        # Graphique
        line_chart = alt.Chart(df_line_long).mark_line(point=True).encode(
            x=alt.X('Full_Date:T', title='Temps', axis=alt.Axis(format='%d/%m %H:%M')), # Format jour/mois heure:minute
            y=alt.Y('Score:Q', title='Note (0-10)'),
            color=alt.Color('Indicateur:N'),
            tooltip=[
                alt.Tooltip('Full_Date', title='Date', format='%d/%m %H:%M'),
                alt.Tooltip('Activité', title='Activité'),
                alt.Tooltip('Indicateur', title='Type'),
                alt.Tooltip('Score', title='Note')
            ]
        ).interactive()
        
        st.altair_chart(line_chart, use_container_width=True)
        
        with st.expander("Voir le tableau détaillé"):
            # On trie le tableau par date et heure avant de l'afficher
            st.dataframe(df_line.sort_values(by="Full_Date")[["Date", "Heure", "Activité", "Plaisir (0-10)", "Maîtrise (0-10)", "Satisfaction (0-10)"]], use_container_width=True)

    else:
        st.info("Aucune activité enregistrée.")

st.divider()
st.page_link("streamlit_app.py", label="Retour à l'accueil", icon="🏠")