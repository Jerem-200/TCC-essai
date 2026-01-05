import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Résolution de Problèmes", page_icon="💡")

# --- VIGILE DE SÉCURITÉ SIMPLIFIÉ ---
if "authentifie" not in st.session_state or not st.session_state.authentifie:
    st.warning("🔒 Accès restreint. Veuillez entrer votre Code Patient sur l'accueil.")
    st.page_link("streamlit_app.py", label="Retourner à l'accueil pour se connecter", icon="🏠")
    st.stop() # Arrête le chargement du reste de la page

# 1. Récupération simple de l'ID
# Grâce à votre modification dans l'accueil, ceci contient DÉJÀ "PAT-001"
CURRENT_USER_ID = st.session_state.get("user_id", "")

if not CURRENT_USER_ID:
    st.error("Session expirée. Veuillez vous reconnecter.")
    st.stop()

# 2. Verrouillage des données (Système Anti-Fuite)
# Si l'utilisateur change, on vide la mémoire
if "pb_owner" not in st.session_state or st.session_state.pb_owner != CURRENT_USER_ID:
    if "data_problemes" in st.session_state: del st.session_state.data_problemes
    st.session_state.pb_owner = CURRENT_USER_ID

# D. LE VIGILE (PERMISSIONS) - NOUVEAU
CLE_PAGE = "problemes" # <--- Changez ceci selon la page (ex: "activites", "conso"...)

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

st.title("💡 Technique de Résolution de Problèmes")
st.info("Une méthode structurée pour transformer un problème en plan d'action.")

# --- 0. INITIALISATION ET CHARGEMENT (ROBUSTE) ---

# A. CHARGEMENT DE L'HISTORIQUE DES PROBLÈMES
if "data_problemes" not in st.session_state:
    cols_pb = ["Patient", "Date", "Problème", "Objectif", "Solution Choisie", "Plan Action", "Obstacles", "Ressources", "Date Évaluation"]
    df_final = pd.DataFrame(columns=cols_pb)
    
    # 1. Tentative de chargement Cloud
    try:
        from connect_db import load_data
        data_cloud = load_data("Résolution_Problème") # Vérifiez que l'onglet Excel s'appelle bien "Résolution_Problème"
    except:
        data_cloud = []

    if data_cloud:
        df_cloud = pd.DataFrame(data_cloud)
        
        # 2. Remplissage intelligent (Gestion Majuscules/Minuscules)
        for col in cols_pb:
            if col in df_cloud.columns:
                df_final[col] = df_cloud[col]
            elif col.lower() in df_cloud.columns: # Si Excel a "date" au lieu de "Date"
                df_final[col] = df_cloud[col.lower()]
            elif col.replace(" ", "_") in df_cloud.columns: # Si Excel a "Plan_Action"
                df_final[col] = df_cloud[col.replace(" ", "_")]
                
    st.session_state.data_problemes = df_final

# B. Mémoires temporaires (Pas besoin de charger, on les vide au démarrage)
if "analyse_detaillee" not in st.session_state:
    st.session_state.analyse_detaillee = pd.DataFrame(columns=[
        "Solution", "Type", "Terme", "Description", "Note", "Valeur"
    ])

if "liste_solutions_temp" not in st.session_state:
    st.session_state.liste_solutions_temp = []

if "plan_etapes_temp" not in st.session_state:
    st.session_state.plan_etapes_temp = []

# --- CRÉATION DES ONGLETS ---
tab1, tab2 = st.tabs(["💡 Méthode (Saisie)", "📊 Tableau Récapitulatif"])

