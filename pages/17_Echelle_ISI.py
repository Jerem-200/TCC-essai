import streamlit as st
import pandas as pd
from datetime import datetime
from visualisations import afficher_isi

st.set_page_config(page_title="Échelle ISI", page_icon="😴")

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
if "isi_owner" not in st.session_state or st.session_state.isi_owner != CURRENT_USER_ID:
    if "data_isi" in st.session_state: del st.session_state.data_isi
    st.session_state.isi_owner = CURRENT_USER_ID

# D. LE VIGILE (PERMISSIONS) - NOUVEAU
CLE_PAGE = "isi" # <--- Changez ceci selon la page (ex: "activites", "conso"...)

if st.session_state.get("user_type") == "patient":
    try:
        from connect_db import load_data
        perms = load_data("Permissions")
        if perms:
            df_perm = pd.DataFrame(perms)
            # On cherche si le patient a des blocages
            row = df_perm[df_perm["Patient"] == CURRENT_USER_ID]
            if not row.empty:
                bloques = str(row.iloc[0]["Bloques"]).split(",")
                # Si la clé de la page est dans la liste des blocages
                if CLE_PAGE in [b.strip() for b in bloques]:
                    st.error("🔒 Cette fonctionnalité n'est pas activée dans votre programme.")
                    st.info("Voyez avec votre thérapeute si vous pensez qu'il s'agit d'une erreur.")
                    if st.button("Retour à l'accueil"):
                        st.switch_page("streamlit_app.py")
                    st.stop() # Arrêt immédiat
    except Exception as e:
        pass # En cas d'erreur technique (ex: pas de connexion), on laisse passer par défaut

st.title("😴 Index de Sévérité de l'Insomnie (ISI)")
st.caption("Veuillez estimer la sévérité actuelle (dernier mois) de vos difficultés de sommeil.")

# ==============================================================================
# 1. CHARGEMENT
# ==============================================================================
COLS_ISI = ["Patient", "Date", "Q1a", "Q1b", "Q1c", "Q2", "Q3", "Q4", "Q5", "Score Total", "Sévérité"]

if "data_isi" not in st.session_state:
    df_init = pd.DataFrame(columns=COLS_ISI)
    try:
        from connect_db import load_data
        data_cloud = load_data("ISI")
        if data_cloud:
            df_cloud = pd.DataFrame(data_cloud)
            if "Patient" not in df_cloud.columns: df_cloud["Patient"] = str(CURRENT_USER_ID)
            
            for col in COLS_ISI:
                if col in df_cloud.columns: df_init[col] = df_cloud[col]
            
            if "Patient" in df_init.columns:
                df_init = df_init[df_init["Patient"].astype(str) == str(CURRENT_USER_ID)]
    except: pass
    st.session_state.data_isi = df_init

# ==============================================================================
# CONTENU
# ==============================================================================
tab1, tab2 = st.tabs(["📝 Nouveau Test", "📊 Historique"])

# Options standards (0-4)
OPTS_STD = ["Aucune (0)", "Légère (1)", "Moyenne (2)", "Très (3)", "Extrêmement (4)"]
OPTS_SATIS = ["Très Satisfait (0)", "Satisfait (1)", "Plutôt Neutre (2)", "Insatisfait (3)", "Très Insatisfait (4)"]
OPTS_IMPACT = ["Aucunement (0)", "Légèrement (1)", "Moyennement (2)", "Très (3)", "Extrêmement (4)"]

SCORES_MAP = {
    "Aucune (0)": 0, "Légère (1)": 1, "Moyenne (2)": 2, "Très (3)": 3, "Extrêmement (4)": 4,
    "Très Satisfait (0)": 0, "Satisfait (1)": 1, "Plutôt Neutre (2)": 2, "Insatisfait (3)": 3, "Très Insatisfait (4)": 4,
    "Aucunement (0)": 0, "Légèrement (1)": 1, "Moyennement (2)": 2, "Très (3)": 3, "Extrêmement (4)": 4
}

with tab1:
    with st.form("form_isi"):
        date_test = st.date_input("Date du jour", datetime.now())
        st.divider()
        
        st.subheader("1. Difficultés de sommeil")
        q1a = st.radio("a. Difficultés à s'endormir :", OPTS_STD, horizontal=True)
        q1b = st.radio("b. Difficultés à rester endormi(e) :", OPTS_STD, horizontal=True)
        q1c = st.radio("c. Problèmes de réveils trop tôt le matin :", OPTS_STD, horizontal=True)
        
        st.divider()
        
        st.subheader("2. Satisfaction & Impact")
        q2 = st.radio("2. Jusqu'à quel point êtes-vous SATISFAIT(E) de votre sommeil actuel ?", OPTS_SATIS, horizontal=True)
        
        st.write("---")
        q3 = st.radio("3. Jusqu'à quel point considérez-vous que vos difficultés de sommeil PERTURBENT votre fonctionnement quotidien ?", OPTS_IMPACT, horizontal=True)
        
        st.write("---")
        q4 = st.radio("4. À quel point considérez-vous que vos difficultés de sommeil sont APPARENTES pour les autres ?", OPTS_IMPACT, horizontal=True)
        
        st.write("---")
        q5 = st.radio("5. Jusqu'à quel point êtes-vous INQUIET(ÈTE)/préoccupé(e) à propos de vos difficultés de sommeil ?", OPTS_IMPACT, horizontal=True)
        
        submitted = st.form_submit_button("Calculer le Score", type="primary")
        
        if submitted:
            # Calcul
            s1a = SCORES_MAP[q1a]
            s1b = SCORES_MAP[q1b]
            s1c = SCORES_MAP[q1c]
            s2 = SCORES_MAP[q2]
            s3 = SCORES_MAP[q3]
            s4 = SCORES_MAP[q4]
            s5 = SCORES_MAP[q5]
            
            total_score = s1a + s1b + s1c + s2 + s3 + s4 + s5
            
            # Interprétation (Basée sur l'image)
            severite = ""
            if total_score <= 7: severite = "Absence d'insomnie"
            elif total_score <= 14: severite = "Insomnie sub-clinique (légère)"
            elif total_score <= 21: severite = "Insomnie clinique (modérée)"
            else: severite = "Insomnie clinique (sévère)"
            
            st.success(f"✅ Score Total : **{total_score} / 28**")
            st.info(f"Interprétation : **{severite}**")
            
            # Sauvegarde
            try:
                from connect_db import save_data
                # Ordre : Patient, Date, Q1a, Q1b, Q1c, Q2, Q3, Q4, Q5, Score, Severité
                data_save = [CURRENT_USER_ID, str(date_test), s1a, s1b, s1c, s2, s3, s4, s5, total_score, severite]
                save_data("ISI", data_save)
                
                # Mise à jour locale
                new_row = {
                    "Patient": CURRENT_USER_ID, "Date": str(date_test),
                    "Q1a": s1a, "Q1b": s1b, "Q1c": s1c, "Q2": s2, "Q3": s3, "Q4": s4, "Q5": s5,
                    "Score Total": total_score, "Sévérité": severite
                }
                st.session_state.data_isi = pd.concat([st.session_state.data_isi, pd.DataFrame([new_row])], ignore_index=True)
                
            except Exception as e:
                st.error(f"Erreur Cloud : {e}")

with tab2:
    st.header("Historique ISI")
    afficher_isi(st.session_state.data_isi, CURRENT_USER_ID)