import streamlit as st
import pandas as pd
import altair as alt 
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

# --- MÉMOIRE POUR L'HEURE (Heure et Minute séparées) ---
if "memoire_h" not in st.session_state:
    st.session_state.memoire_h = datetime.now().hour
if "memoire_m" not in st.session_state:
    st.session_state.memoire_m = datetime.now().minute

# --- 2. FORMULAIRE A : AJOUTER UNE ACTIVITÉ ---
st.subheader("1. Ajouter une activité")

with st.form("activity_form"):
    # On divise la première ligne en 3 colonnes pour que ce soit joli
    # Col 1 : Date (Large) | Col 2 : Heure (Petit) | Col 3 : Minute (Petit)
    c_date, c_h, c_m = st.columns([2, 1, 1])
    
    with c_date:
        date_act = st.date_input("Date", datetime.now())
    
    with c_h:
        # Saisie de l'heure (0 à 23)
        heure_h = st.number_input("Heure", min_value=0, max_value=23, value=st.session_state.memoire_h)
        
    with c_m:
        # Saisie des minutes (0 à 59)
        heure_m = st.number_input("Minute", min_value=0, max_value=59, value=st.session_state.memoire_m, step=5)

    activite_desc = st.text_input("Qu'avez-vous fait ?", placeholder="Ex: Petit déjeuner, Travail, Marche...")

    st.write("**Évaluation de l'activité :**")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        plaisir = st.slider("🎉 Plaisir (0-10)", 0, 10, 5, help="Le sentiment de plaisir fait référence à la joie et/ou au bien-être que procure l'activité.")
    with c2:
        maitrise = st.slider("💪 Maîtrise (0-10)", 0, 10, 5, help="Le sentiment de maîtrise désigne le sentiment de compétence que vous pensez avoir dans la réalisation de l’activité.")
    with c3:
        satisfaction = st.slider("🏆 Satisfaction (0-10)", 0, 10, 5, help="Le sentiment de satisfaction est lié à l’accomplissement d’une tâche importante.")

    submitted_act = st.form_submit_button("Ajouter l'activité")

    if submitted_act:
        # On formate l'heure proprement (HH:MM) avec un zéro devant si besoin (ex: 09:05)
        heure_str = f"{heure_h:02d}:{heure_m:02d}"
        
        new_row = {
            "Date": str(date_act),
            "Heure": heure_str,
            "Activité": activite_desc,
            "Plaisir (0-10)": plaisir,
            "Maîtrise (0-10)": maitrise,
            "Satisfaction (0-10)": satisfaction
        }
        st.session_state.data_activites = pd.concat(
            [st.session_state.data_activites, pd.DataFrame([new_row])],
            ignore_index=True
        )
        
        # --- MISE À JOUR DE LA MÉMOIRE ---
        st.session_state.memoire_h = heure_h
        st.session_state.memoire_m = heure_m
        
        st.success(f"Activité ajoutée à {heure_str} !")

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

# --- 4. APERÇU & GESTION ---
st.divider()
st.subheader(f"Résumé du {datetime.now().strftime('%d/%m/%Y')}")

today_str = str(datetime.now().date())
df_today = st.session_state.data_activites[st.session_state.data_activites["Date"] == today_str]

if not df_today.empty:
    # Tableau
    st.dataframe(df_today[["Heure", "Activité", "Plaisir (0-10)", "Maîtrise (0-10)", "Satisfaction (0-10)"]].sort_values("Heure"), use_container_width=True)
    
    st.write("**Visualisation des activités du jour :**")
    
    # Graphique
    df_chart = df_today.copy()
    cols_score = ["Plaisir (0-10)", "Maîtrise (0-10)", "Satisfaction (0-10)"]
    for col in cols_score:
        df_chart[col] = pd.to_numeric(df_chart[col], errors='coerce')

    # Groupement pour moyenne
    df_grouped = df_chart.groupby("Activité")[cols_score].mean().reset_index()

    df_long = df_grouped.melt(
        id_vars=["Activité"], 
        value_vars=cols_score, 
        var_name="Indicateur", 
        value_name="Score"
    )

    chart = alt.Chart(df_long).mark_bar().encode(
        x=alt.X('Activité:N', title=None, axis=alt.Axis(labelAngle=0)), 
        y=alt.Y('Score:Q', title='Note Moyenne (0-10)'),
        color=alt.Color('Indicateur:N', legend=alt.Legend(title="Type")),
        xOffset='Indicateur:N',
        tooltip=['Activité', 'Indicateur', alt.Tooltip('Score', format='.1f')]
    ).properties(height=350)
    
    st.altair_chart(chart, use_container_width=True)

    # Suppression
    st.divider()
    with st.expander("🗑️ Supprimer une activité (En cas d'erreur)"):
        st.write("Sélectionnez l'activité à supprimer ci-dessous :")
        options_dict = {f"{row['Heure']} - {row['Activité']} (ID:{i})": i for i, row in df_today.iterrows()}
        selected_option = st.selectbox("Choisir l'activité", list(options_dict.keys()))
        
        if st.button("Supprimer définitivement"):
            index_to_delete = options_dict[selected_option]
            st.session_state.data_activites = st.session_state.data_activites.drop(index_to_delete).reset_index(drop=True)
            st.rerun()

else:
    st.info("Aucune activité notée pour aujourd'hui.")

st.divider()
st.page_link("streamlit_app.py", label="Retour à l'accueil", icon="🏠")