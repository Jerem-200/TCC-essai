import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="Historique", page_icon="📜", layout="wide")

st.title("📜 Historique de vos progrès")

# --- INITIALISATION DE SÉCURITÉ ---
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

# ONGLET 3 : LE REGISTRE DES ACTIVITÉS
with tab3:
    # ---------------------------------------------------------
    # GRAPHIQUE 1 : ÉVOLUTION DE L'HUMEUR GLOBALE (Jour par Jour)
    # ---------------------------------------------------------
    st.subheader("1. Évolution de l'Humeur Globale")
    if not st.session_state.data_humeur_jour.empty:
        df_humeur = st.session_state.data_humeur_jour.drop_duplicates(subset=["Date"], keep='last')
        st.line_chart(df_humeur.set_index("Date")["Humeur Globale (0-10)"])
    else:
        st.info("Notez votre humeur en fin de journée dans le Registre pour voir cette courbe.")

    st.divider()

    # Vérification s'il y a des activités pour afficher la suite
    if not st.session_state.data_activites.empty:
        
        # ---------------------------------------------------------
        # GRAPHIQUE 2 : MOYENNE PAR ACTIVITÉ (Barres groupées)
        # ---------------------------------------------------------
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

        # ---------------------------------------------------------
        # GRAPHIQUE 3 : ÉVOLUTION CHRONOLOGIQUE (CORRIGÉ AVEC TEMPS ET TOOLTIP)
        # ---------------------------------------------------------
        st.subheader("3. Fluctuations au fil du temps")
        st.write("Détail de chaque activité enregistrée, dans l'ordre chronologique.")
        
        # 1. Préparation des données pour le temps
        df_line = st.session_state.data_activites.copy()
        
        # Astuce : On prend la date et on essaye d'extraire l'heure de début (ex: "14h" -> 14)
        # On crée une colonne datetime pour qu'Altair comprenne le temps
        try:
            # On extrait le premier nombre de la chaine "XXh - YYh"
            df_line['Heure_Start'] = df_line['Heure'].str.extract(r'(\d+)').astype(str)
            # On crée une vraie date complète (YYYY-MM-DD HH:00)
            df_line['Full_Date'] = pd.to_datetime(df_line['Date'].astype(str) + ' ' + df_line['Heure_Start'] + ':00', errors='coerce')
        except:
            # Si ça échoue, on garde juste la date
            df_line['Full_Date'] = pd.to_datetime(df_line['Date'])

        # 2. Mise en forme longue pour Altair
        df_line_long = df_line.melt(
            id_vars=['Full_Date', 'Date', 'Heure', 'Activité'], # On garde ces colonnes pour le tooltip
            value_vars=["Plaisir (0-10)", "Maîtrise (0-10)", "Satisfaction (0-10)"],
            var_name="Indicateur",
            value_name="Score"
        )

        # 3. Création du graphique avancé
        line_chart = alt.Chart(df_line_long).mark_line(point=True).encode(
            # Axe X : Temps (Format jour + heure)
            x=alt.X('Full_Date:T', title='Date & Heure', axis=alt.Axis(format='%d/%m %Hh')),
            
            # Axe Y : Le score
            y=alt.Y('Score:Q', title='Note (0-10)'),
            
            # Couleur : La ligne change de couleur selon l'indicateur
            color=alt.Color('Indicateur:N', legend=alt.Legend(title="Type")),
            
            # C'EST ICI : Les infos qui s'affichent au survol de la souris
            tooltip=[
                alt.Tooltip('Full_Date', title='Date/Heure', format='%d/%m %H:%M'),
                alt.Tooltip('Activité', title='Activité'), # <-- LE NOM DE L'ACTIVITÉ !
                alt.Tooltip('Indicateur', title='Type'),
                alt.Tooltip('Score', title='Note')
            ]
        ).interactive() # Permet de zoomer/déplacer
        
        st.altair_chart(line_chart, use_container_width=True)
        
        with st.expander("Voir le tableau détaillé des données"):
            st.dataframe(st.session_state.data_activites, use_container_width=True)

    else:
        st.info("Aucune activité enregistrée.")

st.divider()
st.page_link("streamlit_app.py", label="Retour à l'accueil", icon="🏠")