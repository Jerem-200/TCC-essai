import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Balance Décisionnelle", page_icon="⚖️")

# --- VIGILE DE SÉCURITÉ ---
if "authentifie" not in st.session_state or not st.session_state.authentifie:
    st.warning("⛔ Veuillez vous connecter sur la page d'accueil.")
    st.switch_page("streamlit_app.py")
    st.stop()

# === GESTIONNAIRE DE CHARGEMENT (TOP LEVEL) ===
# C'est ce qui permet de remplir le titre sans bug "Already Rendered"
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
    
    # Initialisation de la clé si elle n'existe pas
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
                    # On nettoie aussi les arguments liés
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
        # clear_on_submit=False pour garder l'option sélectionnée
        with st.form("ajout_argument_balance", clear_on_submit=False):
            c1, c2 = st.columns(2)
            with c1: 
                opt_select = st.selectbox("Concerne l'option :", st.session_state.balance_options_list)
            with c2: 
                type_arg = st.selectbox("C'est un :", ["Avantage (+)", "Inconvénient (-)"])
            
            # Clés spécifiques pour pouvoir les vider manuellement
            desc_arg = st.text_input("Description de l'argument :", key="input_desc_arg")
            intensite = st.slider("Intensité / Importance (1 à 10)", 1, 10, 5, key="input_intensite_arg")

            if st.form_submit_button("Ajouter l'argument"):
                if desc_arg:
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
                    
                    # Reset manuel des champs
                    st.session_state["input_desc_arg"] = ""
                    st.session_state["input_intensite_arg"] = 5
                    st.rerun()
                else:
                    st.warning("Veuillez mettre une description.")

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
                # On crée une liste de labels uniques pour le selectbox
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
                        # Création du texte formaté pour Excel
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
                        
                        # 1. Update Local
                        st.session_state.data_balance = pd.concat([st.session_state.data_balance, pd.DataFrame([new_entry])], ignore_index=True)
                        
                        # 2. Update Cloud
                        try:
                            from connect_db import save_data
                            patient_id = st.session_state