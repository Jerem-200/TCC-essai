import streamlit as st
import pandas as pd
from datetime import datetime
from visualisations import afficher_peg

st.set_page_config(page_title="Échelle PEG", page_icon="🤕")

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
if "peg_owner" not in st.session_state or st.session_state.peg_owner != CURRENT_USER_ID:
    if "data_peg" in st.session_state: del st.session_state.data_peg
    st.session_state.peg_owner = CURRENT_USER_ID

# D. LE VIGILE (PERMISSIONS) - NOUVEAU
CLE_PAGE = "peg" # <--- Changez ceci selon la page (ex: "activites", "conso"...)

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

st.title("🤕 Échelle PEG (Douleur)")
st.caption("Évaluation de la douleur et de son interférence sur votre vie (Dernière semaine).")

# ==============================================================================
# 1. CHARGEMENT
# ==============================================================================
COLS_PEG = ["Patient", "Date", "Q1", "Q2", "Q3", "Score Moyen", "Interprétation"]

if "data_peg" not in st.session_state:
    df_init = pd.DataFrame(columns=COLS_PEG)
    try:
        from connect_db import load_data
        data_cloud = load_data("PEG")
        if data_cloud:
            df_cloud = pd.DataFrame(data_cloud)
            if "Patient" not in df_cloud.columns: df_cloud["Patient"] = str(CURRENT_USER_ID)
            
            for col in COLS_PEG:
                if col in df_cloud.columns: df_init[col] = df_cloud[col]
            
            if "Patient" in df_init.columns:
                df_init = df_init[df_init["Patient"].astype(str) == str(CURRENT_USER_ID)]
    except: pass
    st.session_state.data_peg = df_init

# ==============================================================================
# CONTENU
# ==============================================================================
tab1, tab2 = st.tabs(["📝 Nouveau Test", "📊 Historique"])

with tab1:
    with st.form("form_peg"):
        date_test = st.date_input("Date du jour", datetime.now())
        st.divider()
        
        st.write("Veuillez noter de **0 (Nul)** à **10 (Extrême)** :")
        
        st.markdown("**1. Quelle a été l'intensité moyenne de votre douleur au cours de la semaine dernière ?**")
        q1 = st.slider("Douleur moyenne", 0, 10, 5, key="q1")
        st.caption("0 = Aucune douleur | 10 = Douleur aussi forte que l'on puisse imaginer")
        
        st.markdown("**2. À quel point la douleur a-t-elle gêné votre plaisir de vivre au cours de la semaine dernière ?**")
        q2 = st.slider("Interférence Plaisir", 0, 10, 5, key="q2")
        st.caption("0 = Ne gêne pas du tout | 10 = Gêne complètement")

        st.markdown("**3. À quel point la douleur a-t-elle gêné vos activités générales au cours de la semaine dernière ?**")
        q3 = st.slider("Interférence Activité", 0, 10, 5, key="q3")
        st.caption("0 = Ne gêne pas du tout | 10 = Gêne complètement")
        
        submitted = st.form_submit_button("Calculer et Enregistrer", type="primary")
        
        if submitted:
            # Calcul : Moyenne des 3 items
            moyenne = (q1 + q2 + q3) / 3
            moyenne_arrondie = round(moyenne, 1)
            
            # Interprétation simple (suivi d'intensité)
            interpretation = f"Impact moyen : {moyenne_arrondie}/10"
            
            st.success(f"✅ Score PEG : **{moyenne_arrondie} / 10**")
            
            # Sauvegarde
            new_row = {
                "Patient": CURRENT_USER_ID, "Date": str(date_test),
                "Q1": q1, "Q2": q2, "Q3": q3,
                "Score Moyen": moyenne_arrondie, "Interprétation": interpretation
            }
            
            st.session_state.data_peg = pd.concat([st.session_state.data_peg, pd.DataFrame([new_row])], ignore_index=True)
            
            try:
                from connect_db import save_data
                # Ordre : Patient, Date, Q1, Q2, Q3, Score, Interprétation
                data_save = [CURRENT_USER_ID, str(date_test), q1, q2, q3, moyenne_arrondie, interpretation]
                save_data("PEG", data_save)
            except Exception as e:
                st.error(f"Erreur Cloud : {e}")

with tab2:
    st.header("Suivi de la douleur")
    afficher_peg(st.session_state.data_peg, CURRENT_USER_ID)