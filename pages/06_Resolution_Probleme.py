import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Résolution de Problèmes", page_icon="💡")

st.title("💡 Technique de Résolution de Problèmes")
st.info("Une méthode structurée pour transformer un problème en plan d'action.")

# --- 0. INITIALISATION DES MÉMOIRES (AVEC LES NOUVELLES COLONNES) ---
if "data_problemes" not in st.session_state:
    st.session_state.data_problemes = pd.DataFrame(columns=[
        "Date", "Problème", "Objectif", "Solution Choisie", 
        "Plan Action", "Obstacles", "Ressources", "Date Évaluation"
    ])

if "analyse_detaillee" not in st.session_state:
    st.session_state.analyse_detaillee = pd.DataFrame(columns=[
        "Solution", "Type", "Terme", "Description", "Note", "Valeur"
    ])

# ==============================================================================
# BLOC 1 : DÉFINITION & BRAINSTORMING
# ==============================================================================
st.markdown("### 1. Définition")
st.caption("Définissez le problème de façon précise.")
probleme = st.text_area("Quel est le problème ?", placeholder="Qui ? Quoi ? Où ? Quand ?")

st.markdown("### 2. Objectifs")
st.caption("Quels seraient les signes concrets que l'objectif est atteint ?")
objectif = st.text_area("Mon objectif réaliste :")

st.divider()

st.markdown("### 3. Recherche de solutions")
st.caption("Listez vos solutions une par ligne.")
solutions_text = st.text_area("Vos idées (Une par ligne) :", height=100)
liste_solutions = [s.strip() for s in solutions_text.split('\n') if s.strip()]

st.divider()

# ==============================================================================
# BLOC 2 : ANALYSE (CALCULATEUR)
# ==============================================================================
st.markdown("### 4. Analyse Avantages / Inconvénients")

if len(liste_solutions) > 0:
    st.write("Ajoutez des arguments pour construire le tableau comparatif.")
    
    with st.form("ajout_argument_form", clear_on_submit=True):
        c_sol, c_type, c_term = st.columns(3)
        with c_sol: sol_selected = st.selectbox("Solution", liste_solutions)
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
        df = st.session_state.analyse_detaillee
        
        # Construction du tableau comparatif
        rows_display = []
        for sol in df["Solution"].unique():
            pros = df[(df["Solution"] == sol) & (df["Type"].str.contains("Avantage"))]
            pros_text = "\n".join([f"- {row['Description']} ({row['Note']}/10)" for i, row in pros.iterrows()])
            pros_score = pros["Note"].sum()
            
            cons = df[(df["Solution"] == sol) & (df["Type"].str.contains("Inconvénient"))]
            cons_text = "\n".join([f"- {row['Description']} ({row['Note']}/10)" for i, row in cons.iterrows()])
            cons_score = cons["Note"].sum()
            
            rows_display.append({
                "Solution": sol, "Avantages": pros_text, "Total (+)": pros_score,
                "Inconvénients": cons_text, "Total (-)": cons_score, "Bilan": pros_score - cons_score
            })
            
        df_display = pd.DataFrame(rows_display)
        st.table(df_display.set_index("Solution"))
        
        best_sol = df_display.loc[df_display["Bilan"].idxmax()]
        st.success(f"💡 La solution qui semble être la meilleure est : **{best_sol['Solution']}** (Score : {best_sol['Bilan']})")

        if st.button("🗑️ Tout effacer"):
            st.session_state.analyse_detaillee = pd.DataFrame(columns=["Solution", "Type", "Terme", "Description", "Note", "Valeur"])
            st.rerun()
else:
    st.info("👆 Remplissez la case 'Vos idées' à l'étape 3.")

st.divider()

# ==============================================================================
# BLOC 3 : DÉCISION & PLAN
# ==============================================================================
with st.form("plan_final_form"):
    st.markdown("### 5. Décision finale")
    solution_choisie = st.text_input("Je décide de mettre en œuvre :")

    st.markdown("### 6. Préparation")
    c1, c2 = st.columns(2)
    with c1: obstacles = st.text_area("Obstacles possibles")
    with c2: ressources = st.text_area("Ressources nécessaires")

    st.markdown("### 7. Plan d'action")
    st.caption("Étapes concrètes et dates.")
    plan = st.text_area("Mon plan détaillé :", height=150)

    st.markdown("### 8. Évaluation")
    date_eval = st.date_input("Date de bilan", datetime.now() + timedelta(days=7))

    submitted_final = st.form_submit_button("💾 ENREGISTRER LE PLAN D'ACTION")

if submitted_final:
        # Local
        new_row = {
            "Date": datetime.now().strftime("%Y-%m-%d"),
            "Problème": probleme, "Objectif": objectif, "Solution Choisie": solution_choisie,
            "Plan Action": plan, "Obstacles": obstacles, "Ressources": ressources,
            "Date Évaluation": str(date_eval)
        }
        st.session_state.data_problemes = pd.concat([st.session_state.data_problemes, pd.DataFrame([new_row])], ignore_index=True)
        st.session_state.analyse_detaillee = pd.DataFrame(columns=["Solution", "Type", "Terme", "Description", "Note", "Valeur"])
        
        # CLOUD (Envoi vers l'onglet "Plans_Action")
        from connect_db import save_data
        ligne_excel = [
            datetime.now().strftime("%Y-%m-%d"),
            probleme, objectif, solution_choisie, 
            plan, obstacles, ressources, str(date_eval)
        ]
        
        if save_data("Plans_Action", ligne_excel):
            st.success("Plan enregistré dans le Cloud ! ☁️")
        else:
            st.warning("Sauvegarde locale uniquement.")

st.divider()
st.page_link("streamlit_app.py", label="Retour à l'accueil", icon="🏠")