# ==============================================================================
# ONGLET 1 : LA MÉTHODE COMPLÈTE
# ==============================================================================
with tab1:
    st.markdown("### 1. Stop & Attitude Constructive")

    with st.expander("🛑 Lire les consignes de départ (Important)", expanded=True):
        st.markdown("""
        **1. Stop :**
        On doit d’abord réaliser que l’on a un problème qui n’est pas facile à résoudre et qui mérite qu’on prenne un peu de temps pour bien y réfléchir. 
        
        **2. Attitude constructive :**
        Il est important d’adopter une orientation constructive face au problème. Il s’agit de voir le problème comme une **occasion ou un défi** plutôt que comme une menace. 
        """)

    st.divider()

    # ==============================================================================
    # BLOC 1 : DÉFINITION
    # ==============================================================================
    st.markdown("### 1. Définition")
    st.caption("Définissez le problème de façon précise.")
    probleme = st.text_area("Quel est le problème ?", placeholder="Qui ? Quoi ? Où ? Quand ?")

    st.markdown("### 2. Objectifs")
    st.caption("Quels seraient les signes concrets que l'objectif est atteint ?")
    objectif = st.text_area("Mon objectif réaliste :")

    st.divider()

    # ==============================================================================
    # BLOC 2 : BRAINSTORMING
    # ==============================================================================
    st.markdown("### 3. Recherche de solutions")
    st.caption("Ajoutez toutes vos idées une par une.")

    with st.form("ajout_solution_form", clear_on_submit=True):
        col_input, col_btn = st.columns([4, 1])
        with col_input:
            nouvelle_solution = st.text_input("Nouvelle solution :", placeholder="Ex: Demander de l'aide...", label_visibility="collapsed")
        with col_btn:
            submitted_ajout = st.form_submit_button("Ajouter")
        
        if submitted_ajout and nouvelle_solution:
            st.session_state.liste_solutions_temp.append(nouvelle_solution)
            st.rerun()

    if st.session_state.liste_solutions_temp:
        st.write("---")
        st.write("**Vos idées listées :**")
        for i, sol in enumerate(st.session_state.liste_solutions_temp):
            c_text, c_del = st.columns([5, 1])
            with c_text: st.markdown(f"**{i+1}.** {sol}")
            with c_del:
                if st.button("🗑️", key=f"del_sol_{i}"):
                    st.session_state.liste_solutions_temp.pop(i)
                    st.rerun()
    else:
        st.info("Votre liste est vide.")

    st.divider()

    # ==============================================================================
    # BLOC 3 : ANALYSE
    # ==============================================================================
    st.markdown("### 4. Analyse Avantages / Inconvénients")

    if len(st.session_state.liste_solutions_temp) > 0:
        st.write("Pour chaque solution, ajoutez des arguments.")
        
        with st.form("ajout_argument_form", clear_on_submit=True):
            c_sol, c_type, c_term = st.columns(3)
            with c_sol: sol_selected = st.selectbox("Solution", st.session_state.liste_solutions_temp)
            with c_type: type_point = st.selectbox("Type", ["Avantage (+)", "Inconvénient (-)"])
            with c_term: terme = st.selectbox("Échéance", ["Court terme", "Moyen terme", "Long terme"])
            
            c_desc, c_note = st.columns([3, 1])
            with c_desc: desc_point = st.text_input("Description")
            with c_note: note_point = st.number_input("Importance (0-10)", 0, 10, 5)

            if st.form_submit_button("➕ Ajouter l'argument"):
                valeur = note_point if "Avantage" in type_point else -note_point
                new_entry = {"Solution": sol_selected, "Type": type_point, "Terme": terme, "Description": desc_point, "Note": note_point, "Valeur": valeur}
                st.session_state.analyse_detaillee = pd.concat([st.session_state.analyse_detaillee, pd.DataFrame([new_entry])], ignore_index=True)
                st.success("Ajouté !")

        if not st.session_state.analyse_detaillee.empty:
            st.divider()
            st.markdown("#### 📊 Tableau Comparatif")
            df = st.session_state.analyse_detaillee
            rows_display = []
            for sol in df["Solution"].unique():
                pros = df[(df["Solution"] == sol) & (df["Type"].str.contains("Avantage"))]
                pros_score = pros["Note"].sum()
                pros_text = "\n".join([f"- {r['Description']} ({r['Note']}/10)" for i, r in pros.iterrows()])
                
                cons = df[(df["Solution"] == sol) & (df["Type"].str.contains("Inconvénient"))]
                cons_score = cons["Note"].sum()
                cons_text = "\n".join([f"- {r['Description']} ({r['Note']}/10)" for i, r in cons.iterrows()])
                
                rows_display.append({"Solution": sol, "Avantages": pros_text, "Total (+)": pros_score, "Inconvénients": cons_text, "Total (-)": cons_score, "Bilan": pros_score - cons_score})
                
            df_display = pd.DataFrame(rows_display)
            st.table(df_display.set_index("Solution"))
            
            best_sol = df_display.loc[df_display["Bilan"].idxmax()]
            st.success(f"💡 Meilleure solution : **{best_sol['Solution']}** (Score : {best_sol['Bilan']})")

            with st.expander("Gérer / Supprimer des arguments"):
                df["label"] = df["Solution"] + " - " + df["Description"] + " (" + df["Note"].astype(str) + ")"
                options_arg = {row["label"]: i for i, row in df.iterrows()}
                sel_arg = st.selectbox("Choisir un argument à supprimer", list(options_arg.keys()))
                if st.button("Supprimer cet argument"):
                    st.session_state.analyse_detaillee = st.session_state.analyse_detaillee.drop(options_arg[sel_arg]).reset_index(drop=True)
                    st.rerun()
    else:
        st.info("👆 Ajoutez des solutions à l'étape 3.")

    st.divider()

    # ==============================================================================
    # BLOC 4 : DÉCISION & PLAN D'ACTION
    # ==============================================================================
    st.markdown("### 5. Décision finale")
    st.caption("Quelle(s) solution(s) choisissez-vous finalement ? [cite: 22-23]")

    # --- SÉLECTION DES SOLUTIONS (MULTI-SELECT) ---
    if st.session_state.liste_solutions_temp:
        solutions_retenues = st.multiselect(
            "Je décide de mettre en œuvre la ou les solutions suivantes :", 
            st.session_state.liste_solutions_temp
        )
        # On transforme la liste en une seule chaîne de texte pour la sauvegarde
        solution_choisie = ", ".join(solutions_retenues)
    else:
        # Cas de secours si la liste est vide (champ libre)
        solution_choisie = st.text_input("Je décide de mettre en œuvre :")

    st.markdown("### 6. Préparation")
    c1, c2 = st.columns(2)
    with c1: obstacles = st.text_area("Obstacles possibles")
    with c2: ressources = st.text_area("Ressources nécessaires")

    st.divider()

    # --- NOUVEAU : PLAN D'ACTION PAR ÉTAPES ---
    st.markdown("### 7. Plan d'action détaillé")
    st.caption("Déterminez les étapes par lesquelles vous devez passer pour appliquer la solution choisie. Faites un plan détaillé, avec un échéancier précis et réaliste. Veillez à ce que la première étape soit assez facile et passez à l’action rapidement et si possible immédiatement. Un premier pas même tout petit vous donnera le sentiment d’avoir « brisé la glace ». ")

    # Formulaire d'ajout d'étape (AVEC HEURE)
    with st.form("ajout_etape_form", clear_on_submit=True):
        # On divise en 3 colonnes : Description (large) | Date (moyen) | Heure (petit)
        c_step, c_date, c_heure = st.columns([3, 1, 1])
        
        with c_step:
            desc_etape = st.text_input("Description de l'étape", placeholder="Ex: Appeler M. Dupont")
        with c_date:
            date_etape = st.date_input("Date prévue", datetime.now())
        with c_heure:
            # CHANGEMENT ICI : Ajout de l'heure
            heure_etape = st.time_input("Heure", datetime.now().time())
        
        if st.form_submit_button("Ajouter cette étape"):
            # On formate l'étape avec la date ET l'heure
            # Format : "• 05/12 à 14:30 : Faire ceci"
            etape_str = f"• {date_etape.strftime('%d/%m')} à {heure_etape.strftime('%H:%M')} : {desc_etape}"
            st.session_state.plan_etapes_temp.append(etape_str)
            st.rerun()

    # Affichage de la liste des étapes
    if st.session_state.plan_etapes_temp:
        st.write("**Votre plan :**")
        for i, etape in enumerate(st.session_state.plan_etapes_temp):
            col_txt, col_del = st.columns([5, 1])
            with col_txt: st.text(etape) # st.text pour un affichage propre sans markdown qui pourrait gêner
            with col_del:
                if st.button("x", key=f"del_step_{i}"):
                    st.session_state.plan_etapes_temp.pop(i)
                    st.rerun()
    else:
        st.info("Ajoutez votre première étape ci-dessus (la première doit être facile !).")

    st.divider()

    # ==============================================================================
    # BLOC FINAL : VALIDATION & SAUVEGARDE
    # ==============================================================================
    st.markdown("### 8. Évaluation")
    st.caption("Évaluez les résultats après un délai raisonnable.")

    with st.form("validation_finale"):
        date_eval = st.date_input("Date de bilan des résultats", datetime.now() + timedelta(days=7))
        
        submitted_final = st.form_submit_button("💾 ENREGISTRER LE PLAN D'ACTION")

        if submitted_final:
            # Compilation de la liste en texte
            plan_texte_complet = "\n".join(st.session_state.plan_etapes_temp)
            
            new_row = {
                "Date": datetime.now().strftime("%Y-%m-%d"),
                "Problème": probleme, "Objectif": objectif, "Solution Choisie": solution_choisie,
                "Plan Action": plan_texte_complet,
                "Obstacles": obstacles, "Ressources": ressources, "Date Évaluation": str(date_eval)
            }
            
            # Mise à jour locale
            st.session_state.data_problemes = pd.concat([st.session_state.data_problemes, pd.DataFrame([new_row])], ignore_index=True)
            
            # Sauvegarde Cloud
            from connect_db import save_data
            patient = CURRENT_USER_ID
            save_data("Résolution_Problème", [patient, datetime.now().strftime("%Y-%m-%d"), probleme, objectif, solution_choisie, plan_texte_complet, obstacles, ressources, str(date_eval)])
            
            # On vide les mémoires pour repartir à zéro (sauf si on veut modifier, voir plus bas)
            st.session_state.analyse_detaillee = pd.DataFrame(columns=["Solution", "Type", "Terme", "Description", "Note", "Valeur"])
            st.session_state.liste_solutions_temp = [] 
            st.session_state.plan_etapes_temp = [] 
            
            st.success("Plan enregistré avec succès ! Retrouvez-le dans l'Historique.")

