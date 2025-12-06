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

if "analyse_detaillee" not in st.session_state:
    st.session_state.analyse_detaillee = pd.DataFrame(columns=[
        "Solution", "Type", "Terme", "Description", "Note", "Valeur"
    ])

if "liste_solutions_temp" not in st.session_state:
    st.session_state.liste_solutions_temp = []

# NOUVEAU : Mémoire pour les étapes du plan d'action
if "plan_etapes_temp" not in st.session_state:
    st.session_state.plan_etapes_temp = []

# ==============================================================================
# BLOC 0 : STOP & ATTITUDE (AJOUTÉ)
# ==============================================================================
st.markdown("### 1. Stop & Attitude Constructive")

with st.expander("🛑 Lire les consignes de départ (Important)", expanded=True):
    st.markdown("""
    **1. Stop :**
    On doit d’abord réaliser que l’on a un problème qui n’est pas facile à résoudre et mérite qu’on prenne un peu de temps pour bien y réfléchir. 
    
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
# BLOC 4 : DÉCISION & PLAN D'ACTION (NOUVEAU SYSTÈME ÉTAPE PAR ÉTAPE)
# ==============================================================================
st.markdown("### 5. Décision finale")
solution_choisie = st.text_input("Je décide de mettre en œuvre :", placeholder="La solution que vous avez choisie...")

st.markdown("### 6. Préparation")
c1, c2 = st.columns(2)
with c1: obstacles = st.text_area("Obstacles possibles")
with c2: ressources = st.text_area("Ressources nécessaires")

st.divider()

# --- NOUVEAU : PLAN D'ACTION PAR ÉTAPES ---
st.markdown("### 7. Plan d'action détaillé")
st.caption("Déterminez les étapes par lesquelles vous devez passer pour appliquer la solution choisie. Faites un plan détaillé, avec un échéancier précis et réaliste. Veillez à ce que la première étape soit assez facile et passez à l’action rapidement et si possible immédiatement. Un premier pas même tout petit vous donnera le sentiment d’avoir « brisé la glace ». ")

# Formulaire d'ajout d'étape
with st.form("ajout_etape_form", clear_on_submit=True):
    c_step, c_date = st.columns([3, 1])
    with c_step:
        desc_etape = st.text_input("Description de l'étape", placeholder="Ex: Appeler M. Dupont")
    with c_date:
        date_etape = st.date_input("Date prévue", datetime.now())
    
    if st.form_submit_button("Ajouter cette étape"):
        # On ajoute l'étape à la liste en mémoire
        etape_str = f"• {date_etape.strftime('%d/%m')} : {desc_etape}"
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
# BLOC FINAL : VALIDATION
# ==============================================================================
st.markdown("### 8. Évaluation")
with st.form("validation_finale"):
    date_eval = st.date_input("Date de bilan des résultats", datetime.now() + timedelta(days=7))
    
    submitted_final = st.form_submit_button("💾 ENREGISTRER LE PLAN D'ACTION")

    if submitted_final:
        # On transforme la liste des étapes en un seul texte pour la sauvegarde
        plan_texte_complet = "\n".join(st.session_state.plan_etapes_temp)
        
        new_row = {
            "Date": datetime.now().strftime("%Y-%m-%d"),
            "Problème": probleme, "Objectif": objectif, "Solution Choisie": solution_choisie,
            "Plan Action": plan_texte_complet, # On sauve la liste compilée
            "Obstacles": obstacles, "Ressources": ressources, "Date Évaluation": str(date_eval)
        }
        
        st.session_state.data_problemes = pd.concat([st.session_state.data_problemes, pd.DataFrame([new_row])], ignore_index=True)
        
        # Cloud
        from connect_db import save_data
        patient = st.session_state.get("patient_id", "Inconnu")
        save_data("Plans_Action", [patient, datetime.now().strftime("%Y-%m-%d"), probleme, objectif, solution_choisie, plan_texte_complet, obstacles, ressources, str(date_eval)])
        
        # Nettoyage de toutes les mémoires temporaires
        st.session_state.analyse_detaillee = pd.DataFrame(columns=["Solution", "Type", "Terme", "Description", "Note", "Valeur"])
        st.session_state.liste_solutions_temp = [] 
        st.session_state.plan_etapes_temp = [] 
        
        st.success("Plan enregistré avec succès ! Retrouvez-le dans l'Historique.")

st.divider()
st.page_link("streamlit_app.py", label="Retour à l'accueil", icon="🏠")