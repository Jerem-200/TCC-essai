import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Résolution de Problèmes", page_icon="💡")

# --- VIGILE DE SÉCURITÉ ---
if "authentifie" not in st.session_state or not st.session_state.authentifie:
    st.warning("⛔ Veuillez vous connecter sur la page d'accueil.")
    st.switch_page("streamlit_app.py")
    st.stop()

st.title("💡 Technique de Résolution de Problèmes")
st.caption("Définissez le problème, trouvez des solutions et passez à l'action.")

# ==============================================================================
# 0. INITIALISATION ET CHARGEMENT
# ==============================================================================

COLS_PB = ["Patient", "Date", "Problème", "Objectif", "Solution Choisie", "Plan Action", "Obstacles", "Ressources", "Date Évaluation"]

# A. CHARGEMENT DONNÉES CLOUD
if "data_problemes" not in st.session_state:
    df_final = pd.DataFrame(columns=COLS_PB)
    try:
        from connect_db import load_data
        data_cloud = load_data("Résolution_Problème")
        if data_cloud:
            df_cloud = pd.DataFrame(data_cloud)
            for col in COLS_PB:
                if col in df_cloud.columns:
                    df_final[col] = df_cloud[col]
                elif col.replace(" ", "_") in df_cloud.columns: # Gestion Plan_Action
                    df_final[col] = df_cloud[col.replace(" ", "_")]
    except: pass
    st.session_state.data_problemes = df_final

# B. VARIABLES TEMPORAIRES (Listes dynamiques)
if "liste_solutions_temp" not in st.session_state:
    st.session_state.liste_solutions_temp = []
if "plan_etapes_temp" not in st.session_state:
    st.session_state.plan_etapes_temp = []
if "analyse_detaillee" not in st.session_state: # Tableau avantages/inconvénients
    st.session_state.analyse_detaillee = pd.DataFrame(columns=["Solution", "Type", "Description", "Note", "Valeur"])

# --- ONGLETS ---
tab1, tab2 = st.tabs(["📝 Saisie & Modification", "📊 Historique Complet"])