# ==============================================================================
# ONGLET 2 : HISTORIQUE & MODIFICATIONS (TYPE BECK)
# ==============================================================================
with tab2:
    st.header("🗂️ Historique & Actions")
    
    df_history = st.session_state.data_problemes
    
    if not df_history.empty:
        
        # --- A. CONVERSION DU NOM (PAT-XXX) ---
        df_display = df_history.copy()
        nom_dossier = CURRENT_USER_ID # Valeur par défaut
        
        try:
            from connect_db import load_data
            infos = load_data("Codes_Patients")
            if infos:
                df_i = pd.DataFrame(infos)
                # On gère si la colonne s'appelle Identifiant ou Commentaire
                col_id = "Identifiant" if "Identifiant" in df_i.columns else "Commentaire"
                
                # On trouve la ligne correspondante
                match = df_i[df_i["Code"] == CURRENT_USER_ID]
                if not match.empty: nom_dossier = match.iloc[0][col_id]
        except: pass
        
        # On remplace dans le tableau
        if "Patient" in df_display.columns:
            df_display["Patient"] = nom_dossier

        # --- B. AFFICHAGE ---
        st.dataframe(
            df_display.sort_values(by="Date", ascending=False),
            use_container_width=True,
            column_config={
                "Patient": st.column_config.TextColumn("Dossier"), # On renomme la colonne
                "Plan Action": st.column_config.TextColumn("Plan", width="large"),
                "Date": st.column_config.DateColumn("Date", format="DD/MM/YYYY"),
            },
            hide_index=True
        )
        
        st.divider()
        st.subheader("🛠️ Modifier ou Supprimer")

        # 2. SÉLECTION D'UNE ENTRÉE
        # On crée des labels lisibles pour le menu déroulant
        df_sorted = df_history.sort_values(by="Date", ascending=False)
        options_map = {}
        for idx, row in df_sorted.iterrows():
            prob_court = (str(row['Problème'])[:50] + '...') if len(str(row['Problème'])) > 50 else str(row['Problème'])
            label = f"📅 {row['Date']} | {prob_court}"
            options_map[label] = idx
            
        selected_entry = st.selectbox(
            "Sélectionnez le problème à gérer :", 
            list(options_map.keys()), 
            index=None, 
            placeholder="Cliquez pour choisir..."
        )

        # 3. ACTIONS
        if selected_entry:
            idx_sel = options_map[selected_entry]
            row_sel = df_history.loc[idx_sel]
            
            col_edit, col_del = st.columns([1, 1])
            
            # A. SUPPRESSION
            with col_del:
                if st.button("🗑️ Supprimer définitivement", type="primary"):
                    # Cloud
                    try:
                        from connect_db import delete_data_flexible
                        pid = CURRENT_USER_ID
                        delete_data_flexible("Résolution_Problème", {
                            "Patient": pid,
                            "Date": str(row_sel["Date"]),
                            "Problème": str(row_sel["Problème"])
                        })
                    except: pass
                    
                    # Local
                    st.session_state.data_problemes = df_history.drop(idx_sel).reset_index(drop=True)
                    st.success("Plan supprimé !")
                    st.rerun()

            # B. MODIFICATION (Formulaire pré-rempli)
            with st.expander("✏️ Modifier / Mettre à jour", expanded=True):
                st.info("Vous pouvez ajuster le plan d'action ou corriger le problème ici.")
                
                with st.form("edit_pb_form"):
                    # Récupération sécurisée des valeurs
                    def get_val(col): return str(row_sel.get(col, ""))
                    
                    # Champs
                    m_date = st.date_input("Date initiale", value=pd.to_datetime(row_sel['Date']).date())
                    m_prob = st.text_area("Problème", value=get_val("Problème"))
                    m_obj = st.text_area("Objectif", value=get_val("Objectif"))
                    m_sol = st.text_input("Solution Choisie", value=get_val("Solution Choisie"))
                    
                    # Le plan d'action est édité comme un texte complet
                    st.markdown("**Plan d'action (Éditable)**")
                    m_plan = st.text_area("Étapes (Modifiez directement le texte)", value=get_val("Plan Action"), height=150)
                    
                    c_m1, c_m2 = st.columns(2)
                    with c_m1: m_obs = st.text_area("Obstacles", value=get_val("Obstacles"))
                    with c_m2: m_ress = st.text_area("Ressources", value=get_val("Ressources"))
                    
                    try:
                        d_eval_init = pd.to_datetime(row_sel['Date Évaluation']).date()
                    except:
                        d_eval_init = datetime.now().date()
                    m_eval = st.date_input("Date Évaluation", value=d_eval_init)
                    
                    # Validation
                    if st.form_submit_button("💾 Valider les modifications"):
                        # 1. Suppression Cloud (Ancienne version)
                        try:
                            from connect_db import delete_data_flexible, save_data
                            pid = CURRENT_USER_ID
                            delete_data_flexible("Résolution_Problème", {
                                "Patient": pid,
                                "Date": str(row_sel["Date"]),
                                "Problème": str(row_sel["Problème"])
                            })
                            
                            # 2. Création Nouvelle version
                            updated_row = {
                                "Patient": pid,
                                "Date": str(m_date),
                                "Problème": m_prob, "Objectif": m_obj,
                                "Solution Choisie": m_sol, "Plan Action": m_plan,
                                "Obstacles": m_obs, "Ressources": m_ress,
                                "Date Évaluation": str(m_eval)
                            }
                            
                            # 3. Sauvegarde Cloud (Nouvelle version)
                            save_data("Résolution_Problème", [updated_row[c] for c in cols_pb])
                            
                        except Exception as e:
                            st.warning(f"Erreur Cloud: {e}")
                            
                        # 4. Mise à jour Locale (Directe dans le dataframe)
                        for k, v in updated_row.items():
                            if k in st.session_state.data_problemes.columns:
                                st.session_state.data_problemes.loc[idx_sel, k] = v
                                
                        st.success("Mise à jour réussie !")
                        st.rerun()

    else:
        st.info("Aucun historique disponible.")

st.divider()
st.set_page_config(page_title="Résolution de Problèmes", page_icon="📉")
if st.button("⬅️ Retour au tableau de bord"):
    # On dit au menu principal de rouvrir l'onglet "Échelles"
    st.session_state["target_tab"] = "🛠️ Outils & Exos"
    st.switch_page("streamlit_app.py")