import streamlit as st
import pandas as pd

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
        # On affiche d'abord le tableau brut pour référence
        with st.expander("Voir le tableau détaillé des données"):
            st.dataframe(st.session_state.data_activites, use_container_width=True)

        col_g, col_d = st.columns(2)

        # ---------------------------------------------------------
        # GRAPHIQUE 2 : ÉVOLUTION CHRONOLOGIQUE (Ligne)
        # ---------------------------------------------------------
        with col_g:
            st.subheader("2. Fluctuations au fil du temps")
            st.write("Comment varient vos sentiments activité après activité ?")
            # On affiche les 3 courbes sur le même graph
            st.line_chart(
                st.session_state.data_activites[["Plaisir (0-10)", "Maîtrise (0-10)", "Satisfaction (0-10)"]]
            )

        # ---------------------------------------------------------
        # GRAPHIQUE 3 : MOYENNE PAR ACTIVITÉ (Barres)
        # ---------------------------------------------------------
        with col_d:
            st.subheader("3. Quelles activités vous font du bien ?")
            st.write("Moyenne des scores par type d'activité.")
            
            # Calcul magique : on groupe par nom d'activité et on fait la moyenne
            # On force la conversion en nombres pour éviter les bugs
            df_act = st.session_state.data_activites.copy()
            cols_to_mean = ["Plaisir (0-10)", "Maîtrise (0-10)", "Satisfaction (0-10)"]
            
            # Petit nettoyage pour être sûr que ce sont des chiffres
            for col in cols_to_mean:
                df_act[col] = pd.to_numeric(df_act[col], errors='coerce')
            
            # Le calcul de la moyenne
            df_mean = df_act.groupby("Activité")[cols_to_mean].mean()
            
            # Affichage en diagramme à barres
            st.bar_chart(df_mean)

    else:
        st.info("Aucune activité enregistrée. Commencez à remplir votre registre !")

st.divider()
st.page_link("streamlit_app.py", label="Retour à l'accueil", icon="🏠")