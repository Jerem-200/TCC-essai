import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, timedelta
from visualisations import afficher_compulsions

st.set_page_config(page_title="Agenda des Compulsions", page_icon="🛑")

# ==============================================================================
# 0. SÉCURITÉ & IDENTIFICATION
# ==============================================================================

if "authentifie" not in st.session_state or not st.session_state.authentifie:
    st.warning("🔒 Accès restreint. Veuillez entrer votre Code Patient sur l'accueil.")
    st.page_link("streamlit_app.py", label="Retourner à l'accueil", icon="🏠")
    st.stop()

# 1. Récupération simple de l'ID (Standardisé)
# Grâce à votre modification dans l'accueil, ceci contient DÉJÀ "PAT-001"
CURRENT_USER_ID = st.session_state.get("user_id", "")

if not CURRENT_USER_ID:
    st.error("Session expirée. Veuillez vous reconnecter.")
    st.stop()

# 2. Anti-Fuite
if "compulsion_owner" not in st.session_state or st.session_state.compulsion_owner != CURRENT_USER_ID:
    if "data_compulsions" in st.session_state: del st.session_state.data_compulsions
    st.session_state.compulsion_owner = CURRENT_USER_ID

# D. LE VIGILE (PERMISSIONS) - NOUVEAU
CLE_PAGE = "compulsions" # <--- Changez ceci selon la page (ex: "activites", "conso"...)

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

st.title("🛑 Agenda des Compulsions")
st.info(f"Suivi des rituels et compulsions pour le dossier : {CURRENT_USER_ID}")

# ==============================================================================
# 1. CHARGEMENT DES DONNÉES
# ==============================================================================
COLS_COMP = ["Patient", "Date", "Heure", "Nature", "Répétitions", "Durée (min)"]

if "data_compulsions" not in st.session_state:
    df_init = pd.DataFrame(columns=COLS_COMP)
    try:
        from connect_db import load_data
        data_cloud = load_data("Compulsions")
        if data_cloud:
            df_cloud = pd.DataFrame(data_cloud)
            
            # Correction si colonne manquante
            if "Patient" not in df_cloud.columns:
                df_cloud["Patient"] = str(CURRENT_USER_ID)
            
            # Remplissage
            for col in COLS_COMP:
                if col in df_cloud.columns:
                    df_init[col] = df_cloud[col]
            
            # FILTRE SÉCURITÉ SIMPLIFIÉ
            if "Patient" in df_init.columns:
                df_init = df_init[df_init["Patient"].astype(str) == str(CURRENT_USER_ID)]
            else:
                df_init = pd.DataFrame(columns=COLS_COMP)
            
            # Nettoyage numérique
            for c in ["Répétitions", "Durée (min)"]:
                if c in df_init.columns:
                    df_init[c] = pd.to_numeric(df_init[c], errors='coerce').fillna(0).astype(int)

    except: pass
    st.session_state.data_compulsions = df_init

# ==============================================================================
# ONGLETS
# ==============================================================================
tab1, tab2 = st.tabs(["📝 Saisie", "📊 Analyse & Historique"])

# --- ONGLET 1 : SAISIE ---
with tab1:
    st.subheader("Noter un épisode")
    
    with st.form("form_compulsion"):
        c_date, c_heure = st.columns(2)
        with c_date: 
            date_evt = st.date_input("Date", datetime.now())
        with c_heure:
            heure_evt = st.time_input("Heure", datetime.now())
            
        nature = st.text_input("Nature de la compulsion", placeholder="Ex: Lavage des mains, Vérification porte...")
        
        c_rep, c_dur = st.columns(2)
        with c_rep:
            repetitions = st.number_input("Nombre de répétitions", min_value=1, value=1, step=1)
        with c_dur:
            duree = st.number_input("Temps total (minutes)", min_value=0, value=5, step=5)
            
        st.write("")
        submitted = st.form_submit_button("Enregistrer", type="primary")
        
        if submitted:
            heure_str = str(heure_evt)[:5]
            
            new_row = {
                "Patient": CURRENT_USER_ID, # Utilisation directe
                "Date": str(date_evt),
                "Heure": heure_str,
                "Nature": nature,
                "Répétitions": repetitions,
                "Durée (min)": duree
            }
            
            st.session_state.data_compulsions = pd.concat([st.session_state.data_compulsions, pd.DataFrame([new_row])], ignore_index=True)
            
            try:
                from connect_db import save_data
                save_data("Compulsions", [
                    CURRENT_USER_ID, str(date_evt), heure_str, 
                    nature, repetitions, duree
                ])
                st.success("✅ Enregistré !")
            except Exception as e:
                st.error(f"Erreur Cloud : {e}")

    st.divider()
    with st.expander("🗑️ Annuler une saisie récente"):
        df_act = st.session_state.data_compulsions
        if not df_act.empty:
            df_act_s = df_act.sort_values(by=["Date", "Heure"], ascending=False)
            opts = {f"{r['Date']} {r['Heure']} - {r['Nature']}": i for i, r in df_act_s.iterrows()}
            choix = st.selectbox("Choisir :", list(opts.keys()), key="del_quick")
            
            if st.button("Supprimer", key="btn_del_quick") and choix:
                idx = opts[choix]
                row = df_act_s.loc[idx]
                try:
                    from connect_db import delete_data_flexible
                    delete_data_flexible("Compulsions", {
                        "Patient": CURRENT_USER_ID, 
                        "Date": str(row['Date']),
                        "Nature": str(row['Nature'])
                    })
                except: pass
                st.session_state.data_compulsions = df_act.drop(idx).reset_index(drop=True)
                st.success("Supprimé !")
                st.rerun()

# --- ONGLET 2 : ANALYSE ---
with tab2:
    st.header("📊 Tableau de bord")
    
    # APPEL UNIQUE À LA FONCTION CENTRALISÉE
    afficher_compulsions(st.session_state.data_compulsions, CURRENT_USER_ID)

    # 4. Suppression Historique
    st.divider()
    with st.expander("🗑️ Supprimer une entrée ancienne"):
        df_display = st.session_state.data_compulsions
        if not df_display.empty:
            opts = {}
            for i, r in df_display.sort_values(by=["Date", "Heure"], ascending=False).iterrows():
                opts[f"{r['Date']} {r['Heure']} | {r['Nature']}"] = i
            
            choix = st.selectbox("Choisir :", list(opts.keys()), index=None, key="del_hist")
            if st.button("Confirmer", key="btn_del_hist") and choix:
                idx = opts[choix]
                row = df_display.loc[idx]
                try:
                    from connect_db import delete_data_flexible
                    delete_data_flexible("Compulsions", {
                        "Patient": CURRENT_USER_ID, 
                        "Date": str(row['Date']),
                        "Nature": str(row['Nature'])
                    })
                except: pass
                st.session_state.data_compulsions = st.session_state.data_compulsions.drop(idx).reset_index(drop=True)
                st.success("Supprimé !")
                st.rerun()
        else:
            st.info("Historique vide.")

st.divider()
st.page_link("streamlit_app.py", label="Retour à l'accueil", icon="🏠")