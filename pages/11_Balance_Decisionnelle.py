import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Balance Décisionnelle", page_icon="⚖️")

# --- AJOUT : GESTION DES TOASTS APRÈS RECHARGEMENT ---
if "toast_msg" in st.session_state:
    st.toast(st.session_state.toast_msg, icon="🚀")
    del st.session_state.toast_msg
# -----------------------------------------------------

# ==============================================================================
# 0. SÉCURITÉ & NETTOYAGE (OBLIGATOIRE SUR CHAQUE PAGE)
# ==============================================================================

# 1. Vérification de l'authentification
if "authentifie" not in st.session_state or not st.session_state.authentifie:
    st.warning("🔒 Accès restreint. Veuillez entrer votre Code Patient sur l'accueil.")
    st.page_link("streamlit_app.py", label="Retourner à l'accueil", icon="🏠")
    st.stop()

# 2. Récupération sécurisée de l'ID
CURRENT_USER_ID = st.session_state.get("user_id", "")
if not CURRENT_USER_ID:
    CURRENT_USER_ID = st.session_state.get("patient_id", "")

if not CURRENT_USER_ID:
    st.error("Erreur d'identité. Veuillez vous reconnecter.")
    st.stop()

# 3. VERROUILLAGE ANTI-FUITE
if "balance_owner" not in st.session_state or st.session_state.balance_owner != CURRENT_USER_ID:
    # On vide les variables spécifiques à la balance
    if "data_balance" in st.session_state: del st.session_state.data_balance
    if "balance_args_current" in st.session_state: del st.session_state.balance_args_current
    st.session_state.balance_owner = CURRENT_USER_ID

# D. LE VIGILE (PERMISSIONS) - NOUVEAU
CLE_PAGE = "balance" # <--- Changez ceci selon la page (ex: "activites", "conso"...)

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

# === GESTIONNAIRE DE CHARGEMENT (TOP LEVEL) ===
if "sujet_a_charger" in st.session_state:
    st.session_state.input_sujet_decision = st.session_state.sujet_a_charger
    del st.session_state.sujet_a_charger

st.title("⚖️ Balance Décisionnelle")
st.info("Comparez plusieurs options pour prendre la meilleure décision possible.")

# --- 0. INITIALISATION ET CHARGEMENT CLOUD ---

# A. CHARGEMENT DE L'HISTORIQUE
if "data_balance" not in st.session_state:
    cols_balance = ["Patient", "Date", "Sujet", "Option Gagnante", "Détail Arguments", "Score"]
    df_final = pd.DataFrame(columns=cols_balance)
    
    try:
        from connect_db import load_data
        data_cloud = load_data("Balance_Decisionnelle") 
    except:
        data_cloud = []

    if data_cloud:
        df_cloud = pd.DataFrame(data_cloud)
        for col in cols_balance:
            if col in df_cloud.columns:
                df_final[col] = df_cloud[col]
    
    # --- FILTRE SÉCURITÉ ---
    if "Patient" in df_final.columns:
        df_final = df_final[df_final["Patient"].astype(str) == str(CURRENT_USER_ID)]
    else:
        df_final = pd.DataFrame(columns=cols_balance)
        
    st.session_state.data_balance = df_final

# B. Mémoires temporaires pour la session en cours
if "balance_args_current" not in st.session_state:
    st.session_state.balance_args_current = pd.DataFrame(columns=[
        "Option", "Type", "Description", "Intensité", "Score_Calc"
    ])

if "balance_options_list" not in st.session_state:
    st.session_state.balance_options_list = []

# --- FONCTION DE CALLBACK ---
def ajouter_argument_callback():
    """
    Cette fonction s'exécute AVANT le rechargement de la page.
    Elle gère l'ajout de l'argument et le nettoyage des champs input.
    """
    desc_arg = st.session_state.get("input_desc_arg", "")
    intensite = st.session_state.get("input_intensite_arg", 5)
    opt_select = st.session_state.get("sel_opt_arg") 
    type_arg = st.session_state.get("sel_type_arg")

    if desc_arg and opt_select and type_arg:
        score_calc = intensite if "Avantage" in type_arg else -intensite
        
        new_arg = {
            "Option": opt_select,
            "Type": type_arg,
            "Description": desc_arg,
            "Intensité": intensite,
            "Score_Calc": score_calc
        }
        
        st.session_state.balance_args_current = pd.concat(
            [st.session_state.balance_args_current, pd.DataFrame([new_arg])], 
            ignore_index=True
        )
        
        st.toast("✅ Argument ajouté avec succès !", icon="👍")
        
        # RESET DES CHAMPS
        st.session_state["input_desc_arg"] = ""
        st.session_state["input_intensite_arg"] = 5
    else:
        st.toast("⚠️ Veuillez mettre une description.", icon="🚫")


