import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Colonnes de Beck", page_icon="🧩")

# ==============================================================================
# 0. SÉCURITÉ & RÉCUPÉRATION IDENTITÉ
# ==============================================================================

# 1. Vérification de l'authentification
if "authentifie" not in st.session_state or not st.session_state.authentifie:
    st.warning("🔒 Accès restreint. Veuillez entrer votre Code Patient sur l'accueil.")
    st.page_link("streamlit_app.py", label="Retourner à l'accueil", icon="🏠")
    st.stop()

# 2. Récupération simple de l'ID
# Grâce à votre modification dans l'accueil, ceci contient DÉJÀ "PAT-001"
CURRENT_USER_ID = st.session_state.get("user_id", "")

if not CURRENT_USER_ID:
    st.error("Session expirée. Veuillez vous reconnecter.")
    st.stop()

# 3. VERROUILLAGE DES DONNÉES (Système Anti-Fuite)
if "beck_owner" not in st.session_state or st.session_state.beck_owner != CURRENT_USER_ID:
    if "data_beck" in st.session_state:
        del st.session_state.data_beck
    st.session_state.beck_owner = CURRENT_USER_ID

# D. LE VIGILE (PERMISSIONS) - NOUVEAU
CLE_PAGE = "beck" # <--- Changez ceci selon la page (ex: "activites", "conso"...)

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

st.title("🧩 Colonnes de Beck")
st.caption("Identifiez et restructurez vos pensées automatiques.")

# ==============================================================================
# 1. INITIALISATION & CHARGEMENT DES DONNÉES CLOUD
# ==============================================================================

# Définition des colonnes
COLS_BECK = [
    "Patient", "Date", "Situation", "Émotion", "Intensité (Avant)", 
    "Pensée Auto", "Croyance (Avant)", "Pensée Rationnelle", 
    "Croyance (Rationnelle)", "Intensité (Après)", "Croyance (Après)"
]

if "data_beck" not in st.session_state:
    # Création du DataFrame vide
    df_init = pd.DataFrame(columns=COLS_BECK)
    
    # Tentative de chargement depuis le Cloud
    try:
        from connect_db import load_data
        data_cloud = load_data("Beck") # Nom de l'onglet GSheet
        
        if data_cloud:
            df_cloud = pd.DataFrame(data_cloud)
            
            # Mapping intelligent des colonnes (Gestion des majuscules/minuscules)
            for col in COLS_BECK:
                if col in df_cloud.columns:
                    df_init[col] = df_cloud[col]
                elif col.lower() in df_cloud.columns: # Si écrit en minuscule dans le sheet
                    df_init[col] = df_cloud[col.lower()]
            
            # Nettoyage des chiffres (Conversion texte -> nombre pour les sliders)
            numeric_cols = ["Intensité (Avant)", "Croyance (Avant)", "Croyance (Rationnelle)", "Intensité (Après)", "Croyance (Après)"]
            for c in numeric_cols:
                if c in df_init.columns:
                    df_init[c] = pd.to_numeric(df_init[c], errors='coerce').fillna(0).astype(int)

            # =================================================================
            # 🛑 AJOUTEZ CE FILTRE ICI
            # =================================================================
            if "Patient" in df_init.columns:
                # On ne garde que les lignes du patient connecté
                df_init = df_init[df_init["Patient"].astype(str) == str(CURRENT_USER_ID)]
            else:
                df_init = pd.DataFrame(columns=COLS_BECK)

    except Exception as e:
        # En cas d'erreur (pas de connexion, etc.), on reste sur un tableau vide
        pass

    st.session_state.data_beck = df_init

# ==============================================================================
# CRÉATION DES ONGLETS
# ==============================================================================
tab1, tab2 = st.tabs(["📝 Nouvel Exercice", "🗂️ Historique & Modifications"])

