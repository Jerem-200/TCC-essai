import streamlit as st
import pandas as pd
from datetime import datetime
from visualisations import afficher_who5

st.set_page_config(page_title="Échelle WHO-5", page_icon="🌿")

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
if "who5_owner" not in st.session_state or st.session_state.who5_owner != CURRENT_USER_ID:
    if "data_who5" in st.session_state: del st.session_state.data_who5
    st.session_state.who5_owner = CURRENT_USER_ID

# D. LE VIGILE (PERMISSIONS) - NOUVEAU
CLE_PAGE = "who5" # <--- Changez ceci selon la page (ex: "activites", "conso"...)

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

st.title("🌿 Indice de Bien-être (WHO-5)")
st.caption("Au cours des **2 dernières semaines**, comment vous êtes-vous senti(e) ?")

# ==============================================================================
# 1. CHARGEMENT
# ==============================================================================
COLS_WHO = ["Patient", "Date", "Q1", "Q2", "Q3", "Q4", "Q5", "Score Brut", "Score Pourcent"]

if "data_who5" not in st.session_state:
    df_init = pd.DataFrame(columns=COLS_WHO)
    try:
        from connect_db import load_data
        data_cloud = load_data("WHO5")
        if data_cloud:
            df_cloud = pd.DataFrame(data_cloud)
            if "Patient" not in df_cloud.columns: df_cloud["Patient"] = str(CURRENT_USER_ID)
            
            for col in COLS_WHO:
                if col in df_cloud.columns: df_init[col] = df_cloud[col]
            
            if "Patient" in df_init.columns:
                df_init = df_init[df_init["Patient"].astype(str) == str(CURRENT_USER_ID)]
    except: pass
    st.session_state.data_who5 = df_init

# ==============================================================================
# CONTENU
# ==============================================================================
tab1, tab2 = st.tabs(["📝 Nouveau Test", "📊 Historique"])

QUESTIONS = [
    "1. Je me suis senti(e) gai(e) et de bonne humeur",
    "2. Je me suis senti(e) calme et détendu(e)",
    "3. Je me suis senti(e) actif(ve) et énergique",
    "4. Je me suis réveillé(e) frais(che) et dispos(e)",
    "5. Ma vie quotidienne a été remplie de choses qui m'intéressent"
]

# Attention : Echelle positive (5 = Top)
OPTIONS = [
    "Tout le temps (5)", 
    "La plupart du temps (4)", 
    "Plus de la moitié du temps (3)", 
    "Moins de la moitié du temps (2)", 
    "De temps en temps (1)", 
    "À aucun moment (0)"
]

SCORES_MAP = {
    "Tout le temps (5)": 5, 
    "La plupart du temps (4)": 4, 
    "Plus de la moitié du temps (3)": 3, 
    "Moins de la moitié du temps (2)": 2, 
    "De temps en temps (1)": 1, 
    "À aucun moment (0)": 0
}

with tab1:
    with st.form("form_who5"):
        date_test = st.date_input("Date du jour", datetime.now())
        st.divider()
        
        reponses_scores = []
        for q in QUESTIONS:
            st.markdown(f"**{q}**")
            rep = st.radio(f"Rép {q}", OPTIONS, horizontal=True, label_visibility="collapsed", key=q)
            reponses_scores.append(SCORES_MAP[rep])
            st.write("")
        
        submitted = st.form_submit_button("Calculer le Bien-être", type="primary")
        
        if submitted:
            raw_score = sum(reponses_scores) # Sur 25
            percent_score = raw_score * 4    # Sur 100
            
            # Interprétation
            message = "Bien-être satisfaisant"
            if percent_score < 28: message = "Probable état dépressif"
            elif percent_score < 50: message = "Bien-être faible (Risque)"
            
            st.success(f"✅ Score : **{percent_score}%** ({raw_score}/25)")
            st.info(f"Interprétation : **{message}**")
            
            # Sauvegarde
            new_row = {
                "Patient": CURRENT_USER_ID, "Date": str(date_test),
                "Score Brut": raw_score, "Score Pourcent": percent_score
            }
            # Ajout des Q1-Q5
            for i, score in enumerate(reponses_scores):
                new_row[f"Q{i+1}"] = score
            
            st.session_state.data_who5 = pd.concat([st.session_state.data_who5, pd.DataFrame([new_row])], ignore_index=True)
            
            try:
                from connect_db import save_data
                # Ordre : Patient, Date, Q1...Q5, Score Brut, Score Pourcent
                data_save = [CURRENT_USER_ID, str(date_test)] + reponses_scores + [raw_score, percent_score]
                save_data("WHO5", data_save)
            except Exception as e:
                st.error(f"Erreur Cloud : {e}")

with tab2:
    st.header("Historique Bien-être")
    afficher_who5(st.session_state.data_who5, CURRENT_USER_ID)