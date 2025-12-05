import streamlit as st
import pandas as pd
import altair as alt 
from datetime import datetime, time

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

# --- NOUVEAU : On initialise la mémoire de l'heure ---
# Si c'est la première fois qu'on ouvre, on met l'heure actuelle.
# Sinon, on garde celle qui est déjà en mémoire.
if "memoire_heure" not in st.session_state:
    st.session_state.memoire_heure = datetime.now().time()

# --- 2. FORMULAIRE A : AJOUTER UNE ACTIVITÉ ---
st.subheader("1. Ajouter une activité")

with st.form("activity_form"):
    col_date, col_heure = st.columns([1, 1])
    with col_date:
        date_act = st.date_input("Date", datetime.now())
    with col_heure:
        # L'heure par défaut est celle stockée en mémoire
        heure_act = st.time_input("Heure de début", value=st.session_state.memoire_heure, step=900)

    activite_desc = st.text_input("Qu'avez-vous fait ?", placeholder="Ex: Marcher en travaillant...")

    st.write("**Évaluation de l'activité :**")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        plaisir = st.slider("🎉 Plaisir (0-10)", 0, 10, 5, help="Joie / Bien-être")
    with c2:
        maitrise = st.slider("💪 Maîtrise (0-10)", 0, 10, 5, help="Sentiment de compétence")
    with c3:
        satisfaction = st.slider("🏆 Satisfaction (0-10)", 0, 10, 5, help="Accomplissement / But")

    submitted_act = st.form_submit_button("Ajouter l'activité")

    if submitted_act:
        heure_str = heure_act.strftime("%H:%M")
        
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
        # On sauvegarde l'heure qu'on vient d'utiliser pour la prochaine fois
        st.session_state.memoire_heure = heure_act
        
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

# --- 4. APERÇU DU JOUR ---
st.divider()
st.subheader(f"Résumé du {datetime.now().strftime('%d/%m/%Y')}")

today_str = str(datetime.now().date())
df_today = st.session_state.data_activites[st.session_state.data_activites["Date"] == today_str]

if not df_today.empty:
    # On trie par heure pour l'affichage
    df_today = df_today.sort_values(by="Heure")
    
    st.dataframe(df_today[["Heure", "Activité", "Plaisir (0-10)", "Maîtrise (0-10)", "Satisfaction (0-10)"]], use_container_width=True)
    
    st.write("**Visualisation des activités du jour :**")
    
    # --- PRÉPARATION POUR LE GRAPHIQUE (MOYENNE) ---
    # Si deux activités ont le même nom (ex: 2x "Marche"), on fait la moyenne pour l'affichage barres
    df_chart = df_today.copy()
    cols_score = ["Plaisir (0-10)", "Maîtrise (0-10)", "Satisfaction (0-10)"]
    for col in cols_score:
        df_chart[col] = pd.to_numeric(df_chart[col], errors='coerce')

    # On groupe par Activité pour avoir la moyenne si doublons
    df_chart_grouped = df_chart.groupby("Activité")[cols_score].mean().reset_index()

    df_long = df_chart_grouped.melt(
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

else:
    st.info("Aucune activité notée pour aujourd'hui.")

st.divider()
st.page_link("streamlit_app.py", label="Retour à l'accueil", icon="🏠")