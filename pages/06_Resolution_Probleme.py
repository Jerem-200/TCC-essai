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
st.info("Une méthode structurée pour transformer un problème en plan d'action.")

# --- 0. INITIALISATION DES MÉMOIRES ---
if "data_problemes" not in st.session_state:
    st.session_state.data_problemes = pd.DataFrame(columns=[
        "Date", "Problème", "Objectif", "Solution Choisie", "Date Évaluation"
    ])

# Mémoire pour l'analyse (Tableau Avantages/Inconvénients)
if "analyse_detaillee" not in st.session_state:
    st.session_state.analyse_detaillee = pd.DataFrame(columns=[
        "Solution", "Type", "Terme", "Description", "Note", "Valeur"
    ])

# NOUVEAU : Mémoire pour la liste des solutions (Brainstorming)
if "liste_solutions_temp" not in st.session_state:
    st.session_state.liste_solutions_temp = []

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
# BLOC 2 : BRAINSTORMING INTERACTIF (NOUVEAU SYSTÈME)
# ==============================================================================
st.markdown("### 3. Recherche de solutions")
st.caption("Ajoutez toutes vos idées une par une, sans les juger.")

col_input, col_btn = st.columns([4, 1])

# On utilise un petit formulaire pour que "Entrée" valide l'ajout
with st.form("ajout_solution_form", clear_on_submit=True):
    nouvelle_solution = st.text_input("Nouvelle solution :", placeholder="Ex: Demander de l'aide...")
    submitted_ajout = st.form_submit_button("Ajouter")
    
    if submitted_ajout and nouvelle_solution:
        st.session_state.liste_solutions_temp.append(nouvelle_solution)
        st.rerun() # On recharge pour afficher la liste mise à jour

# Affichage de la liste actuelle
if st.session_state.liste_solutions_temp:
    st.write("---")
    st.write("**Vos idées listées :**")
    for i, sol in enumerate(st.session_state.liste_solutions_temp):
        st.markdown(f"**{i+1}.** {sol}")
    
    col_clear, col_valid = st.columns([1, 2])
    with col_clear:
        if st.button("🗑️ Tout effacer"):
            st.session_state.liste_solutions_temp = []
            st.rerun()
else:
    st.info("Votre liste est vide pour l'instant.")

st.divider()

# ==============================================================================
# BLOC 3 : ANALYSE (ACTIVÉ SI LISTE NON VIDE)
# ==============================================================================
st.markdown("### 4. Analyse Avantages / Inconvénients")

