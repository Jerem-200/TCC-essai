import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Analyse SORC", page_icon="🔍")

# ==============================================================================
# 0. SÉCURITÉ & IDENTIFICATION
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

# 2. Récupération de l'Identifiant Lisible (PAT-001)
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
st.info(f"Dossier : {USER_IDENTIFIER}")

# D. LE VIGILE (PERMISSIONS) - NOUVEAU
CLE_PAGE = "sorc" # <--- Changez ceci selon la page (ex: "activites", "conso"...)

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

# ==============================================================================
# 1. CHARGEMENT DES DONNÉES
# ==============================================================================
# Mise à jour des colonnes pour inclure l'heure et les deux types de conséquences
COLS_SORC = [
    "Patient", "Date", "Heure", "Situation", 
    "Pensées", "Émotions", "Intensité Emo", 
    "Douleur Active", "Desc Douleur", "Intensité Douleur",
    "Réponse", "Csq Court Terme", "Csq Long Terme"
]

if "data_sorc" not in st.session_state:
    df_init = pd.DataFrame(columns=COLS_SORC)
    try:
        from connect_db import load_data
        data_cloud = load_data("SORC")
        if data_cloud:
            df_cloud = pd.DataFrame(data_cloud)
            
            if "Patient" not in df_cloud.columns:
                df_cloud["Patient"] = str(USER_IDENTIFIER)
            
            # Remplissage intelligent
            for col in COLS_SORC:
                if col in df_cloud.columns:
                    df_init[col] = df_cloud[col]
            
            # Filtre Sécurité
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
    
    # --- INTERACTIVITÉ HORS FORMULAIRE ---
    # On met la case à cocher ici pour qu'elle recharge la page immédiatement
    has_pain = st.toggle("⚠️ Cette situation inclut-elle des douleurs chroniques ?", value=False)
    
    st.divider()

    with st.form("sorc_form"):
        # 1. S - SITUATION
        st.markdown("### 1. Situation (S)")
        c_date, c_heure, c_sit = st.columns([1, 1, 3])
        with c_date: 
            date_evt = st.date_input("Date", datetime.now())
        with c_heure:
            heure_evt = st.time_input("Heure", datetime.now())
        with c_sit: 
            situation = st.text_area("Que se passait-il ? (Où, quand, avec qui ?)", height=80, help="Décrivez les faits objectivement, comme une caméra.")
        
        st.divider()
        
        # 2. O - ORGANISME
        st.markdown("### 2. Organisme (O)")
        
        # A. Douleurs (Conditionnel, géré par le toggle au-dessus)
        desc_douleur = ""
        int_douleur = 0
        
        if has_pain:
            st.info("🩸 **Focus Douleur**")
            c_p1, c_p2 = st.columns([3, 1])
            with c_p1: desc_douleur = st.text_area("Description de la douleur / sensation physique :", height=80)
            with c_p2: 
                st.write("")
                int_douleur = st.slider("Intensité Douleur (0-10)", 0, 10, 5)
        
        # B. Pensées & Emotions
        pensees = st.text_area("💭 Pensées : Qu'est-ce qui vous a traversé l'esprit ?", height=80)
        
        c_emo, c_int = st.columns([3, 1])
        with c_emo: 
            # MODIFICATION : Text Area au lieu de Input pour avoir plus de place
            emotions = st.text_area("❤️ Émotions / Sensations (ex: Peur, Colère, Boule au ventre)", height=80)
        with c_int: 
            st.write("") # Petit espace pour aligner le slider
            int_emo = st.slider("Intensité Émotion", 0, 10, 7)
        
        st.divider()
        
        # 3. R - RÉPONSE
        st.markdown("### 3. Réponse (R)")
        reponse = st.text_area("🏃‍♂️ Comportement : Qu'avez-vous fait concrètement ?", height=80, placeholder="Ex: J'ai quitté la pièce, j'ai crié, j'ai pris un médicament, j'ai ruminé...")
        
        st.divider()
        
        # 4. C - CONSÉQUENCES
        st.markdown("### 4. Conséquences (C)")
        st.caption("Analysez l'impact de votre réaction.")
        
        c_court, c_long = st.columns(2)
        with c_court:
            csq_court = st.text_area("🟢 Court Terme (Soulagement immédiat ?)", height=100, placeholder="Ex: Baisse de l'anxiété, la douleur semble diminuer...")
        with c_long:
            csq_long = st.text_area("🔴 Long Terme (Le problème persiste ?)", height=100, placeholder="Ex: Je me sens coupable, la douleur revient plus fort, je suis isolé...")
        
        # VALIDATION
        st.write("")
        submitted = st.form_submit_button("Enregistrer l'analyse SORC", type="primary")
        
        if submitted:
            # Formatage
            heure_str = str(heure_evt)[:5]
            douleur_active_str = "Oui" if has_pain else "Non"
            
            new_row = {
                "Patient": USER_IDENTIFIER,
                "Date": str(date_evt),
                "Heure": heure_str,
                "Situation": situation,
                "Pensées": pensees,
                "Émotions": emotions,
                "Intensité Emo": int_emo,
                "Douleur Active": douleur_active_str,
                "Desc Douleur": desc_douleur if has_pain else "",
                "Intensité Douleur": int_douleur if has_pain else 0,
                "Réponse": reponse,
                "Csq Court Terme": csq_court,
                "Csq Long Terme": csq_long
            }
            
            # Sauvegarde Locale
            st.session_state.data_sorc = pd.concat([st.session_state.data_sorc, pd.DataFrame([new_row])], ignore_index=True)
            
            # Sauvegarde Cloud
            try:
                from connect_db import save_data
                values_list = [
                    USER_IDENTIFIER, str(date_evt), heure_str, situation, 
                    pensees, emotions, int_emo, 
                    douleur_active_str, desc_douleur, int_douleur,
                    reponse, csq_court, csq_long
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
        
        # 1. Traduction Identifiant (TCC -> PAT)
        if "Patient" in df_display.columns:
            df_display["Patient"] = str(USER_IDENTIFIER)
            
        # 2. Sécurisation colonnes
        if "Heure" not in df_display.columns: df_display["Heure"] = ""
        if "Douleur Active" not in df_display.columns: df_display["Douleur Active"] = "Non"

        # 3. Tri global
        if "Date" in df_display.columns:
            df_display = df_display.sort_values(by=["Date", "Heure"], ascending=False)

        # --- SÉPARATION DES DONNÉES ---
        # On filtre sur la colonne "Douleur Active" (qui contient "Oui" ou "Non")
        df_sans_douleur = df_display[df_display["Douleur Active"] != "Oui"]
        df_avec_douleur = df_display[df_display["Douleur Active"] == "Oui"]

        # --- TABLEAU 1 : ANALYSES CLASSIQUES (Sans Douleur) ---
        if not df_sans_douleur.empty:
            st.subheader("🧘 Analyses Standards")
            cols_std = [
                "Date", "Heure", "Situation", 
                "Pensées", "Émotions", "Intensité Emo", 
                "Réponse", "Csg Court Terme", "Csg Long Terme"
            ]
            # On filtre pour éviter les bugs si une colonne manque
            cols_final_std = [c for c in cols_std if c in df_sans_douleur.columns]
            
            st.dataframe(
                df_sans_douleur[cols_final_std],
                use_container_width=True, 
                hide_index=True,
                column_config={
                    "Date": st.column_config.DateColumn("Date", format="DD/MM/YYYY"),
                    "Heure": st.column_config.TimeColumn("Heure", format="HH:mm"),
                    "Situation": st.column_config.TextColumn("Situation", width="medium"),
                    "Pensées": st.column_config.TextColumn("Pensées", width="medium"),
                    "Réponse": st.column_config.TextColumn("Comportement", width="medium"),
                    "Intensité Emo": st.column_config.NumberColumn("Emo", format="%d/10"),
                }
            )
            st.write("") # Espace

        # --- TABLEAU 2 : ANALYSES DOULEURS (Colonnes Spécifiques) ---
        if not df_avec_douleur.empty:
            st.subheader("🩸 Analyses avec Douleurs Chroniques")
            # Ici on ajoute les colonnes description et intensité de la douleur
            cols_pain = [
                "Date", "Heure", "Situation", 
                "Desc Douleur", "Intensité Douleur", # <-- Colonnes spécifiques
                "Pensées", "Émotions", "Intensité Emo", 
                "Réponse", "Csg Court Terme", "Csg Long Terme"
            ]
            cols_final_pain = [c for c in cols_pain if c in df_avec_douleur.columns]

            st.dataframe(
                df_avec_douleur[cols_final_pain],
                use_container_width=True, 
                hide_index=True,
                column_config={
                    "Date": st.column_config.DateColumn("Date", format="DD/MM/YYYY"),
                    "Heure": st.column_config.TimeColumn("Heure", format="HH:mm"),
                    "Situation": st.column_config.TextColumn("Situation", width="medium"),
                    "Desc Douleur": st.column_config.TextColumn("Description Douleur", width="medium"),
                    "Intensité Douleur": st.column_config.NumberColumn("Doul.", format="%d/10"),
                    "Intensité Emo": st.column_config.NumberColumn("Emo", format="%d/10"),
                }
            )

        st.divider()
        
        # --- SUPPRESSION (Commune aux deux tableaux) ---
        with st.expander("🗑️ Supprimer une analyse"):
            opts = {}
            # On parcourt le dataframe GLOBAL pour avoir toutes les options dans le menu
            for i, r in df_display.iterrows():
                h_str = f" à {r['Heure']}" if r.get('Heure') else ""
                # Petit indicateur visuel (🩸) si c'est une ligne douleur
                is_pain = "🩸 " if r.get("Douleur Active") == "Oui" else ""
                sit_str = str(r.get('Situation', '')) 
                label = f"{is_pain}{r['Date']}{h_str} | {sit_str[:40]}..."
                opts[label] = i

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
st.set_page_config(page_title="Analyse SORC", page_icon="📉")
if st.button("⬅️ Retour au tableau de bord"):
    # On dit au menu principal de rouvrir l'onglet "Échelles"
    st.session_state["target_tab"] = "🛠️ Outils & Exos"
    st.switch_page("streamlit_app.py")