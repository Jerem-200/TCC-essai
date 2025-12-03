import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Exercices TCC", layout="centered")

st.title("🧠 Exercices TCC – Prototype")

# Load local data (in session)
if "data_beck" not in st.session_state:
    st.session_state.data_beck = pd.DataFrame(columns=[
        "Date", "Situation", "Pensée automatique", "Émotion (0-100)",
        "Comportement", "Pensée alternative"
    ])

if "data_echelles" not in st.session_state:
    st.session_state.data_echelles = pd.DataFrame(columns=[
        "Date", "Type d'échelle", "Score", "Commentaire"
    ])

menu = st.sidebar.selectbox("Menu", ["Colonnes de Beck", "Échelles", "Historique"])

if menu == "Colonnes de Beck":
    st.header("🧩 Colonnes de Beck")

    with st.form("beck_form"):
        situation = st.text_area("Situation")
        pensee = st.text_area("Pensée automatique")
        emotion = st.slider("Émotion (0–100)", 0, 100, 50)
        comportement = st.text_area("Comportement")
        alternative = st.text_area("Pensée alternative")
        submitted = st.form_submit_button("Enregistrer")

        if submitted:
            new_row = {
                "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Situation": situation,
                "Pensée automatique": pensee,
                "Émotion (0-100)": emotion,
                "Comportement": comportement,
                "Pensée alternative": alternative,
            }
            st.session_state.data_beck = pd.concat(
                [st.session_state.data_beck, pd.DataFrame([new_row])],
                ignore_index=True
            )
            st.success("Enregistré ✔️")

if menu == "Échelles":
    st.header("📊 Échelles d’auto-évaluation")

    with st.form("scale_form"):
        type_echelle = st.selectbox("Type d’échelle", ["BDI", "Anxiété 0–10", "Humeur 0–10"])
        score = st.number_input("Score", min_value=0, max_value=63)
        commentaire = st.text_area("Commentaire")
        submitted = st.form_submit_button("Enregistrer")

        if submitted:
            new_row = {
                "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Type d'échelle": type_echelle,
                "Score": score,
                "Commentaire": commentaire,
            }
            st.session_state.data_echelles = pd.concat(
                [st.session_state.data_echelles, pd.DataFrame([new_row])],
                ignore_index=True
            )
            st.success("Enregistré ✔️")

if menu == "Historique":
    st.header("📚 Historique des exercices")

    st.subheader("Colonnes de Beck")
    st.dataframe(st.session_state.data_beck)

    st.subheader("Échelles")
    st.dataframe(st.session_state.data_echelles)
