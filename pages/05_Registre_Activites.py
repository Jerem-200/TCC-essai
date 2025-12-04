import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Registre des Activités", page_icon="📝")

st.title("📝 Registre des Activités")

# --- 1. TEXTE EXPLICATIF (Votre demande) ---
with st.expander("ℹ️ Comprendre l'objectif de cet outil (Cliquez pour lire)", expanded=True):
    st.markdown("""
    Le registre des activités est un outil d’auto-observation pour enregistrer en détail les activités de la journée et les émotions associées. 
    
    **Il permet :**
    1. D'évaluer le niveau d’activité actuel.
    2. De repérer les comportements qui maintiennent le mal-être.
    3. D'identifier les activités déjà sources de plaisir ou de satisfaction.

    Cette évaluation de base servira de référence pour comparer les progrès futurs et visualiser les effets des techniques thérapeutiques mises en place au fil des séances.
    
    **Consigne :**
    Il est important de relever heure par heure, et en temps réel, les activités réalisées dès le lever jusqu’au coucher.
    Pour chaque activité, évaluez vos sentiments sur une échelle de 0 à 10.
    
    *Par exemple, "écouter de la musique" peut vous donner Plaisir = 7, Maîtrise = 10 et Satisfaction = 6.*
    """)

# --- 2. INITIALISATION DE LA MÉMOIRE ---
if "data_activites" not in st.session_state:
    st.session_state.data_activites = pd.DataFrame(columns=[
        "Date", "Heure", "Activité", "Plaisir (0-10)", 
        "Maîtrise (0-10)", "Satisfaction (0-10)", "Humeur Globale (0-10)"
    ])

# --- 3. LE FORMULAIRE DE SAISIE ---
st.subheader("Nouvelle entrée")

with st.form("activity_form"):
    col_date, col_heure = st.columns([1, 1])
    with col_date:
        date_act = st.date_input("Date", datetime.now())
    with col_heure:
        # Création des créneaux horaires de 6h à minuit
        creneaux = [f"{h}h - {h+1}h" for h in range(6, 24)] + ["00h - 01h", "Autre"]
        heure_act = st.selectbox("Créneau horaire", creneaux)

    activite_desc = st.text_input("Description de l'activité", placeholder="Ex: Préparer le petit déjeuner, Marcher, Lire...")

    st.markdown("---")
    st.write("**Évaluation de l'expérience :**")

    # Plaisir
    plaisir = st.slider(
        "🎉 Sentiment de Plaisir (0-10)", 0, 10, 5,
        help="Le sentiment de plaisir fait référence à la joie et/ou au bien-être que procure l'activité."
    )
    
    # Maîtrise
    maitrise = st.slider(
        "💪 Sentiment de Maîtrise (0-10)", 0, 10, 5,
        help="Le sentiment de maîtrise désigne le sentiment de compétence que vous pensez avoir dans la réalisation de l’activité (était-ce facile ou difficile pour vous ?)."
    )

    # Satisfaction
    satisfaction = st.slider(
        "🏆 Sentiment de Satisfaction (0-10)", 0, 10, 5,
        help="Le sentiment de satisfaction est lié à l’accomplissement d’une tâche importante et dont la réalisation vous permet de vous rapprocher d’un but que vous vous êtes fixé."
    )

    st.markdown("---")
    humeur = st.slider("🌈 Humeur globale sur la journée (0-10)", 0, 10, 5, help="Comment vous sentez-vous globalement aujourd'hui ?")

    submitted = st.form_submit_button("Ajouter au registre")

    if submitted:
        new_row = {
            "Date": str(date_act),
            "Heure": heure_act,
            "Activité": activite_desc,
            "Plaisir (0-10)": plaisir,
            "Maîtrise (0-10)": maitrise,
            "Satisfaction (0-10)": satisfaction,
            "Humeur Globale (0-10)": humeur
        }
        
        st.session_state.data_activites = pd.concat(
            [st.session_state.data_activites, pd.DataFrame([new_row])],
            ignore_index=True
        )
        st.success("Activité enregistrée ! ✔️")

# --- 4. APERÇU RAPIDE DU JOUR ---
st.divider()
st.subheader("Vos activités du jour")
# On filtre pour ne montrer que ce qui a été saisi aujourd'hui
today_str = str(datetime.now().date())
df_today = st.session_state.data_activites[st.session_state.data_activites["Date"] == today_str]

if not df_today.empty:
    st.dataframe(df_today[["Heure", "Activité", "Plaisir (0-10)", "Maîtrise (0-10)", "Satisfaction (0-10)"]], use_container_width=True)
else:
    st.info("Aucune activité enregistrée pour aujourd'hui.")

st.divider()
st.page_link("streamlit_app.py", label="Retour à l'accueil", icon="🏠")