# ==============================================================================
# ONGLET 1 : SAISIE ET MODIFICATION
# ==============================================================================
with tab1:
    # --- 1. SÉLECTEUR DE MODE (NOUVEAU / MODIFIER) ---
    df_hist = st.session_state.data_problemes
    options_chargement = ["🆕 Nouvel exercice"]
    
    # Dictionnaire de correspondance : "Label Affiché" -> Index dans le DataFrame
    map_options = {}
    
    if not df_hist.empty:
        df_hist_sorted = df_hist.sort_values(by="Date", ascending=False).reset_index(drop=True)
        for idx, row in df_hist_sorted.iterrows():
            lbl = f"📅 {row['Date']} : {str(row['Problème'])[:40]}..."
            options_chargement.append(lbl)
            map_options[lbl] = idx

    choix_mode = st.selectbox("Que voulez-vous faire ?", options_chargement)

    # --- LOGIQUE DE CHARGEMENT ---
    # On initialise les variables par défaut (Vides)
    val_prob = ""
    val_obj = ""
    val_obs = ""
    val_ress = ""
    val_sol_txt = "" # Si jamais on ne peut pas reconstruire la liste
    val_date_eval = datetime.now() + timedelta(days=7)
    current_key_for_delete = None # Pour savoir quoi supprimer en cas de modif

    if choix_mode != "🆕 Nouvel exercice":
        st.info("✏️ Mode Modification activé : Vous modifiez une entrée existante.")
        
        idx_load = map_options[choix_mode]
        row_load = df_hist_sorted.loc[idx_load]
        
        # 1. Champs Textes Simples
        val_prob = row_load["Problème"]
        val_obj = row_load["Objectif"]
        val_obs = row_load["Obstacles"]
        val_ress = row_load["Ressources"]
        val_sol_txt = row_load["Solution Choisie"]
        
        # 2. Dates
        try: val_date_eval = pd.to_datetime(row_load["Date Évaluation"]).date()
        except: pass
        
        # 3. Restauration des Listes (Uniquement si on vient de changer de sélection)
        # On utilise une clé de session pour ne pas recharger en boucle à chaque clic
        if f"loaded_{idx_load}" not in st.session_state:
            # A. Plan d'action (séparé par des retours à la ligne)
            raw_plan = str(row_load["Plan Action"])
            if raw_plan and raw_plan != "nan":
                st.session_state.plan_etapes_temp = [line.strip() for line in raw_plan.split('\n') if line.strip()]
            else:
                st.session_state.plan_etapes_temp = []
            
            # B. Solutions (On essaie de deviner si c'est une liste séparée par des virgules)
            # Note : C'est approximatif car on ne stocke pas la liste brute, mais le résultat final
            if val_sol_txt and "," in val_sol_txt:
                st.session_state.liste_solutions_temp = [s.strip() for s in val_sol_txt.split(',')]
            elif val_sol_txt:
                st.session_state.liste_solutions_temp = [val_sol_txt]
            
            # C. Reset Analyse (On ne peut pas la restaurer car non sauvegardée en détail dans le cloud)
            st.session_state.analyse_detaillee = st.session_state.analyse_detaillee.iloc[0:0]
            
            # Marqueur pour dire "c'est chargé"
            st.session_state[f"loaded_{idx_load}"] = True

        # Clé pour la suppression future (Date + Problème original)
        current_key_for_delete = {
            "Date": str(row_load["Date"]),
            "Problème": str(row_load["Problème"])
        }
    else:
        # Mode Nouveau : On vide si nécessaire
        if "is_clean_new" not in st.session_state:
            st.session_state.liste_solutions_temp = []
            st.session_state.plan_etapes_temp = []
            st.session_state.analyse_detaillee = st.session_state.analyse_detaillee.iloc[0:0]
            st.session_state.is_clean_new = True

    st.divider()

    # --- LE FORMULAIRE ---
    
    st.markdown("### 1. Définition")
    c1, c2 = st.columns(2)
    with c1: 
        probleme = st.text_area("Quel est le problème ?", value=val_prob, placeholder="Qui ? Quoi ? Où ? Quand ?")
    with c2: 
        objectif = st.text_area("Objectif réaliste :", value=val_obj, placeholder="Situation désirée")

    st.divider()

    st.markdown("### 2. Recherche de Solutions")
    st.caption("Ajoutez vos idées ici (Brainstorming).")
    
    # Ajout solution
    col_add, col_btn = st.columns([4, 1])
    with col_add: 
        new_sol = st.text_input("Nouvelle idée", key="input_new_sol", label_visibility="collapsed")
    with col_btn:
        if st.button("Ajouter", key="btn_add_sol"):
            if new_sol:
                st.session_state.liste_solutions_temp.append(new_sol)
                st.rerun()
    
    # Liste solutions
    if st.session_state.liste_solutions_temp:
        for i, s in enumerate(st.session_state.liste_solutions_temp):
            cols = st.columns([5, 1])
            cols[0].write(f"• {s}")
            if cols[1].button("🗑️", key=f"del_sol_{i}"):
                st.session_state.liste_solutions_temp.pop(i)
                st.rerun()
    
    st.divider()

    st.markdown("### 3. Décision")
    # Choix final (Multiselect pré-rempli si possible)
    # On s'assure que les options contiennent les valeurs chargées
    all_options = list(set(st.session_state.liste_solutions_temp + ([val_sol_txt] if val_sol_txt else [])))
    
    # Pré-selection
    default_sel = []
    if val_sol_txt:
        # On essaie de mapper la chaine chargée avec les options
        for opt in all_options:
            if opt in val_sol_txt:
                default_sel.append(opt)
    
    sol_finale = st.multiselect("Quelle(s) solution(s) choisissez-vous ?", options=all_options, default=default_sel)
    sol_finale_str = ", ".join(sol_finale) if sol_finale else val_sol_txt # Fallback texte

    st.divider()

    st.markdown("### 4. Plan d'Action")
    c_obs, c_res = st.columns(2)
    with c_obs: obstacles = st.text_area("Obstacles possibles", value=val_obs)
    with c_res: ressources = st.text_area("Ressources nécessaires", value=val_ress)

    st.write("**Étapes concrètes :**")
    # Ajout étape
    with st.form("add_step_form", clear_on_submit=True):
        cs1, cs2, cs3 = st.columns([3, 1, 1])
        with cs1: s_desc = st.text_input("Action")
        with cs2: s_date = st.date_input("Date", datetime.now())
        with cs3: s_heure = st.time_input("Heure", datetime.now().time())
        if st.form_submit_button("Ajouter étape"):
            step_str = f"• {s_date.strftime('%d/%m')} à {s_heure.strftime('%H:%M')} : {s_desc}"
            st.session_state.plan_etapes_temp.append(step_str)
            st.rerun()

    # Liste étapes (avec possibilité de supprimer)
    if st.session_state.plan_etapes_temp:
        for i, step in enumerate(st.session_state.plan_etapes_temp):
            c_st, c_sd = st.columns([5, 1])
            c_st.text(step)
            if c_sd.button("x", key=f"del_step_{i}"):
                st.session_state.plan_etapes_temp.pop(i)
                st.rerun()

    st.divider()

    st.markdown("### 5. Validation")
    date_eval = st.date_input("Date du bilan", value=val_date_eval)

    # BOUTON SAUVEGARDE UNIQUE
    btn_label = "💾 SAUVEGARDER (NOUVEAU)" if choix_mode == "🆕 Nouvel exercice" else "💾 METTRE À JOUR"
    
    if st.button(btn_label, type="primary"):
        # 1. Construction des données
        plan_complet_str = "\n".join(st.session_state.plan_etapes_temp)
        
        # Données à sauvegarder
        patient_id = st.session_state.get("patient_id", "Anonyme")
        today_str = datetime.now().strftime("%Y-%m-%d")
        # Si on modifie, on garde la date d'origine, sinon date du jour
        date_record = row_load["Date"] if choix_mode != "🆕 Nouvel exercice" else today_str
        
        new_record = {
            "Patient": patient_id,
            "Date": str(date_record),
            "Problème": probleme,
            "Objectif": objectif,
            "Solution Choisie": sol_finale_str,
            "Plan Action": plan_complet_str,
            "Obstacles": obstacles,
            "Ressources": ressources,
            "Date Évaluation": str(date_eval)
        }

        # 2. Si Modification : Suppression de l'ancien
        if choix_mode != "🆕 Nouvel exercice" and current_key_for_delete:
            try:
                from connect_db import delete_data_flexible
                delete_data_flexible("Résolution_Problème", {
                    "Patient": patient_id,
                    "Date": current_key_for_delete["Date"],
                    "Problème": current_key_for_delete["Problème"]
                })
                # Suppression locale
                st.session_state.data_problemes = st.session_state.data_problemes[
                    ~((st.session_state.data_problemes["Date"] == current_key_for_delete["Date"]) & 
                      (st.session_state.data_problemes["Problème"] == current_key_for_delete["Problème"]))
                ]
            except Exception as e:
                st.error(f"Erreur lors de la suppression de l'ancienne version : {e}")

        # 3. Sauvegarde (Nouveau ou Mise à jour)
        try:
            from connect_db import save_data
            # Liste respectant l'ordre COLS_PB
            data_list = [new_record[col] for col in COLS_PB]
            save_data("Résolution_Problème", data_list)
            
            # Mise à jour locale
            st.session_state.data_problemes = pd.concat([st.session_state.data_problemes, pd.DataFrame([new_record])], ignore_index=True)
            
            st.success("✅ Enregistré avec succès !")
            
            # On vide pour le prochain
            st.session_state.liste_solutions_temp = []
            st.session_state.plan_etapes_temp = []
            
            # Petit hack pour forcer le rechargement propre
            import time
            time.sleep(1)
            st.rerun()
            
        except Exception as e:
            st.error(f"Erreur de sauvegarde : {e}")


# ==============================================================================
# ONGLET 2 : HISTORIQUE SIMPLE (CONSULTATION)
# ==============================================================================
with tab2:
    st.header("Historique")
    st.info("Pour modifier ou supprimer, utilisez le sélecteur dans l'onglet 1.")
    
    if not st.session_state.data_problemes.empty:
        st.dataframe(
            st.session_state.data_problemes.sort_values(by="Date", ascending=False),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("Aucune donnée.")

st.divider()
st.page_link("streamlit_app.py", label="Retour à l'accueil", icon="🏠")