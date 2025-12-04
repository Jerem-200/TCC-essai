import streamlit as st
import pandas as pd
import altair as alt # Bibliothèque nécessaire pour le graphique en barres groupées

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

# ONGLET 3 : LE REGISTRE DES ACTIVITÉS (Vos 3 graphiques)
with tab3:
    # ---------------------------------------------------------
    # GRAPHIQUE 1 : ÉVOLUTION DE L'HUMEUR GLOBALE (Jour par Jour)
    # ---------------------------------------------------------
    st.subheader("1. Évolution de l'Humeur Globale")
    if not st.session_state.data_humeur_jour.empty:
        # On nettoie les doublons (on garde la dernière note du jour)
        df_humeur = st.session_state.data_humeur_jour.drop_duplicates(subset=["Date"], keep='last')
        st.line_chart(df_humeur.set_index("Date")["Humeur Globale (0-10)"])
    else:
        st.info("Notez votre humeur en fin de journée dans le Registre pour voir cette courbe.")

    st.divider()

    # Vérification s'il y a des activités pour afficher la suite
    if not st.session_state.data_activites.empty:
        
        # ---------------------------------------------------------
        # GRAPHIQUE 2 : MOYENNE PAR ACTIVITÉ (Barres groupées style "Image")
        # ---------------------------------------------------------
        st.subheader("2. Quelles activités vous font du bien ? (Moyenne)")
        st.write("Comparaison des scores moyens par type d'activité.")

        # Préparation des données
        df_act = st.session_state.data_activites.copy()
        cols_to_mean = ["Plaisir (0-10)", "Maîtrise (0-10)", "Satisfaction (0-10)"]
        
        # Nettoyage et conversion en numérique
        for col in cols_to_mean:
            df_act[col] = pd.to_numeric(df_act[col], errors='coerce')
        
        # Calcul de la moyenne par activité
        df_mean = df_act.groupby("Activité")[cols_to_mean].mean().reset_index()
        
        # Transformation pour le graphique (Format long)
        df_long = df_mean.melt("Activité", var_name="Type", value_name="Score")

        # Création du graphique Altair (Barres côte à côte)
        chart = alt.Chart(df_long).mark_bar().encode(
            x=alt.X('Activité:N', title=None),  # L'activité en bas
            y=alt.Y('Score:Q', title='Score Moyen (0-10)'),
            color=alt.Color('Type:N', legend=alt.Legend(title="Indicateur")), # Couleur selon le type
            xOffset='Type:N' # C'est cette option qui met les barres côte à côte !
        ).properties(
            height=400 # Hauteur du graphique
        )
        
        st.altair_chart(chart, use_container_width=True)

        st.divider()

        # ---------------------------------------------------------
        # GRAPHIQUE 3 : ÉVOLUTION CHRONOLOGIQUE (Ligne)
        # ---------------------------------------------------------
        st.subheader("3. Fluctuations au fil du temps")
        st.write("Détail de chaque activité enregistrée, dans l'ordre chronologique.")
        st.line_chart(
            st.session_state.data_activites[["Plaisir (0-10)", "Maîtrise (0-10)", "Satisfaction (0-10)"]]
        )
        
        with st.expander("Voir le tableau détaillé des données"):
            st.dataframe(st.session_state.data_activites, use_container_width=True)

    else:
        st.info("Aucune activité enregistrée. Commencez à remplir votre registre !")

st.divider()
st.page_link("streamlit_app.py", label="Retour à l'accueil", icon="🏠")