# On vérifie qu'il y a des solutions dans la liste mémoire
if len(st.session_state.liste_solutions_temp) > 0:
    st.write("Pour chaque solution, ajoutez des arguments 'Pour' ou 'Contre'.")
    
    with st.form("ajout_argument_form", clear_on_submit=True):
        c_sol, c_type, c_term = st.columns(3)
        with c_sol:
            # On utilise la liste mémoire ici !
            sol_selected = st.selectbox("Solution", st.session_state.liste_solutions_temp)
        with c_type:
            type_point = st.selectbox("Type", ["Avantage (+)", "Inconvénient (-)"])
        with c_term:
            terme = st.selectbox("Échéance", ["Court terme", "Moyen terme", "Long terme"])
        
        c_desc, c_note = st.columns([3, 1])
        with c_desc:
            desc_point = st.text_input("Description")
        with c_note:
            note_point = st.number_input("Importance (0-10)", 0, 10, 5)

        if st.form_submit_button("➕ Ajouter l'argument"):
            valeur = note_point if "Avantage" in type_point else -note_point
            new_entry = {"Solution": sol_selected, "Type": type_point, "Terme": terme, "Description": desc_point, "Note": note_point, "Valeur": valeur}
            st.session_state.analyse_detaillee = pd.concat([st.session_state.analyse_detaillee, pd.DataFrame([new_entry])], ignore_index=True)
            st.success("Ajouté !")

    # Tableau comparatif
    if not st.session_state.analyse_detaillee.empty:
        st.divider()
        st.markdown("#### 📊 Tableau Comparatif")
        
        df = st.session_state.analyse_detaillee
        rows_display = []
        
        for sol in df["Solution"].unique():
            pros = df[(df["Solution"] == sol) & (df["Type"].str.contains("Avantage"))]
            pros_text = "\n".join([f"- {r['Description']} ({r['Note']}/10)" for i, r in pros.iterrows()])
            pros_score = pros["Note"].sum()
            
            cons = df[(df["Solution"] == sol) & (df["Type"].str.contains("Inconvénient"))]
            cons_text = "\n".join([f"- {r['Description']} ({r['Note']}/10)" for i, r in cons.iterrows()])
            cons_score = cons["Note"].sum()
            
            rows_display.append({
                "Solution": sol, "Avantages": pros_text, "Total (+)": pros_score,
                "Inconvénients": cons_text, "Total (-)": cons_score, "Bilan": pros_score - cons_score
            })
            
        df_display = pd.DataFrame(rows_display)
        st.table(df_display.set_index("Solution"))
        
        best_sol = df_display.loc[df_display["Bilan"].idxmax()]
        st.success(f"💡 Meilleure solution mathématique : **{best_sol['Solution']}** (Score : {best_sol['Bilan']})")

        if st.button("🗑️ Effacer l'analyse"):
            st.session_state.analyse_detaillee = pd.DataFrame(columns=["Solution", "Type", "Terme", "Description", "Note", "Valeur"])
            st.rerun()
else:
    st.info("👆 Ajoutez des solutions à l'étape 3 ci-dessus.")

st.divider()

# ==============================================================================
# BLOC 4 : DÉCISION & PLAN
# ==============================================================================
with st.form("plan_final_form"):
    st.markdown("### 5. Décision finale")
    st.caption("Quelle solution choisissez-vous finalement ?")
    solution_choisie = st.text_input("Je décide de mettre en œuvre :")

    st.markdown("### 6. Préparation")
    c1, c2 = st.columns(2)
    with c1: obstacles = st.text_area("Obstacles possibles")
    with c2: ressources = st.text_area("Ressources nécessaires")

    st.markdown("### 7. Plan d'action")
    st.caption("Étapes concrètes et dates.")
    plan = st.text_area("Mon plan détaillé :", height=100)

    st.markdown("### 8. Évaluation")
    date_eval = st.date_input("Date de bilan", datetime.now() + timedelta(days=7))

    submitted_final = st.form_submit_button("💾 ENREGISTRER LE PLAN D'ACTION")

    if submitted_final:
        new_row = {
            "Date": datetime.now().strftime("%Y-%m-%d"),
            "Problème": probleme, "Objectif": objectif, "Solution Choisie": solution_choisie,
            "Plan Action": plan, "Obstacles": obstacles, "Ressources": ressources, "Date Évaluation": str(date_eval)
        }
        st.session_state.data_problemes = pd.concat([st.session_state.data_problemes, pd.DataFrame([new_row])], ignore_index=True)
        
        # Cloud
        from connect_db import save_data
        patient = st.session_state.get("patient_id", "Inconnu")
        save_data("Plans_Action", [patient, datetime.now().strftime("%Y-%m-%d"), probleme, objectif, solution_choisie, plan, obstacles, ressources, str(date_eval)])
        
        # Nettoyage
        st.session_state.analyse_detaillee = pd.DataFrame(columns=["Solution", "Type", "Terme", "Description", "Note", "Valeur"])
        st.session_state.liste_solutions_temp = [] # On vide la liste aussi
        
        st.success("Plan enregistré ! Retrouvez-le dans l'Historique.")

st.divider()
st.page_link("streamlit_app.py", label="Retour à l'accueil", icon="🏠")