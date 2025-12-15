import streamlit as st
import pandas as pd
from datetime import datetime
from visualisations import afficher_phq9

st.set_page_config(page_title="Échelle PHQ-9", page_icon="📉")

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
if "phq9_owner" not in st.session_state or st.session_state.phq9_owner != CURRENT_USER_ID:
    if "data_phq9" in st.session_state: del st.session_state.data_phq9
    st.session_state.phq9_owner = CURRENT_USER_ID

# D. LE VIGILE (PERMISSIONS) - NOUVEAU
CLE_PAGE = "phq9" # <--- Changez ceci selon la page (ex: "activites", "conso"...)

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

st.title("📉 Questionnaire PHQ-9")
st.caption("Au cours des **2 dernières semaines**, selon quelle fréquence avez-vous été gêné(e) par les problèmes suivants ?")

# ==============================================================================
# 1. CHARGEMENT
# ==============================================================================
COLS_PHQ = ["Patient", "Date", "Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7", "Q8", "Q9", "Score Total", "Impact", "Sévérité"]

if "data_phq9" not in st.session_state:
    df_init = pd.DataFrame(columns=COLS_PHQ)
    try:
        from connect_db import load_data
        data_cloud = load_data("PHQ9")
        if data_cloud:
            df_cloud = pd.DataFrame(data_cloud)
            # Correction colonne manquante
            if "Patient" not in df_cloud.columns: df_cloud["Patient"] = str(CURRENT_USER_ID)
            
            # Mapping
            for col in COLS_PHQ:
                if col in df_cloud.columns: df_init[col] = df_cloud[col]
            
            # Filtre
            if "Patient" in df_init.columns:
                df_init = df_init[df_init["Patient"].astype(str) == str(CURRENT_USER_ID)]
    except: pass
    st.session_state.data_phq9 = df_init

# ==============================================================================
# CONTENU
# ==============================================================================
tab1, tab2 = st.tabs(["📝 Nouveau Test", "📊 Historique"])

QUESTIONS = [
    "1. Peu d'intérêt ou de plaisir à faire les choses",
    "2. Être triste, déprimé(e) ou désespéré(e)",
    "3. Difficultés à s'endormir ou à rester endormi(e), ou dormir trop",
    "4. Se sentir fatigué(e) ou manquer d'énergie",
    "5. Avoir peu d'appétit ou manger trop",
    "6. Avoir une mauvaise opinion de soi-même, ou avoir le sentiment d’être nul(le), ou d’avoir déçu sa famille ou s’être déçu(e) soi-même",
    "7. Avoir du mal à se concentrer, par exemple, pour lire le journal ou regarder la télévision",
    "8. Bouger ou parler si lentement que les autres auraient pu le remarquer.   Ou au contraire, être si agité(e) que vous avez eu du mal à tenir en place par rapport à d’habitude",
    "9. Penser qu’il vaudrait mieux mourir ou envisager de vous faire du mal d’une manière ou d’une autre"
]

OPTIONS = ["Jamais (0)", "Plusieurs jours (1)", "Plus de la moitié du temps (2)", "Presque tous les jours (3)"]
SCORES_MAP = {"Jamais (0)": 0, "Plusieurs jours (1)": 1, "Plus de la moitié du temps (2)": 2, "Presque tous les jours (3)": 3}

with tab1:
    with st.form("form_phq9"):
        date_test = st.date_input("Date du jour", datetime.now())
        st.divider()
        
        reponses_scores = []
        
        for q in QUESTIONS:
            st.markdown(f"**{q}**")
            # Horizontal pour gagner de la place
            rep = st.radio(f"Rép {q}", OPTIONS, horizontal=True, label_visibility="collapsed", key=q)
            reponses_scores.append(SCORES_MAP[rep])
            st.write("")
        
        st.divider()
        st.markdown("**Si vous avez coché des problèmes, à quel point ont-ils rendu votre travail ou vos tâches difficiles ?**")
        impact = st.selectbox("Impact fonctionnel :", ["Pas du tout difficile", "Assez difficile", "Très difficile", "Extrêmement difficile"])
        
        submitted = st.form_submit_button("Calculer et Enregistrer", type="primary")
        
        if submitted:
            total_score = sum(reponses_scores)
            
            # Interprétation
            severite = "Aucune"
            if 5 <= total_score <= 9: severite = "Légère"
            elif 10 <= total_score <= 14: severite = "Modérée"
            elif 15 <= total_score <= 19: severite = "Modérément sévère"
            elif total_score >= 20: severite = "Sévère"
            
            st.success(f"✅ Enregistré ! Score Total : **{total_score} / 27** ({severite})")
            
            # Sauvegarde
            new_row = {
                "Patient": CURRENT_USER_ID, "Date": str(date_test),
                "Score Total": total_score, "Impact": impact, "Sévérité": severite
            }
            # Ajout des Q1-Q9
            for i, score in enumerate(reponses_scores):
                new_row[f"Q{i+1}"] = score
            
            st.session_state.data_phq9 = pd.concat([st.session_state.data_phq9, pd.DataFrame([new_row])], ignore_index=True)
            
            try:
                from connect_db import save_data
                # Ordre liste pour GSheet : Patient, Date, Q1...Q9, Score, Impact, Severité
                data_save = [CURRENT_USER_ID, str(date_test)] + reponses_scores + [total_score, impact, severite]
                save_data("PHQ9", data_save)
            except Exception as e:
                st.error(f"Erreur Cloud : {e}")

with tab2:
    st.header("Suivi des scores")
    afficher_phq9(st.session_state.data_phq9, CURRENT_USER_ID)