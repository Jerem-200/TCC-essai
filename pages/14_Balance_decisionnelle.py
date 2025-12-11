import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Balance Décisionnelle", page_icon="⚖️")

# --- VIGILE DE SÉCURITÉ ---
if "authentifie" not in st.session_state or not st.session_state.authentifie:
    st.warning("⛔ Veuillez vous connecter sur la page d'accueil.")
    st.switch_page("streamlit_app.py")
    st.stop()

st.title("⚖️ Balance Décisionnelle")
st.info("Comparez plusieurs options pour prendre la meilleure décision possible.")

# --- 0. INITIALISATION ET CHARGEMENT CLOUD ---

# A. CHARGEMENT DE L'HISTORIQUE
if "data_balance" not in st.session_state:
    cols_balance = ["Patient", "Date", "Sujet", "Option Gagnante", "Détail Arguments", "Score"]
    df_final = pd.DataFrame(columns=cols_balance)
    
    try:
        from connect_db import load_data
        # Assurez-vous que l'onglet Google Sheet s'appelle "Balance_Decisionnelle"
        data_cloud = load_data("Balance_Decisionnelle") 
    except:
        data_cloud = []

    if data_cloud:
        df_cloud = pd.DataFrame(data_cloud)
        # Harmonisation des colonnes
        for col in cols_balance:
            if col in df_cloud.columns:
                df_final[col] = df_cloud[col]
                
    st.session_state.data_balance = df_final

# B. Mémoires temporaires pour la session en cours
if "balance_args_current" not in st.session_state:
    st.session_state.balance_args_current = pd.DataFrame(columns=[
        "Option", "Type", "Description", "Intensité", "Score_Calc"
    ])

if "balance_options_list" not in st.session_state:
    st.session_state.balance_options_list = []

# --- CRÉATION DES ONGLETS ---
tab1, tab2 = st.tabs(["⚖️ Créer une balance", "🗄️ Historique"])

# ==============================================================================
# ONGLET 1 : L'OUTIL DE COMPARAISON
# ==============================================================================
with tab1:
    st.header("1. Le Sujet")
    sujet_decision = st.text_input("Quelle décision devez-vous prendre ?", placeholder="Ex: Déménager à Paris ou rester à Lyon ?")

    st.divider()

    # --- ÉTAPE 1 : DÉFINITION DES OPTIONS ---
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
                    # On supprime l'option de la liste ET ses arguments associés
                    st.session_state.balance_options_list.pop(i)
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
                opt_select = st.selectbox("Concerne l'option :", st.session_state.balance_options_list)
            with c2: 
                type_arg = st.selectbox("C'est un :", ["Avantage (+)", "Inconvénient (-)"])
            
            desc_arg = st.text_input("Description de l'argument :")
            intensite = st.slider("Intensité / Importance (1 à 10)", 1, 10, 5)

            if st.form_submit_button("Ajouter l'argument"):
                # Calcul du score (Positif ou Négatif)
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
                st.success("Argument ajouté !")
                st.rerun()

        # --- TABLEAU COMPARATIF ---
        if not st.session_state.balance_args_current.empty:
            st.divider()
            st.subheader("📊 Résultats Comparatifs")
            
            df_args = st.session_state.balance_args_current
            
            # Calcul des scores par option
            scores = df_args.groupby("Option")["Score_Calc"].sum().reset_index()
            scores.columns = ["Option", "Score Total"]
            scores = scores.sort_values(by="Score Total", ascending=False)
            
            # Affichage du tableau des scores
            st.dataframe(scores, use_container_width=True, hide_index=True)

            # Détail des arguments (Expandable)
            with st.expander("Voir le détail des arguments"):
                st.dataframe(df_args[["Option", "Type", "Description", "Intensité"]], use_container_width=True)
                
                # Suppression d'un argument spécifique
                arg_to_del = st.selectbox("Supprimer un argument incorrect :", 
                                          df_args.index, 
                                          format_func=lambda x: f"{df_args.loc[x, 'Option']} - {df_args.loc[x, 'Description']}")
                if st.button("Supprimer cet argument"):
                    st.session_state.balance_args_current = st.session_state.balance_args_current.drop(arg_to_del).reset_index(drop=True)
                    st.rerun()

            # Identification du gagnant
            if not scores.empty:
                winner = scores.iloc[0]
                st.success(f"🏆 L'option recommandée est : **{winner['Option']}** (Score : {winner['Score Total']})")
                
                # --- ÉTAPE 4 : ENREGISTREMENT ---
                st.divider()
                if st.button("💾 ENREGISTRER CETTE BALANCE DANS LE CLOUD"):
                    if not sujet_decision:
                        st.error("Veuillez indiquer le sujet de la décision en haut de page.")
                    else:
                        # Préparation des données pour le cloud
                        # On crée un résumé texte des arguments pour qu'il tienne dans une cellule Excel
                        resume_args = ""
                        for idx, row in df_args.iterrows():
                            signe = "+" if row['Score_Calc'] > 0 else "-"
                            resume_args += f"[{row['Option']}] {signe} {row['Description']} ({row['Intensité']}) | "

                        new_entry = {
                            "Date": datetime.now().strftime("%Y-%m-%d"),
                            "Sujet": sujet_decision,
                            "Option Gagnante": winner['Option'],
                            "Détail Arguments": resume_args,
                            "Score": int(winner['Score Total'])
                        }
                        
                        # 1. Mise à jour Locale
                        st.session_state.data_balance = pd.concat([st.session_state.data_balance, pd.DataFrame([new_entry])], ignore_index=True)
                        
                        # 2. Sauvegarde Cloud
                        try:
                            from connect_db import save_data
                            patient_id = st.session_state.get("patient_id", "Anonyme")
                            save_data("Balance_Decisionnelle", [
                                patient_id, 
                                new_entry["Date"], 
                                new_entry["Sujet"], 
                                new_entry["Option Gagnante"], 
                                new_entry["Détail Arguments"], 
                                new_entry["Score"]
                            ])
                            st.success("Sauvegarde réussie !")
                            
                            # Reset pour nouvelle balance
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
        # Tri par date
        if "Date" in df_history.columns:
            df_history = df_history.sort_values(by="Date", ascending=False)

        st.dataframe(df_history, use_container_width=True, hide_index=True)
        
        st.divider()
        
        # SUPPRESSION
        with st.expander("🗑️ Supprimer une entrée"):
            options_suppr = {
                f"{row['Date']} - {row['Sujet']}": idx 
                for idx, row in df_history.iterrows()
            }
            
            sel_suppr = st.selectbox("Choisir la ligne à supprimer :", list(options_suppr.keys()))
            
            if st.button("Confirmer la suppression"):
                idx_to_drop = options_suppr[sel_suppr]
                row_to_del = df_history.loc[idx_to_drop]

                # Suppression Cloud
                try:
                    from connect_db import delete_data_flexible
                    pid = st.session_state.get("patient_id", "Anonyme")
                    # On identifie la ligne par Patient + Date + Sujet
                    delete_data_flexible("Balance_Decisionnelle", {
                        "Patient": pid,
                        "Date": str(row_to_del['Date']),
                        "Sujet": row_to_del['Sujet']
                    })
                except Exception as e:
                    st.warning(f"Note : Suppression cloud non confirmée ({e}), mais supprimé localement.")
                
                # Suppression Locale
                st.session_state.data_balance = df_history.drop(idx_to_drop).reset_index(drop=True)
                st.success("Ligne supprimée !")
                st.rerun()
    else:
        st.info("Aucune balance décisionnelle enregistrée.")