# ==============================================================================
# ONGLET 1 : LE FORMULAIRE DE SAISIE
# ==============================================================================
with tab1:
    st.subheader("Nouvelle entrée")
    
    with st.form("beck_form"):
        # --- SITUATION ---
        col1, col2 = st.columns(2)
        with col1:
            date_event = st.date_input("Date", datetime.now())
        with col2:
            lieu = st.text_input("Lieu / Contexte")
        
        help_situation = "Contexte factuel (horaire, lieu, personnes...).\nEx : Entretien d'embauche non concluant."
        situation = st.text_area("Situation (Fait déclencheur)", help=help_situation)
        
        st.divider()
        
        # --- EMOTION ---
        help_emotion = "Nommez l'émotion et son intensité (0-10)."
        emotion = st.text_input("Émotion", help=help_emotion)
        intensite_avant = st.slider("Intensité de l'émotion (0-10)", 0, 10, 7)
        
        st.divider()
        
        # --- PENSÉE AUTOMATIQUE ---
        help_pensee = "La petite voix qui commente.\nEx: 'Je n'arrive jamais à rien'."
        pensee_auto = st.text_area("Pensée Automatique", help=help_pensee)
        croyance_auto = st.slider("Croyance en cette pensée (0-10)", 0, 10, 8)
        
        st.divider()
        
        # --- PENSÉE RATIONNELLE ---
        help_rationnel = "Arguments contraires, vision d'un ami...\nEx : 'J'ai déjà réussi des choses'."
        pensee_rat = st.text_area("Pensée Alternative / Rationnelle", help=help_rationnel)
        croyance_rat = st.slider("Croyance rationnelle (0-10)", 0, 10, 5)
        
        st.divider()
        
        # --- RÉSULTATS ---
        st.subheader("5. Ré-évaluation")
        croyance_apres = st.slider("Nouveau degré de croyance pensée auto (0-10)", 0, 10, 4)
        intensite_apres = st.slider("Nouvelle intensité de l'émotion (0-10)", 0, 10, 4)
        
        submitted = st.form_submit_button("Enregistrer l'exercice")

        if submitted:
            # Création de la ligne de données
            new_row_dict = {
                "Patient": CURRENT_USER_ID,
                "Date": str(date_event),
                "Situation": f"{lieu} - {situation}",
                "Émotion": emotion,
                "Intensité (Avant)": intensite_avant,
                "Pensée Auto": pensee_auto,
                "Croyance (Avant)": croyance_auto,
                "Pensée Rationnelle": pensee_rat,
                "Croyance (Rationnelle)": croyance_rat,
                "Intensité (Après)": intensite_apres,
                "Croyance (Après)": croyance_apres
            }
            
            # 1. Sauvegarde Locale
            st.session_state.data_beck = pd.concat([st.session_state.data_beck, pd.DataFrame([new_row_dict])], ignore_index=True)
            
            # 2. Sauvegarde Cloud
            try:
                from connect_db import save_data
                # Conversion dict -> list pour GSheet (Respecter l'ordre de COLS_BECK)
                values_list = [new_row_dict[col] for col in COLS_BECK]
                save_data("Beck", values_list)
                st.success("✅ Enregistré avec succès !")
            except Exception as e:
                st.warning(f"⚠️ Enregistré en local uniquement ({e}).")

