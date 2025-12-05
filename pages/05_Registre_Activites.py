import streamlit as st
import pandas as pd
import altair as alt 
from datetime import datetime

st.set_page_config(page_title="Registre des Activités", page_icon="📝")

# --- 1. LE VIGILE DE SÉCURITÉ (Toujours en premier !) ---
if "authentifie" not in st.session_state or not st.session_state.authentifie:
    st.warning("⛔ Veuillez vous connecter sur la page d'accueil.")
    st.switch_page("streamlit_app.py")
    st.stop()

st.title("📝 Registre des Activités")

# --- 2. INITIALISATION DES MÉMOIRES (Correction du bug KeyError) ---
# On définit explicitement les colonnes pour être sûr que "Date" existe
if "data_activites" not in st.session_state:
    st.session_state.data_activites = pd.DataFrame(columns=[
        "Date", "Heure", "Activité", 
        "Plaisir (0-10)", "Maîtrise (0-10)", "Satisfaction (0-10)"
    ])

if "data_humeur_jour" not in st.session_state:
    st.session_state.data_humeur_jour = pd.DataFrame(columns=["Date", "Humeur Globale (0-10)"])

if "memoire_h" not in st.session_state:
    st.session_state.memoire_h = datetime.now().hour
if "memoire_m" not in st.session_state:
    st.session_state.memoire_m = datetime.now().minute

# --- 3. FORMULAIRE A : AJOUTER UNE ACTIVITÉ ---
st.subheader("1. Ajouter une activité")

with st.form("activity_form"):
    c_date, c_h, c_m = st.columns([2, 1, 1])
    with c_date:
        date_act = st.date_input("Date", datetime.now())
    with c_h:
        heure_h = st.number_input("Heure", min_value=0, max_value=23, value=st.session_state.memoire_h)
    with c_m:
        heure_m = st.number_input("Minute", min_value=0, max_value=59, value=st.session_state.memoire_m, step=5)

    activite_desc = st.text_input("Qu'avez-vous fait ?", placeholder="Ex: Petit déjeuner, Travail...")

    st.write("**Évaluation :**")
    c1, c2, c3 = st.columns(3)
    with c1: plaisir = st.slider("🎉 Plaisir", 0, 10, 5, help="Joie / Bien-être")
    with c2: maitrise = st.slider("💪 Maîtrise", 0, 10, 5, help="Compétence")
    with c3: satisfaction = st.slider("🏆 Satisfaction", 0, 10, 5, help="Accomplissement")

    submitted_act = st.form_submit_button("Ajouter l'activité")

    if submitted_act:
        heure_str = f"{heure_h:02d}:{heure_m:02d}"
        
        # Sauvegarde Locale
        new_row = {
            "Date": str(date_act), "Heure": heure_str, "Activité": activite_desc, 
            "Plaisir (0-10)": plaisir, "Maîtrise (0-10)": maitrise, "Satisfaction (0-10)": satisfaction
        }
        st.session_state.data_activites = pd.concat([st.session_state.data_activites, pd.DataFrame([new_row])], ignore_index=True)
        
        # Mise à jour mémoire heure
        st.session_state.memoire_h = heure_h
        st.session_state.memoire_m = heure_m
        
        # Sauvegarde Cloud
        from connect_db import save_data
        patient = st.session_state.get("patient_id", "Inconnu")
        save_data("Activites", [patient, str(date_act), heure_str, activite_desc, plaisir, maitrise, satisfaction])
        
        st.success(f"Activité ajoutée à {heure_str} !")

st.divider()

# --- 4. FORMULAIRE B : HUMEUR ---
st.subheader("2. Bilan de la journée")
with st.form("humeur_form"):
    date_humeur = st.date_input("Date du bilan", datetime.now(), key="date_bilan")
    humeur_globale = st.slider("🌈 Humeur globale du jour (0-10)", 0, 10, 5)
    
    if st.form_submit_button("Enregistrer l'humeur"):
        # Local
        new_humeur = {"Date": str(date_humeur), "Humeur Globale (0-10)": humeur_globale}
        st.session_state.data_humeur_jour = pd.concat([st.session_state.data_humeur_jour, pd.DataFrame([new_humeur])], ignore_index=True)
        
        # Cloud
        from connect_db import save_data
        patient = st.session_state.get("patient_id", "Inconnu")
        save_data("Humeur", [patient, str(date_humeur), humeur_globale])
        
        st.success("Humeur enregistrée !")

# --- 5. APERÇU DU JOUR ---
st.divider()
st.subheader(f"Résumé du {datetime.now().strftime('%d/%m/%Y')}")

# C'est ici que ça plantait : on vérifie d'abord si le dataframe est vide
if not st.session_state.data_activites.empty:
    today_str = str(datetime.now().date())
    
    # On vérifie que la colonne "Date" existe bien (Sécurité anti-bug)
    if "Date" in st.session_state.data_activites.columns:
        df_today = st.session_state.data_activites[st.session_state.data_activites["Date"] == today_str]
        
        if not df_today.empty:
            st.dataframe(df_today[["Heure", "Activité", "Plaisir (0-10)", "Maîtrise (0-10)", "Satisfaction (0-10)"]].sort_values("Heure"), use_container_width=True)
            
            # Graphique
            df_chart = df_today.copy()
            cols_score = ["Plaisir (0-10)", "Maîtrise (0-10)", "Satisfaction (0-10)"]
            for col in cols_score: df_chart[col] = pd.to_numeric(df_chart[col], errors='coerce')

            df_grouped = df_chart.groupby("Activité")[cols_score].mean().reset_index()
            df_long = df_grouped.melt(id_vars=["Activité"], value_vars=cols_score, var_name="Indicateur", value_name="Score")

            chart = alt.Chart(df_long).mark_bar().encode(
                x=alt.X('Activité:N', title=None, axis=alt.Axis(labelAngle=0)), 
                y=alt.Y('Score:Q', title='Note'),
                color='Indicateur:N', xOffset='Indicateur:N',
                tooltip=['Activité', 'Indicateur', alt.Tooltip('Score', format='.1f')]
            ).properties(height=350)
            st.altair_chart(chart, use_container_width=True)

            # Suppression
            st.divider()
            with st.expander("🗑️ Supprimer une activité"):
                options_dict = {f"{row['Heure']} - {row['Activité']} (ID:{i})": i for i, row in df_today.iterrows()}
                selected = st.selectbox("Choisir", list(options_dict.keys()))
                if st.button("Supprimer"):
                    st.session_state.data_activites = st.session_state.data_activites.drop(options_dict[selected]).reset_index(drop=True)
                    st.rerun()
        else:
            st.info("Rien pour aujourd'hui.")
    else:
        st.error("Erreur de structure de données. Veuillez rafraîchir la page (F5).")
else:
    st.info("Aucune activité enregistrée.")

st.divider()
st.page_link("streamlit_app.py", label="Retour à l'accueil", icon="🏠")