# --- CRÉATION DES ONGLETS ---
tab1, tab2 = st.tabs(["⚖️ Créer une balance", "🗄️ Historique"])

# ==============================================================================
# ONGLET 1 : L'OUTIL DE COMPARAISON
# ==============================================================================
with tab1:
    st.header("1. Le Sujet")
    
    if "input_sujet_decision" not in st.session_state:
        st.session_state.input_sujet_decision = ""

    sujet_decision = st.text_input(
        "Quelle décision devez-vous prendre ?", 
        placeholder="Ex: Déménager à Paris ou rester à Lyon ?",
        key="input_sujet_decision" 
    )

    st.divider()

    # --- ÉTAPE 2 : DÉFINITION DES OPTIONS ---
    st.header("2. Les Options")
    st.caption("Listez les différentes options qui s'offrent à vous.")

    with st.form("ajout_option_form", clear_on_submit=True):
        col_opt, col_btn = st.columns([4, 1])
        with col_opt:
            nouvelle_opt = st.text_input("Nouvelle option :", placeholder="Ex: Option A...", label_visibility="collapsed")
        with col_btn:
            submitted_opt = st.form_submit_button("Ajouter")
        
        if submitted_opt and nouvelle_opt:
            if nouvelle_opt not in st.session_state.balance_options_list:
                st.session_state.balance_options_list.append(nouvelle_opt)
                st.rerun()
            else:
                st.warning("Cette option existe déjà.")

    # Affichage et suppression des options
    if st.session_state.balance_options_list:
        st.write("**Options en lice :**")
        for i, opt in enumerate(st.session_state.balance_options_list):
            c_text, c_del = st.columns([5, 1])
            with c_text: st.markdown(f"🔹 **{opt}**")
            with c_del:
                if st.button("🗑️", key=f"del_opt_{i}"):
                    st.session_state.balance_options_list.pop(i)
                    if not st.session_state.balance_args_current.empty:
                        st.session_state.balance_args_current = st.session_state.balance_args_current[
                            st.session_state.balance_args_current["Option"] != opt
                        ]
                    st.rerun()
    else:
        st.info("Ajoutez au moins deux options pour commencer la comparaison.")

    st.divider()

    # --- ÉTAPE 3 : ARGUMENTS ---
    st.header("3. Peser le pour et le contre")
    
    if len(st.session_state.balance_options_list) >= 1:
        with st.form("ajout_argument_balance", clear_on_submit=False):
            c1, c2 = st.columns(2)
            with c1: 
                opt_select = st.selectbox("Concerne l'option :", st.session_state.balance_options_list, key="sel_opt_arg")
            with c2: 
                type_arg = st.selectbox("C'est un :", ["Avantage (+)", "Inconvénient (-)"], key="sel_type_arg")
            
            desc_arg = st.text_input("Description de l'argument :", key="input_desc_arg")
            intensite = st.slider("Intensité / Importance (1 à 10)", 1, 10, 5, key="input_intensite_arg")

            st.form_submit_button("Ajouter l'argument", on_click=ajouter_argument_callback)

        # --- TABLEAU COMPARATIF ---
        if not st.session_state.balance_args_current.empty:
            st.divider()
            st.subheader("📊 Résultats Comparatifs")
            
            df_args = st.session_state.balance_args_current
            
            # Calcul des scores
            scores = df_args.groupby("Option")["Score_Calc"].sum().reset_index()
            scores.columns = ["Option", "Score Total"]
            scores = scores.sort_values(by="Score Total", ascending=False)
            
            st.dataframe(scores, use_container_width=True, hide_index=True)

            with st.expander("Voir le détail des arguments"):
                st.dataframe(df_args[["Option", "Type", "Description", "Intensité"]], use_container_width=True)
                
                # Suppression d'un argument
                labels_args = [f"{row['Option']} - {row['Description']}" for i, row in df_args.iterrows()]
                arg_to_del_idx = st.selectbox("Supprimer un argument :", range(len(df_args)), format_func=lambda x: labels_args[x])
                
                if st.button("Supprimer cet argument"):
                    st.session_state.balance_args_current = st.session_state.balance_args_current.drop(arg_to_del_idx).reset_index(drop=True)
                    st.rerun()

            # Gagnant & Enregistrement
            if not scores.empty:
                winner = scores.iloc[0]
                st.success(f"🏆 L'option recommandée est : **{winner['Option']}** (Score : {winner['Score Total']})")
                
                st.divider()
                if st.button("💾 ENREGISTRER CETTE BALANCE DANS LE CLOUD"):
                    if not sujet_decision:
                        st.error("Veuillez indiquer le sujet de la décision en haut de page.")
                    else:
                        liste_lignes = []
                        for idx, row in df_args.iterrows():
                            icone = "🟢" if "Avantage" in row['Type'] else "🔴"
                            ligne = f"• {row['Option']} : {icone} {row['Description']} ({row['Intensité']}/10)"
                            liste_lignes.append(ligne)

                        resume_args = "\n".join(liste_lignes)

                        new_entry = {
                            "Date": datetime.now().strftime("%Y-%m-%d"),
                            "Sujet": sujet_decision,
                            "Option Gagnante": winner['Option'],
                            "Détail Arguments": resume_args,
                            "Score": int(winner['Score Total'])
                        }
                        
                        st.session_state.data_balance = pd.concat([st.session_state.data_balance, pd.DataFrame([new_entry])], ignore_index=True)
                        
                        try:
                            from connect_db import save_data
                            # On utilise la variable sécurisée définie en haut
                            save_data("Balance_Decisionnelle", [
                                CURRENT_USER_ID,  # <--- CORRECTION (au lieu de patient_id)
                                new_entry["Date"], 
                                new_entry["Sujet"], 
                                new_entry["Option Gagnante"], 
                                new_entry["Détail Arguments"], 
                                new_entry["Score"]
                            ])
                            st.success("Sauvegarde réussie !")
                            
                            st.session_state.balance_args_current = pd.DataFrame(columns=["Option", "Type", "Description", "Intensité", "Score_Calc"])
                            st.session_state.balance_options_list = []
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"Erreur de sauvegarde Cloud : {e}")

    else:
        st.warning("Ajoutez des options pour débloquer la saisie des arguments.")

