import streamlit as st
import pandas as pd
import altair as alt # NOUVEAU : Pour le graphique groupé
from datetime import datetime

st.set_page_config(page_title="Registre des Activités", page_icon="📝")

st.title("📝 Registre des Activités")

# --- 1. INITIALISATION DES MÉMOIRES ---
if "data_activites" not in st.session_state:
    st.session_state.data_activites = pd.DataFrame(columns=[
        "Date", "Heure", "Activité", 
        "Plaisir (0-10)", "Maîtrise (0-10)", "Satisfaction (0-10)"
    ])

if "data_humeur_jour" not in st.session_state:
    st.session_state.data_humeur_jour = pd.DataFrame(columns=["Date", "Humeur Globale (0-10)"])

# --- 2. FORMULAIRE A : AJOUTER UNE ACTIVITÉ ---
st.subheader("1. Ajouter une activité")

with st.form("activity_form"):
    col_date, col_heure = st.columns([1, 1])
    with col_date:
        date_act = st.date_input("Date de l'activité", datetime.now())
    with col_heure:
        creneaux = [f"{h}h - {h+1}h" for h in range(6, 24)] + ["00h - 01h", "Autre"]
        heure_act = st.selectbox("Créneau horaire", creneaux)

    activite_desc = st.text_input("Qu'avez-vous fait ?", placeholder="Ex: Petit déjeuner, Travail, Marche...")

    st.write("**Évaluation de l'activité :**")
    c1, c2, c3 = st.columns(3)
    with c1:
        plaisir = st.number_input("🎉 Plaisir (0-10)", 0, 10, 5)
    with c2:
        maitrise = st.number_input("💪 Maîtrise (0-10)", 0, 10, 5)
    with c3:
        satisfaction = st.number_input("🏆 Satisfaction (0-10)", 0, 10, 5)

    submitted_act = st.form_submit_button("Ajouter l'activité")

    if submitted_act:
        new_row = {
            "Date": str(date_act),
            "Heure": heure_act,
            "Activité": activite_desc,
            "Plaisir (0-10)": plaisir,
            "Maîtrise (0-10)": maitrise,
            "Satisfaction (0-10)": satisfaction
        }
        st.session_state.data_activites = pd.concat(
            [st.session_state.data_activites, pd.DataFrame([new_row])],
            ignore_index=True
        )
        st.success("Activité ajoutée !")

st.divider()

# --- 3. FORMULAIRE B : HUMEUR GLOBALE ---
st.subheader("2. Bilan de la journée (Humeur globale)")
st.caption("À remplir une fois la journée terminée.")

with st.form("humeur_form"):
    date_humeur = st.date_input("Date du bilan", datetime.now(), key="date_bilan")
    humeur_globale = st.slider("🌈 Comment évaluez-vous votre humeur globale aujourd'hui ? (0-10)", 0, 10, 5)
    
    submitted_humeur = st.form_submit_button("Enregistrer l'humeur du jour")
    
    if submitted_humeur:
        new_humeur = {
            "Date": str(date_humeur),
            "Humeur Globale (0-10)": humeur_globale
        }
        st.session_state.data_humeur_jour = pd.concat(
            [st.session_state.data_humeur_jour, pd.DataFrame([new_humeur])],
            ignore_index=True
        )
        st.success(f"Humeur du {date_humeur} enregistrée !")

# --- 4. APERÇU DU JOUR (AVEC GRAPHIQUE BARRES GROUPÉES) ---
st.divider()
st.subheader(f"Résumé du {datetime.now().strftime('%d/%m/%Y')}")

# Filtrer les activités d'aujourd'hui
today_str = str(datetime.now().date())
df_today = st.session_state.data_activites[st.session_state.data_activites["Date"] == today_str]

if not df_today.empty:
    # Tableau
    st.dataframe(df_today[["Heure", "Activité", "Plaisir (0-10)", "Maîtrise (0-10)", "Satisfaction (0-10)"]], use_container_width=True)
    
    st.write("**Visualisation des activités du jour :**")
    
    # --- GRAPHIQUE ALTAIR (Barres Groupées) ---
    # 1. On prépare les données en format "long" pour Altair
    # Cela transforme le tableau pour avoir une ligne par type de score
    df_chart = df_today.copy()
    
    # Conversion forcée en numérique pour éviter les erreurs
    cols_score = ["Plaisir (0-10)", "Maîtrise (0-10)", "Satisfaction (0-10)"]
    for col in cols_score:
        df_chart[col] = pd.to_numeric(df_chart[col], errors='coerce')

    # Transformation ("Melt")
    df_long = df_chart.melt(
        id_vars=["Activité"], 
        value_vars=cols_score, 
        var_name="Indicateur", 
        value_name="Score"
    )

    # 2. Création du graphique
    chart = alt.Chart(df_long).mark_bar().encode(
        x=alt.X('Activité:N', title=None, axis=alt.Axis(labelAngle=0)), # Activité en bas (texte horizontal)
        y=alt.Y('Score:Q', title='Note (0-10)'),
        color=alt.Color('Indicateur:N', legend=alt.Legend(title="Type")), # Couleur selon Plaisir/Maitrise/Satisf
        xOffset='Indicateur:N' # C'est LA clé : décale les barres pour les grouper côte à côte
    ).properties(
        height=350 # Hauteur du graphique
    )
    
    st.altair_chart(chart, use_container_width=True)

else:
    st.info("Aucune activité notée pour aujourd'hui.")

st.divider()
st.page_link("streamlit_app.py", label="Retour à l'accueil", icon="🏠")