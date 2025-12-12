import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Analyse SORC", page_icon="🔍")

# ==============================================================================
# 0. SÉCURITÉ & IDENTIFICATION (STANDARDISÉ)
# ==============================================================================

if "authentifie" not in st.session_state or not st.session_state.authentifie:
    st.warning("🔒 Accès restreint. Veuillez entrer votre Code Patient sur l'accueil.")
    st.page_link("streamlit_app.py", label="Retourner à l'accueil", icon="🏠")
    st.stop()

# 1. Récupération du Code Technique
CURRENT_USER_ID = st.session_state.get("user_id", "")
if not CURRENT_USER_ID:
    CURRENT_USER_ID = st.session_state.get("patient_id", "")

if not CURRENT_USER_ID:
    st.error("Erreur d'identité. Veuillez vous reconnecter.")
    st.stop()

# 2. Récupération de l'Identifiant Lisible (PAT-001) pour sauvegarde/affichage
USER_IDENTIFIER = CURRENT_USER_ID 
try:
    from connect_db import load_data
    infos = load_data("Codes_Patients")
    if infos:
        df_infos = pd.DataFrame(infos)
        code_clean = str(CURRENT_USER_ID).strip().upper()
        match = df_infos[df_infos["Code"].astype(str).str.strip().str.upper() == code_clean]
        if not match.empty:
            col_id = "Identifiant" if "Identifiant" in df_infos.columns else "Commentaire"
            val = str(match.iloc[0][col_id]).strip()
            if val: USER_IDENTIFIER = val
except: pass

# 3. Système Anti-Fuite
if "sorc_owner" not in st.session_state or st.session_state.sorc_owner != CURRENT_USER_ID:
    if "data_sorc" in st.session_state: del st.session_state.data_sorc
    st.session_state.sorc_owner = CURRENT_USER_ID

st.title("🔍 Analyse SORC")
st.info("Analysez une situation problème : Situation, Organisme (Pensées/Émotions), Réponse, Conséquences.")

# ==============================================================================
# 1. CHARGEMENT DES DONNÉES
# ==============================================================================
COLS_SORC = [
    "Patient", "Date", "Situation", 
    "Pensées", "Émotions", "Intensité Emo", 
    "Douleur Active", "Desc Douleur", "Intensité Douleur",
    "Réponse", "Conséquences", "Type Conséquence"
]

if "data_sorc" not in st.session_state:
    df_init = pd.DataFrame(columns=COLS_SORC)
    try:
        from connect_db import load_data
        data_cloud = load_data("SORC") # Nom de l'onglet GSheet
        if data_cloud:
            df_cloud = pd.DataFrame(data_cloud)
            
            # Gestion colonne manquante (Patient)
            if "Patient" not in df_cloud.columns:
                df_cloud["Patient"] = str(USER_IDENTIFIER)
            
            # Remplissage
            for col in COLS_SORC:
                if col in df_cloud.columns:
                    df_init[col] = df_cloud[col]
            
            # Filtre Sécurité (Accepte Code ou PAT-001)
            ids_ok = [str(CURRENT_USER_ID).strip(), str(USER_IDENTIFIER).strip()]
            df_init["Patient"] = df_init["Patient"].astype(str).str.strip()
            df_init = df_init[df_init["Patient"].isin(ids_ok)]
            
            # Nettoyage numérique
            for c in ["Intensité Emo", "Intensité Douleur"]:
                if c in df_init.columns:
                    df_init[c] = pd.to_numeric(df_init[c], errors='coerce').fillna(0).astype(int)

    except: pass
    st.session_state.data_sorc = df_init

# ==============================================================================
# ONGLETS
# ==============================================================================
tab1, tab2 = st.tabs(["📝 Nouvelle Analyse", "🗂️ Historique"])

