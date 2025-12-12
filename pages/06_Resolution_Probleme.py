import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Résolution de Problèmes", page_icon="💡")

# --- VIGILE DE SÉCURITÉ ---
if "authentifie" not in st.session_state or not st.session_state.authentifie:
    st.warning("🔒 Accès restreint. Veuillez entrer votre Code Patient sur l'accueil.")
    st.page_link("streamlit_app.py", label="Retourner à l'accueil", icon="🏠")
    st.stop()

# Récupération sécurisée de l'ID
CURRENT_USER_ID = st.session_state.get("user_id", "")
if not CURRENT_USER_ID:
    CURRENT_USER_ID = st.session_state.get("patient_id", "")

if not CURRENT_USER_ID:
    st.error("Erreur d'identité. Veuillez vous reconnecter.")
    st.stop()

# Verrouillage des données (Système Anti-Fuite)
if "pb_owner" not in st.session_state or st.session_state.pb_owner != CURRENT_USER_ID:
    if "data_problemes" in st.session_state: del st.session_state.data_problemes
    st.session_state.pb_owner = CURRENT_USER_ID

st.title("💡 Technique de Résolution de Problèmes")
st.info("Une méthode structurée pour transformer un problème en plan d'action.")

# --- 0. INITIALISATION ET CHARGEMENT ---

# A. CHARGEMENT DE L'HISTORIQUE
cols_pb = ["Patient", "Date", "Problème", "Objectif", "Solution Choisie", "Plan Action", "Obstacles", "Ressources", "Date Évaluation"]

if "data_problemes" not in st.session_state:
    df_final = pd.DataFrame(columns=cols_pb)
    try:
        from connect_db import load_data
        data_cloud = load_data("Résolution_Problème")
        if data_cloud:
            df_cloud = pd.DataFrame(data_cloud)
            for col in cols_pb:
                if col in df_cloud.columns:
                    df_final[col] = df_cloud[col]
                elif col.lower() in df_cloud.columns:
                    df_final[col] = df_cloud[col.lower()]
                elif col.replace(" ", "_") in df_cloud.columns:
                    df_final[col] = df_cloud[col.replace(" ", "_")]
            
            # FILTRE SÉCURITÉ
            if "Patient" in df_final.columns:
                df_final = df_final[df_final["Patient"].astype(str) == str(CURRENT_USER_ID)]
            else:
                df_final = pd.DataFrame(columns=cols_pb)

    except: pass
    st.session_state.data_problemes = df_final

# B. Mémoires temporaires
if "analyse_detaillee" not in st.session_state:
    st.session_state.analyse_detaillee = pd.DataFrame(columns=["Solution", "Type", "Terme", "Description", "Note", "Valeur"])
if "liste_solutions_temp" not in st.session_state:
    st.session_state.liste_solutions_temp = []
if "plan_etapes_temp" not in st.session_state:
    st.session_state.plan_etapes_temp = []

# --- CRÉATION DES ONGLETS ---
tab1, tab2 = st.tabs(["💡 Méthode (Saisie)", "📊 Historique & Actions"])