# ==============================================================================
# ONGLET 2 : HISTORIQUE
# ==============================================================================
with tab2:
    st.header("🗂️ Historique")
    
    df_history = st.session_state.data_beck
    
    # Filtre de sécurité
    if "Patient" in df_history.columns:
        df_history = df_history[df_history["Patient"] == CURRENT_USER_ID]
    
    if not df_history.empty:

        # A. TABLEAU
        st.dataframe(
            df_history.sort_values(by="Date", ascending=False), 
            use_container_width=True,
            column_config={
                "Patient": st.column_config.TextColumn("Dossier", width="small"), # On renomme l'entête
                "Date": st.column_config.DateColumn("Date", format="DD/MM/YYYY"),
                "Situation": st.column_config.TextColumn("Situation", width="medium"),
                "Pensée Auto": st.column_config.TextColumn("Pensée Auto", width="medium"),
                "Pensée Rationnelle": st.column_config.TextColumn("Rationnel", width="medium"),
            },
            hide_index=True
        )
        
        st.divider()
        st.subheader("🛠️ Modifier ou Supprimer une entrée")

        # B. SÉLECTEUR D'ENTRÉE
        # On trie pour avoir les plus récents en premier
        df_sorted = df_history.sort_values(by="Date", ascending=False)
        
        # Création d'un dictionnaire { "Label lisible" : index_original }
        options_dict = {}
        for idx, row in df_sorted.iterrows():
            # On coupe le texte s'il est trop long pour le menu déroulant
            sit_short = (str(row['Situation'])[:40] + '...') if len(str(row['Situation'])) > 40 else str(row['Situation'])
            label = f"📅 {row['Date']} | {sit_short}"
            options_dict[label] = idx

        selected_label = st.selectbox(
            "Sélectionnez l'exercice à modifier ou supprimer :", 
            options=list(options_dict.keys()),
            index=None,
            placeholder="Choisissez une ligne..."
        )

        # C. ZONE D'ACTION (Si une ligne est sélectionnée)
        if selected_label:
            idx_sel = options_dict[selected_label]
            row_sel = df_history.loc[idx_sel]

            col_edit, col_delete = st.columns([1, 1])

            # --- BOUTON SUPPRIMER ---
            with col_delete:
                if st.button("🗑️ Supprimer définitivement", type="primary"):
                    # 1. Suppression Cloud
                    try:
                        from connect_db import delete_data_flexible
                        pid = CURRENT_USER_ID
                        # On utilise Date et Situation comme clés pour identifier la ligne
                        delete_data_flexible("Beck", {
                            "Patient": pid,
                            "Date": str(row_sel['Date']),
                            "Situation": str(row_sel['Situation']) # On suppose que la situation est assez unique
                        })
                    except: pass
                    
                    # 2. Suppression Locale
                    st.session_state.data_beck = df_history.drop(idx_sel).reset_index(drop=True)
                    st.success("Entrée supprimée !")
                    st.rerun()

            # --- MODIFICATION (EXPANDER) ---
            with st.expander("✏️ Modifier / Corriger cette entrée", expanded=True):
                st.info("Modifiez les champs ci-dessous puis cliquez sur 'Valider les modifications'.")
                
                with st.form("edit_form"):
                    # On pré-remplit les champs avec les valeurs actuelles (row_sel)
                    
                    # Date & Situation
                    try:
                        d_val = pd.to_datetime(row_sel['Date']).date()
                    except:
                        d_val = datetime.now()
                        
                    e_date = st.date_input("Date", value=d_val)
                    e_sit = st.text_area("Situation", value=row_sel['Situation'])
                    
                    # Emotion
                    c1, c2 = st.columns(2)
                    with c1: e_emo = st.text_input("Émotion", value=row_sel['Émotion'])
                    with c2: e_int_avt = st.slider("Intensité (Avant)", 0, 10, int(row_sel['Intensité (Avant)']))
                    
                    # Pensées
                    e_auto = st.text_area("Pensée Automatique", value=row_sel['Pensée Auto'])
                    e_croy_avt = st.slider("Croyance (Avant)", 0, 10, int(row_sel['Croyance (Avant)']))
                    
                    e_rat = st.text_area("Pensée Rationnelle", value=row_sel['Pensée Rationnelle'])
                    e_croy_rat = st.slider("Croyance (Rationnelle)", 0, 10, int(row_sel['Croyance (Rationnelle)']))
                    
                    # Après
                    st.markdown("**Ré-évaluation**")
                    c3, c4 = st.columns(2)
                    with c3: e_int_apr = st.slider("Intensité (Après)", 0, 10, int(row_sel['Intensité (Après)']))
                    with c4: e_croy_apr = st.slider("Croyance (Après)", 0, 10, int(row_sel['Croyance (Après)']))
                    
                    btn_save_edit = st.form_submit_button("💾 Valider les modifications")

                    if btn_save_edit:
                        # LOGIQUE DE MISE À JOUR : On supprime l'ancien et on crée le nouveau
                        
                        # 1. Suppression de l'ancienne version (Cloud)
                        try:
                            from connect_db import delete_data_flexible, save_data
                            pid = CURRENT_USER_ID
                            delete_data_flexible("Beck", {
                                "Patient": pid,
                                "Date": str(row_sel['Date']),
                                "Situation": str(row_sel['Situation'])
                            })
                            
                            # 2. Création de la nouvelle ligne
                            updated_row = {
                                "Patient": pid,
                                "Date": str(e_date),
                                "Situation": e_sit,
                                "Émotion": e_emo,
                                "Intensité (Avant)": e_int_avt,
                                "Pensée Auto": e_auto,
                                "Croyance (Avant)": e_croy_avt,
                                "Pensée Rationnelle": e_rat,
                                "Croyance (Rationnelle)": e_croy_rat,
                                "Intensité (Après)": e_int_apr,
                                "Croyance (Après)": e_croy_apr
                            }
                            
                            # 3. Sauvegarde de la nouvelle version (Cloud)
                            # Conversion dict -> list
                            values_list = [updated_row[col] for col in COLS_BECK]
                            save_data("Beck", values_list)
                            
                        except Exception as e:
                            st.error(f"Erreur Cloud: {e}")
                        
                        # 4. Mise à jour Locale (On remplace dans le dataframe)
                        st.session_state.data_beck.loc[idx_sel, "Date"] = str(e_date)
                        st.session_state.data_beck.loc[idx_sel, "Situation"] = e_sit
                        st.session_state.data_beck.loc[idx_sel, "Émotion"] = e_emo
                        st.session_state.data_beck.loc[idx_sel, "Intensité (Avant)"] = e_int_avt
                        st.session_state.data_beck.loc[idx_sel, "Pensée Auto"] = e_auto
                        st.session_state.data_beck.loc[idx_sel, "Croyance (Avant)"] = e_croy_avt
                        st.session_state.data_beck.loc[idx_sel, "Pensée Rationnelle"] = e_rat
                        st.session_state.data_beck.loc[idx_sel, "Croyance (Rationnelle)"] = e_croy_rat
                        st.session_state.data_beck.loc[idx_sel, "Intensité (Après)"] = e_int_apr
                        st.session_state.data_beck.loc[idx_sel, "Croyance (Après)"] = e_croy_apr
                        
                        st.success("Modification enregistrée !")
                        st.rerun()

    else:
        st.info("Aucun exercice enregistré pour le moment. Commencez par l'onglet 'Nouvel Exercice'.")

st.divider()
st.set_page_config(page_title="Colonnes Beck", page_icon="📉")
if st.button("⬅️ Retour au tableau de bord"):
    # On dit au menu principal de rouvrir l'onglet "Échelles"
    st.session_state["target_tab"] = "🛠️ Outils & Exos"
    st.switch_page("streamlit_app.py")