# --- ONGLET 1 : SAISIE ---
with tab1:
    st.subheader("Décortiquer une situation")
    
    with st.form("sorc_form"):
        # 1. S - SITUATION
        st.markdown("### 1. Situation (S)")
        col_d, col_l = st.columns([1, 3])
        with col_d: date_evt = st.date_input("Date", datetime.now())
        with col_l: situation = st.text_area("Que se passait-il ? (Où, quand, avec qui, quoi ?)", height=80)
        
        st.divider()
        
        # 2. O - ORGANISME
        st.markdown("### 2. Organisme (O)")
        
        # A. Douleurs (Optionnel)
        has_pain = st.checkbox("⚠️ Présence de Douleurs Chroniques ?")
        desc_douleur = ""
        int_douleur = 0
        
        if has_pain:
            with st.container(border=True):
                c_p1, c_p2 = st.columns([3, 1])
                with c_p1: desc_douleur = st.text_input("Description de la douleur / sensation physique :")
                with c_p2: int_douleur = st.slider("Intensité Douleur", 0, 10, 5)
        
        # B. Pensées & Emotions
        pensees = st.text_area("💭 Pensées : Qu'est-ce qui vous a traversé l'esprit ?")
        
        c_emo, c_int = st.columns([3, 1])
        with c_emo: emotions = st.text_input("❤️ Émotions / Sensations (ex: Peur, Colère, Boule au ventre)")
        with c_int: int_emo = st.slider("Intensité Émotion", 0, 10, 7)
        
        st.divider()
        
        # 3. R - RÉPONSE
        st.markdown("### 3. Réponse (R)")
        reponse = st.text_area("🏃‍♂️ Comportement : Qu'avez-vous fait concrètement ?", height=80, placeholder="Ex: J'ai quitté la pièce, j'ai crié, j'ai pris un médicament...")
        
        st.divider()
        
        # 4. C - CONSÉQUENCES
        st.markdown("### 4. Conséquences (C)")
        consequences = st.text_area("Le résultat immédiat ou retardé ?")
        type_consq = st.radio("Impact principal :", ["Court terme (Soulagement immédiat)", "Long terme (Problème maintenu)"], horizontal=True)
        
        # VALIDATION
        st.write("")
        submitted = st.form_submit_button("Enregistrer l'analyse SORC", type="primary")
        
        if submitted:
            # Préparation des données
            douleur_active_str = "Oui" if has_pain else "Non"
            
            new_row = {
                "Patient": USER_IDENTIFIER,
                "Date": str(date_evt),
                "Situation": situation,
                "Pensées": pensees,
                "Émotions": emotions,
                "Intensité Emo": int_emo,
                "Douleur Active": douleur_active_str,
                "Desc Douleur": desc_douleur if has_pain else "",
                "Intensité Douleur": int_douleur if has_pain else 0,
                "Réponse": reponse,
                "Conséquences": consequences,
                "Type Conséquence": type_consq
            }
            
            # Sauvegarde Locale
            st.session_state.data_sorc = pd.concat([st.session_state.data_sorc, pd.DataFrame([new_row])], ignore_index=True)
            
            # Sauvegarde Cloud
            try:
                from connect_db import save_data
                # Ordre strict des colonnes pour GSheet
                values_list = [
                    USER_IDENTIFIER, str(date_evt), situation, 
                    pensees, emotions, int_emo, 
                    douleur_active_str, desc_douleur, int_douleur,
                    reponse, consequences, type_consq
                ]
                save_data("SORC", values_list)
                st.success("✅ Analyse SORC enregistrée avec succès !")
            except Exception as e:
                st.error(f"Erreur sauvegarde Cloud : {e}")

# --- ONGLET 2 : HISTORIQUE ---
with tab2:
    st.header("🗂️ Vos Analyses")
    
    if not st.session_state.data_sorc.empty:
        df_display = st.session_state.data_sorc.copy()
        
        # Forçage affichage identifiant
        if "Patient" in df_display.columns:
            df_display["Patient"] = str(USER_IDENTIFIER)
            
        # Tri par date
        if "Date" in df_display.columns:
            df_display = df_display.sort_values(by="Date", ascending=False)

        # Affichage Tableau
        st.dataframe(
            df_display, 
            use_container_width=True, 
            hide_index=True,
            column_config={
                "Situation": st.column_config.TextColumn("Situation", width="medium"),
                "Pensées": st.column_config.TextColumn("Pensées", width="medium"),
                "Réponse": st.column_config.TextColumn("Comportement", width="medium"),
                "Intensité Emo": st.column_config.NumberColumn("Int. Emo", format="%d/10"),
                "Intensité Douleur": st.column_config.NumberColumn("Douleur", format="%d/10"),
            }
        )
        
        st.divider()
        
        # Suppression
        with st.expander("🗑️ Supprimer une analyse"):
            opts = {f"{r['Date']} - {str(r['Situation'])[:30]}...": i for i, r in df_display.iterrows()}
            choix = st.selectbox("Choisir l'entrée :", list(opts.keys()), index=None)
            
            if st.button("Supprimer définitivement") and choix:
                idx = opts[choix]
                row = df_display.loc[idx]
                
                try:
                    from connect_db import delete_data_flexible
                    delete_data_flexible("SORC", {
                        "Patient": USER_IDENTIFIER, 
                        "Date": str(row['Date']),
                        "Situation": str(row['Situation'])
                    })
                except: pass
                
                st.session_state.data_sorc = st.session_state.data_sorc.drop(idx).reset_index(drop=True)
                st.success("Supprimé !")
                st.rerun()
    else:
        st.info("Aucune analyse SORC pour le moment.")

st.divider()
st.page_link("streamlit_app.py", label="Retour à l'accueil", icon="🏠")