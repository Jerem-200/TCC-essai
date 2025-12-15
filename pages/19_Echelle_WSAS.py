import streamlit as st
import pandas as pd
from datetime import datetime
from visualisations import afficher_wsas

st.set_page_config(page_title="Échelle WSAS", page_icon="🧩")

# ==============================================================================
# 0. SÉCURITÉ
# ==============================================================================
if "authentifie" not in st.session_state or not st.session_state.authentifie:
    st.warning("🔒 Accès restreint.")
    st.stop()

CURRENT_USER_ID = st.session_state.get("user_id", "")
if not CURRENT_USER_ID:
    st.error("Session expirée.")
    st.stop()

# Anti-Fuite
if "wsas_owner" not in st.session_state or st.session_state.wsas_owner != CURRENT_USER_ID:
    if "data_wsas" in st.session_state: del st.session_state.data_wsas
    st.session_state.wsas_owner = CURRENT_USER_ID

st.title("🧩 Échelle WSAS")
st.caption("Évaluation du retentissement de votre problème sur votre fonctionnement social et professionnel.")

# ==============================================================================
# 1. CHARGEMENT
# ==============================================================================
COLS_WSAS = ["Patient", "Date", "Q1", "Q2", "Q3", "Q4", "Q5", "Score Total", "Sévérité"]

if "data_wsas" not in st.session_state:
    df_init = pd.DataFrame(columns=COLS_WSAS)
    try:
        from connect_db import load_data
        data_cloud = load_data("WSAS")
        if data_cloud:
            df_cloud = pd.DataFrame(data_cloud)
            if "Patient" not in df_cloud.columns: df_cloud["Patient"] = str(CURRENT_USER_ID)
            
            for col in COLS_WSAS:
                if col in df_cloud.columns: df_init[col] = df_cloud[col]
            
            if "Patient" in df_init.columns:
                df_init = df_init[df_init["Patient"].astype(str) == str(CURRENT_USER_ID)]
    except: pass
    st.session_state.data_wsas = df_init

# ==============================================================================
# CONTENU
# ==============================================================================
tab1, tab2 = st.tabs(["📝 Nouveau Test", "📊 Historique"])

with tab1:
    with st.form("form_wsas"):
        date_test = st.date_input("Date du jour", datetime.now())
        st.write("Veuillez indiquer à quel point votre problème affecte votre capacité à effectuer les activités suivantes (0 = Pas du tout, 8 = Très sévèrement).")
        st.divider()
        
        st.markdown("**1. TRAVAIL** (si vous ne travaillez pas pour des raisons liées au trouble, cochez 8. Si c'est pour d'autres raisons, cochez 0).")
        q1 = st.slider("Capacité à travailler / Étudier", 0, 8, 0, key="w_q1")
        
        st.markdown("**2. GESTION DU DOMICILE** (ménage, courses, cuisine, entretien...)")
        q2 = st.slider("Gestion domestique", 0, 8, 0, key="w_q2")

        st.markdown("**3. LOISIRS SOCIAUX** (avec d'autres personnes : sorties, restaurants, visites...)")
        q3 = st.slider("Activités sociales", 0, 8, 0, key="w_q3")

        st.markdown("**4. LOISIRS PRIVÉS** (seul : lecture, jardinage, collection, marche...)")
        q4 = st.slider("Activités individuelles", 0, 8, 0, key="w_q4")

        st.markdown("**5. FAMILLE ET RELATIONS** (capacité à nouer et maintenir des relations proches)")
        q5 = st.slider("Relations proches", 0, 8, 0, key="w_q5")
        
        submitted = st.form_submit_button("Calculer le Score", type="primary")
        
        if submitted:
            total_score = q1 + q2 + q3 + q4 + q5
            
            # Interprétation
            severite = ""
            if total_score < 10: severite = "Impact faible (Sub-clinique)"
            elif total_score <= 20: severite = "Impact significatif"
            else: severite = "Impact sévère"
            
            st.success(f"✅ Score Total : **{total_score} / 40**")
            st.info(f"Niveau de handicap : **{severite}**")
            
            # Sauvegarde
            try:
                from connect_db import save_data
                # Ordre : Patient, Date, Q1...Q5, Score, Severité
                data_save = [CURRENT_USER_ID, str(date_test), q1, q2, q3, q4, q5, total_score, severite]
                save_data("WSAS", data_save)
                
                # Mise à jour locale
                new_row = {
                    "Patient": CURRENT_USER_ID, "Date": str(date_test),
                    "Q1": q1, "Q2": q2, "Q3": q3, "Q4": q4, "Q5": q5,
                    "Score Total": total_score, "Sévérité": severite
                }
                st.session_state.data_wsas = pd.concat([st.session_state.data_wsas, pd.DataFrame([new_row])], ignore_index=True)
                
            except Exception as e:
                st.error(f"Erreur Cloud : {e}")

with tab2:
    st.header("Suivi fonctionnel")
    afficher_wsas(st.session_state.data_wsas, CURRENT_USER_ID)