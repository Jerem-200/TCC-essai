import streamlit as st
import pandas as pd

st.set_page_config(page_title="Historique", page_icon="📜", layout="wide")

st.title("📜 Historique de vos progrès")
st.write("Retrouvez ici l'ensemble de vos exercices et suivis.")

# Vérification si les données existent (pour éviter les erreurs)
if "data_beck" not in st.session_state:
    st.session_state.data_beck = pd.DataFrame(columns=["Date", "Situation", "Émotion", "Pensée Auto", "Pensée Rationnelle"])

if "data_echelles" not in st.session_state:
    st.session_state.data_echelles = pd.DataFrame(columns=["Date", "Type", "Score", "Commentaire"])

# --- ONGLETS ---
tab1, tab2 = st.tabs(["🧩 Colonnes de Beck", "📊 Échelles & Scores"])

with tab1:
    st.header("Vos restructurations cognitives")
    if not st.session_state.data_beck.empty:
        # On affiche le tableau
        st.dataframe(st.session_state.data_beck, use_container_width=True)
        
        # Petit bonus : Un bouton pour télécharger (utile pour vous l'envoyer)
        csv_beck = st.session_state.data_beck.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Télécharger ces données (CSV)", csv_beck, "beck_historique.csv", "text/csv")
    else:
        st.info("Aucun exercice de Beck enregistré pour cette session.")

with tab2:
    st.header("Suivi de l'humeur (BDI et autres)")
    if not st.session_state.data_echelles.empty:
        st.dataframe(st.session_state.data_echelles, use_container_width=True)
        
        # Bonus : Un graphique simple pour voir l'évolution
        st.subheader("Évolution graphique")
        # On essaie de faire un graphique seulement s'il y a des scores numériques
        try:
            chart_data = st.session_state.data_echelles[["Date", "Score"]].copy()
            st.line_chart(chart_data.set_index("Date"))
        except:
            st.warning("Pas assez de données pour le graphique.")

        csv_echelles = st.session_state.data_echelles.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Télécharger les scores (CSV)", csv_echelles, "scores_historique.csv", "text/csv")
    else:
        st.info("Aucune évaluation enregistrée pour cette session.")

# Bouton retour