# ==============================================================================
# ONGLET 2 : HISTORIQUE
# ==============================================================================
with tab2:
    st.header("🗄️ Historique des décisions")
    
    df_history = st.session_state.data_balance
    
    if not df_history.empty:
        if "Date" in df_history.columns:
            df_history = df_history.sort_values(by="Date", ascending=False).reset_index(drop=True)

        # --- 1. CONVERSION DU NOM (Code -> PAT-XXX) ---
        df_display = df_history.copy()
        nom_dossier = CURRENT_USER_ID # Par défaut
        
        try:
            from connect_db import load_data
            infos = load_data("Codes_Patients")
            if infos:
                df_i = pd.DataFrame(infos)
                # On gère les noms de colonnes possibles
                col_id = "Identifiant" if "Identifiant" in df_i.columns else "Commentaire"
                
                # On trouve la correspondance
                match = df_i[df_i["Code"] == CURRENT_USER_ID]
                if not match.empty: nom_dossier = match.iloc[0][col_id]
        except: pass
        
        # On remplace dans le tableau d'affichage
        if "Patient" in df_display.columns:
            df_display["Patient"] = nom_dossier
        
        # Affichage Propre
        st.dataframe(
            df_display, 
            column_config={"Patient": st.column_config.TextColumn("Dossier")},
            use_container_width=True, 
            hide_index=True
        )
        
        st.divider()

        # --- GESTION DES DOUBLONS AVEC LABELS PARLANTS ---
        options_history = {}
        for idx, row in df_history.iterrows():
            # On construit un label qui contient le GAGNANT et le SCORE pour aider à différencier
            gagnant = row.get('Option Gagnante', '?')
            score = row.get('Score', 0)
            
            base_label = f"{row['Date']} - {row['Sujet']} | 🏆 {gagnant} ({score} pts)"
            
            # Si jamais ce label exact existe déjà (doublon parfait), on ajoute un compteur
            if base_label in options_history:
                final_label = f"{base_label} (Copie {idx})"
            else:
                final_label = base_label
                
            options_history[final_label] = idx

        # --- BLOC 1 : SUPPRESSION ---
        with st.expander("🗑️ Supprimer une entrée"):
            sel_suppr = st.selectbox("Choisir la ligne à supprimer :", list(options_history.keys()), key="select_suppr")
            
            if st.button("Confirmer la suppression"):
                idx_to_drop = options_history[sel_suppr]
                row_to_del = df_history.loc[idx_to_drop]

                try:
                    from connect_db import delete_data_flexible
                    pid = CURRENT_USER_ID
                    delete_data_flexible("Balance_Decisionnelle", {
                        "Patient": pid,
                        "Date": str(row_to_del['Date']),
                        "Sujet": row_to_del['Sujet']
                    })
                except:
                    pass
                
                st.session_state.data_balance = df_history.drop(idx_to_drop).reset_index(drop=True)
                st.success("Ligne supprimée !")
                st.rerun()

        # --- BLOC 2 : MODIFICATION (RECHARGER) ---
        with st.expander("✏️ Modifier / Reprendre une balance"):
            st.write("Sélectionnez une balance pour recharger ses données.")
            
            sel_modif = st.selectbox("Choisir la balance à modifier :", list(options_history.keys()), key="select_modif")
            
            if st.button("🔄 Charger les données pour modification", key="btn_charger_modif"):
                idx_to_load = options_history[sel_modif]
                row_to_load = df_history.loc[idx_to_load]
                
                # 1. Transfert du sujet
                st.session_state.sujet_a_charger = row_to_load['Sujet']
                
                # 2. Parsing
                raw_text = row_to_load['Détail Arguments']
                
                if pd.isna(raw_text) or str(raw_text) == "nan":
                    lignes = []
                else:
                    lignes = str(raw_text).split('\n')
                
                new_data = []
                loaded_options = []
                
                for ligne in lignes:
                    ligne = ligne.strip()
                    if not ligne: continue
                    try:
                        clean_line = ligne.replace("• ", "")
                        if " : " in clean_line:
                            parts = clean_line.split(" : ", 1)
                            opt_name = parts[0].strip()
                            reste = parts[1].strip()
                        else:
                            opt_name = "Option Inconnue"
                            reste = clean_line

                        if opt_name not in loaded_options:
                            loaded_options.append(opt_name)
                        
                        if "🟢" in reste:
                            type_arg = "Avantage (+)"
                            reste = reste.replace("🟢 ", "").strip()
                            score_mult = 1
                        elif "🔴" in reste:
                            type_arg = "Inconvénient (-)"
                            reste = reste.replace("🔴 ", "").strip()
                            score_mult = -1
                        else:
                            type_arg = "Avantage (+)"
                            score_mult = 1
                            
                        if "(" in reste and ")" in reste:
                            last_paren_idx = reste.rfind("(")
                            description = reste[:last_paren_idx].strip()
                            try:
                                intensite_part = reste[last_paren_idx+1:].replace(")", "")
                                intensite_val = int(intensite_part.split("/")[0])
                            except:
                                intensite_val = 5
                        else:
                            description = reste
                            intensite_val = 5

                        new_data.append({
                            "Option": opt_name,
                            "Type": type_arg,
                            "Description": description,
                            "Intensité": intensite_val,
                            "Score_Calc": intensite_val * score_mult
                        })
                    except Exception as e:
                        print(f"Erreur parsing ligne: {ligne} - {e}")
                
                # 3. Mise à jour
                st.session_state.balance_options_list = loaded_options
                st.session_state.balance_args_current = pd.DataFrame(new_data)
                
                # --- MODIFICATION ICI ---
                # Au lieu d'afficher le toast maintenant (qui serait tué par le rerun),
                # on le stocke pour qu'il s'affiche au démarrage suivant.
                st.session_state.toast_msg = "✅ Données chargées ! Retournez sur l'onglet 'Créer une balance' pour modifier."
                st.rerun()

    else:
        st.info("Aucune balance décisionnelle enregistrée.")
st.set_page_config(page_title="Balance Décisionnelle", page_icon="📉")
if st.button("⬅️ Retour au tableau de bord"):
    # On dit au menu principal de rouvrir l'onglet "Échelles"
    st.session_state["target_tab"] = "🛠️ Outils & Exos"
    st.switch_page("streamlit_app.py")