# ==============================================================================
# ONGLET 1 : LA MÉTHODE COMPLÈTE
# ==============================================================================
with tab1:
    st.markdown("### 1. Stop & Attitude Constructive")
    with st.expander("🛑 Lire les consignes", expanded=False):
        st.markdown("**1. Stop :** Réaliser qu'on a un problème.\n**2. Attitude :** Voir le problème comme un défi.")
    st.divider()

    # 1. DÉFINITION
    st.markdown("### 1. Définition")
    probleme = st.text_area("Quel est le problème ?", placeholder="Qui ? Quoi ? Où ? Quand ?")
    st.markdown("### 2. Objectifs")
    objectif = st.text_area("Mon objectif réaliste :")
    st.divider()

    # 2. BRAINSTORMING
    st.markdown("### 3. Recherche de solutions")
    with st.form("ajout_solution_form", clear_on_submit=True):
        c_in, c_btn = st.columns([4, 1])
        with c_in: new_sol = st.text_input("Nouvelle solution :", label_visibility="collapsed")
        with c_btn: sub_add = st.form_submit_button("Ajouter")
        if sub_add and new_sol:
            st.session_state.liste_solutions_temp.append(new_sol)
            st.rerun()

    if st.session_state.liste_solutions_temp:
        st.write("---")
        for i, sol in enumerate(st.session_state.liste_solutions_temp):
            c_txt, c_del = st.columns([5, 1])
            c_txt.markdown(f"**{i+1}.** {sol}")
            if c_del.button("🗑️", key=f"del_sol_{i}"):
                st.session_state.liste_solutions_temp.pop(i)
                st.rerun()
    
    st.divider()

    # 3. ANALYSE
    st.markdown("### 4. Analyse Avantages / Inconvénients")
    if len(st.session_state.liste_solutions_temp) > 0:
        with st.form("ajout_argument_form", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            with c1: sol_sel = st.selectbox("Solution", st.session_state.liste_solutions_temp)
            with c2: type_p = st.selectbox("Type", ["Avantage (+)", "Inconvénient (-)"])
            with c3: terme = st.selectbox("Échéance", ["Court terme", "Moyen terme", "Long terme"])
            
            c4, c5 = st.columns([3, 1])
            with c4: desc = st.text_input("Description")
            with c5: note = st.number_input("Note (0-10)", 0, 10, 5)
            
            if st.form_submit_button("Ajouter argument"):
                val = note if "Avantage" in type_p else -note
                new_entry = {"Solution": sol_sel, "Type": type_p, "Terme": terme, "Description": desc, "Note": note, "Valeur": val}
                st.session_state.analyse_detaillee = pd.concat([st.session_state.analyse_detaillee, pd.DataFrame([new_entry])], ignore_index=True)
                st.success("Ajouté !")
                
        if not st.session_state.analyse_detaillee.empty:
            st.dataframe(st.session_state.analyse_detaillee)

    st.divider()

    # 4. DÉCISION & PLAN
    st.markdown("### 5. Décision finale")
    if st.session_state.liste_solutions_temp:
        sol_ret = st.multiselect("Je choisis :", st.session_state.liste_solutions_temp)
        solution_choisie = ", ".join(sol_ret)
    else:
        solution_choisie = st.text_input("Je décide de :")

    st.markdown("### 6. Préparation")
    c1, c2 = st.columns(2)
    with c1: obstacles = st.text_area("Obstacles possibles")
    with c2: ressources = st.text_area("Ressources nécessaires")

    st.divider()

    # PLAN D'ACTION
    st.markdown("### 7. Plan d'action détaillé")
    with st.form("ajout_etape_form", clear_on_submit=True):
        c_s, c_d, c_h = st.columns([3, 1, 1])
        with c_s: desc_e = st.text_input("Description étape")
        with c_d: date_e = st.date_input("Date", datetime.now())
        with c_h: heure_e = st.time_input("Heure", datetime.now().time())
        
        if st.form_submit_button("Ajouter étape"):
            etape_str = f"• {date_e.strftime('%d/%m')} à {heure_e.strftime('%H:%M')} : {desc_e}"
            st.session_state.plan_etapes_temp.append(etape_str)
            st.rerun()

    if st.session_state.plan_etapes_temp:
        for i, et in enumerate(st.session_state.plan_etapes_temp):
            c_t, c_d = st.columns([5, 1])
            c_t.text(et)
            if c_d.button("x", key=f"del_step_{i}"):
                st.session_state.plan_etapes_temp.pop(i)
                st.rerun()

    st.divider()

    # VALIDATION
    st.markdown("### 8. Évaluation")
    with st.form("validation_finale"):
        date_eval = st.date_input("Date bilan", datetime.now() + timedelta(days=7))
        if st.form_submit_button("💾 ENREGISTRER LE PLAN"):
            plan_txt = "\n".join(st.session_state.plan_etapes_temp)
            new_row = {
                "Patient": CURRENT_USER_ID,
                "Date": datetime.now().strftime("%Y-%m-%d"),
                "Problème": probleme, "Objectif": objectif, "Solution Choisie": solution_choisie,
                "Plan Action": plan_txt, "Obstacles": obstacles, "Ressources": ressources, "Date Évaluation": str(date_eval)
            }
            st.session_state.data_problemes = pd.concat([st.session_state.data_problemes, pd.DataFrame([new_row])], ignore_index=True)
            
            try:
                from connect_db import save_data
                vals = [new_row[c] for c in cols_pb]
                save_data("Résolution_Problème", vals)
                st.success("Enregistré !")
            except: st.warning("Local seulement.")

# ==============================================================================
# ONGLET 2 : HISTORIQUE
# ==============================================================================
with tab2:
    st.header("🗂️ Historique")
    
    df_hist = st.session_state.data_problemes
    if "Patient" in df_hist.columns:
        df_hist = df_hist[df_hist["Patient"] == CURRENT_USER_ID]

    if not df_hist.empty:
        # AFFICHER "DOSSIER" AU LIEU DU CODE
        df_display = df_hist.copy()
        nom_dossier = CURRENT_USER_ID
        try:
            from connect_db import load_data
            infos = load_data("Codes_Patients")
            if infos:
                df_i = pd.DataFrame(infos)
                col_id = "Identifiant" if "Identifiant" in df_i.columns else "Commentaire"
                match = df_i[df_i["Code"] == CURRENT_USER_ID]
                if not match.empty: nom_dossier = match.iloc[0][col_id]
        except: pass
        
        df_display["Patient"] = nom_dossier

        st.dataframe(
            df_display.sort_values(by="Date", ascending=False),
            column_config={"Patient": st.column_config.TextColumn("Dossier")},
            use_container_width=True,
            hide_index=True
        )

        st.divider()
        st.subheader("🛠️ Modifier / Supprimer")
        
        # SÉLECTEUR
        df_sorted = df_hist.sort_values(by="Date", ascending=False)
        opts = {f"{r['Date']} | {str(r['Problème'])[:40]}...": i for i, r in df_sorted.iterrows()}
        sel = st.selectbox("Choisir :", list(opts.keys()), index=None)

        if sel:
            idx = opts[sel]
            row = df_hist.loc[idx]
            
            c_edit, c_del = st.columns([1, 1])
            with c_del:
                if st.button("🗑️ Supprimer"):
                    try:
                        from connect_db import delete_data_flexible
                        delete_data_flexible("Résolution_Problème", {
                            "Patient": CURRENT_USER_ID, "Date": str(row["Date"]), "Problème": str(row["Problème"])
                        })
                    except: pass
                    st.session_state.data_problemes = df_hist.drop(idx).reset_index(drop=True)
                    st.success("Supprimé !")
                    st.rerun()

            with st.expander("✏️ Modifier", expanded=True):
                with st.form("edit_form"):
                    e_prob = st.text_area("Problème", value=row["Problème"])
                    e_obj = st.text_area("Objectif", value=row["Objectif"])
                    e_sol = st.text_input("Solution", value=row["Solution Choisie"])
                    e_plan = st.text_area("Plan Action", value=row["Plan Action"], height=150)
                    
                    if st.form_submit_button("Valider"):
                        # Suppression ancien
                        try:
                            from connect_db import delete_data_flexible, save_data
                            delete_data_flexible("Résolution_Problème", {
                                "Patient": CURRENT_USER_ID, "Date": str(row["Date"]), "Problème": str(row["Problème"])
                            })
                            # Création nouveau
                            upd_row = row.to_dict()
                            upd_row.update({"Problème": e_prob, "Objectif": e_obj, "Solution Choisie": e_sol, "Plan Action": e_plan})
                            save_data("Résolution_Problème", [upd_row[c] for c in cols_pb])
                        except: pass
                        
                        # Update Local
                        st.session_state.data_problemes.loc[idx, "Problème"] = e_prob
                        st.session_state.data_problemes.loc[idx, "Objectif"] = e_obj
                        st.session_state.data_problemes.loc[idx, "Solution Choisie"] = e_sol
                        st.session_state.data_problemes.loc[idx, "Plan Action"] = e_plan
                        st.success("Modifié !")
                        st.rerun()
    else:
        st.info("Aucun historique.")

st.divider()
st.page_link("streamlit_app.py", label="Retour à l'accueil", icon="🏠")