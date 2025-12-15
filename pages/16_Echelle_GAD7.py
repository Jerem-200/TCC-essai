import streamlit as st
import pandas as pd
from datetime import datetime
from visualisations import afficher_gad7

st.set_page_config(page_title="Échelle GAD-7", page_icon="😰")

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
if "gad7_owner" not in st.session_state or st.session_state.gad7_owner != CURRENT_USER_ID:
    if "data_gad7" in st.session_state: del st.session_state.data_gad7
    st.session_state.gad7_owner = CURRENT_USER_ID

# D. LE VIGILE (PERMISSIONS) - NOUVEAU
CLE_PAGE = "gad7" # <--- Changez ceci selon la page (ex: "activites", "conso"...)

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

st.title("😰 Questionnaire GAD-7")
st.caption("Au cours des **2 dernières semaines**, à quelle fréquence avez-vous été gêné(e) par les problèmes suivants ?")

# ==============================================================================
# 1. CHARGEMENT
# ==============================================================================
COLS_GAD = ["Patient", "Date", "Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7", "Score Total", "Impact", "Sévérité"]

if "data_gad7" not in st.session_state:
    df_init = pd.DataFrame(columns=COLS_GAD)
    try:
        from connect_db import load_data
        data_cloud = load_data("GAD7")
        if data_cloud:
            df_cloud = pd.DataFrame(data_cloud)
            if "Patient" not in df_cloud.columns: df_cloud["Patient"] = str(CURRENT_USER_ID)
            
            for col in COLS_GAD:
                if col in df_cloud.columns: df_init[col] = df_cloud[col]
            
            if "Patient" in df_init.columns:
                df_init = df_init[df_init["Patient"].astype(str) == str(CURRENT_USER_ID)]
    except: pass
    st.session_state.data_gad7 = df_init

# ==============================================================================
# CONTENU
# ==============================================================================
tab1, tab2 = st.tabs(["📝 Nouveau Test", "📊 Historique"])

QUESTIONS = [
    "1. Se sentir nerveux(se), anxieux(se) ou sur les nerfs",
    "2. Ne pas être capable d'arrêter de s'inquiéter ou de contrôler ses inquiétudes",
    "3. S'inquiéter trop à propos de différentes choses",
    "4. Avoir du mal à se détendre",
    "5. Être si agité(e) qu'il est difficile de tenir en place",
    "6. Devenir facilement contrarié(e) ou irritable",
    "7. Avoir peur comme si quelque chose d'horrible allait arriver"
]

OPTIONS = ["Jamais (0)", "Plusieurs jours (1)", "Plus de la moitié du temps (2)", "Presque tous les jours (3)"]
SCORES_MAP = {"Jamais (0)": 0, "Plusieurs jours (1)": 1, "Plus de la moitié du temps (2)": 2, "Presque tous les jours (3)": 3}

with tab1:
    with st.form("form_gad7"):
        date_test = st.date_input("Date du jour", datetime.now())
        st.divider()
        
        reponses_scores = []
        for q in QUESTIONS:
            st.markdown(f"**{q}**")
            rep = st.radio(f"Rép {q}", OPTIONS, horizontal=True, label_visibility="collapsed", key=q)
            reponses_scores.append(SCORES_MAP[rep])
            st.write("")
        
        st.divider()
        st.markdown("**Si vous avez coché des problèmes, à quel point ont-ils rendu votre travail ou vos tâches difficiles ?**")
        impact = st.selectbox("Impact fonctionnel :", ["Pas du tout difficile", "Assez difficile", "Très difficile", "Extrêmement difficile"])
        
        submitted = st.form_submit_button("Calculer l'Anxiété", type="primary")
        
        if submitted:
            total_score = sum(reponses_scores)
            
            # Interprétation GAD-7
            severite = "Minimale"
            if 5 <= total_score <= 9: severite = "Légère"
            elif 10 <= total_score <= 14: severite = "Modérée"
            elif total_score >= 15: severite = "Sévère"
            
            st.success(f"✅ Score Total : **{total_score} / 21**")
            st.info(f"Niveau d'anxiété : **{severite}**")
            
            # Sauvegarde
            new_row = {
                "Patient": CURRENT_USER_ID, "Date": str(date_test),
                "Score Total": total_score, "Impact": impact, "Sévérité": severite
            }
            for i, score in enumerate(reponses_scores):
                new_row[f"Q{i+1}"] = score
            
            st.session_state.data_gad7 = pd.concat([st.session_state.data_gad7, pd.DataFrame([new_row])], ignore_index=True)
            
            try:
                from connect_db import save_data
                # Ordre : Patient, Date, Q1...Q7, Score, Impact, Severité
                data_save = [CURRENT_USER_ID, str(date_test)] + reponses_scores + [total_score, impact, severite]
                save_data("GAD7", data_save)
            except Exception as e:
                st.error(f"Erreur Cloud : {e}")

with tab2:
    st.header("Suivi de l'anxiété")
    afficher_gad7(st.session_state.data_gad7, CURRENT_USER_ID)