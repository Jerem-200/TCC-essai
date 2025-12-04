import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Registre des Activités", page_icon="📝")

st.title("📝 Registre des Activités")

# --- 1. TEXTE EXPLICATIF ---
with st.expander("ℹ️ Comprendre l'objectif de cet outil (Cliquez pour lire)", expanded=False):
    st.markdown("""
    Le registre des activités est un outil d’auto-observation pour enregistrer en détail les activités de la journée et les émotions associées. 
    
    **Il permet :**
    1. D'évaluer le niveau d’activité actuel.
    2. De repérer les comportements qui maintiennent le mal-être.
    3. D'identifier les activités déjà sources de plaisir ou de satisfaction.
    
    **Consigne :**
    Relevez heure par heure les activités réalisées. Pour chaque activité, évaluez vos sentiments sur une échelle de 0 à 10.
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
        # Création des créneaux horaires
        creneaux = [f"{h}h - {h+1}h" for h in range(6, 24)] + ["00h - 01h", "Autre"]
        heure_act = st.selectbox("Créneau horaire", creneaux)

    activite_desc = st.text_input("Description de l'activité", placeholder="Ex: Préparer le petit déjeuner, Marcher, Lire...")

    st.markdown("---")
    st.write("**Évaluation de l'activité :**")

    # Plaisir
    plaisir = st.slider(
        "🎉 Sentiment de Plaisir (0-10)", 0, 10, 5,
        help="Joie et/ou bien-être que procure l'activité."
    )
    
    # Maîtrise
    maitrise = st.slider(
        "💪 Sentiment de Maîtrise (0-10)", 0, 10, 5,
        help="Sentiment de compétence dans la réalisation de l’activité (facile/difficile)."
    )

    # Satisfaction
    satisfaction = st.slider(
        "🏆 Sentiment de Satisfaction (0-10)", 0, 10, 5,
        help="Accomplissement d’une tâche importante ou rapprochement d'un but."
    )

    st.markdown("---")
    
    # --- MODIFICATION ICI : OPTION FIN DE JOURNÉE ---
    st.write("**Bilan de la journée :**")
    fin_journee = st.checkbox("C'est la dernière activité de la journée (noter l'humeur globale)")
    
    humeur = None # Par défaut, pas de note
    if fin_journee:
        humeur = st.slider("🌈 Humeur globale sur la journée (0-10)", 0, 10, 5, help="Comment vous êtes-vous senti globalement aujourd'hui ?")

    submitted = st.form_submit_button("Ajouter au registre")

    if submitted:
        # On prépare la valeur de l'humeur pour la sauvegarde
        humeur_save = humeur if fin_journee else None

        new_row = {
            "Date": str(date_act),
            "Heure": heure_act,
            "Activité": activite_desc,
            "Plaisir (0-10)": plaisir,
            "Maîtrise (0-10)": maitrise,
            "Satisfaction (0-10)": satisfaction,
            "Humeur Globale (0-10)": humeur_save
        }
        
        st.session_state.data_activites = pd.concat(
            [st.session_state.data_activites, pd.DataFrame([new_row])],
            ignore_index=True
        )
        st.success("Activité enregistrée ! ✔️")

# --- 4. APERÇU RAPIDE DU JOUR ---
st.divider()
st.subheader("Vos activités du jour")
today_str = str(datetime.now().date())
df_today = st.session_state.data_activites[st.session_state.data_activites["Date"] == today_str]

if not df_today.empty:
    # On affiche un tableau propre
    st.dataframe(df_today[["Heure", "Activité", "Plaisir (0-10)", "Maîtrise (0-10)", "Satisfaction (0-10)", "Humeur Globale (0-10)"]], use_container_width=True)
else:
    st.info("Aucune activité enregistrée pour aujourd'hui.")

st.divider()
st.page_link("streamlit_app.py", label="Retour à l'accueil", icon="🏠")