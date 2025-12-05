import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Résolution de Problèmes", page_icon="💡")

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

# ==============================================================================
# BLOC 1 : DÉFINITION & BRAINSTORMING (Interactif)
# ==============================================================================
st.markdown("### 1. Définition")
[cite_start]st.caption("Définissez le problème de façon précise. [cite: 180-181]"),
probleme = st.text_area("Quel est le problème ?", placeholder="Qui ? Quoi ? Où ? Quand ?")

st.markdown("### 2. Objectifs")
[cite_start]st.caption("Quels seraient les signes concrets que l'objectif est atteint ? [cite: 184-185]"),
objectif = st.text_area("Mon objectif réaliste :")

st.divider()

st.markdown("### 3. Recherche de solutions")
[cite_start]st.caption("Listez vos solutions une par ligne. [cite: 186-187]"),

# Astuce : On sort ce champ du formulaire pour que Streamlit le lise en direct
solutions_text = st.text_area("Vos idées (Une par ligne) :", height=100, help="Écrivez une idée, appuyez sur Entrée, écrivez la suivante...")

# Transformation immédiate du texte en liste
liste_solutions = [s.strip() for s in solutions_text.split('\n') if s.strip()]

st.divider()

# ==============================================================================
# BLOC 2 : ANALYSE (LE CALCULATEUR)
# ==============================================================================
st.markdown("### 4. Analyse Avantages / Inconvénients")

if len(liste_solutions) > 0:
    [cite_start]st.write("Pour chaque solution, ajoutez des arguments 'Pour' ou 'Contre'. [cite: 192-194]"),
    
    # On met l'ajout d'argument dans son propre petit formulaire pour être propre
    with st.form("ajout_argument_form", clear_on_submit=True):
        st.write("**Ajouter un argument :**")
        c_sol, c_type, c_term = st.columns(3)
        with c_sol:
            sol_selected = st.selectbox("Solution concernée", liste_solutions)
        with c_type:
            type_point = st.selectbox("Type", ["Avantage (+)", "Inconvénient (-)"])
        with c_term:
            terme = st.selectbox("Échéance", ["Court terme", "Moyen terme", "Long terme"])
        
        c_desc, c_note = st.columns([3, 1])
        with c_desc:
            desc_point = st.text_input("Description (Ex: Coûte cher...)")
        with c_note:
            note_point = st.number_input("Importance (0-10)", 0, 10, 5)

        # Ce bouton ne valide que ce petit bloc
        submit_arg = st.form_submit_button("➕ Ajouter l'argument")
        
        if submit_arg:
            valeur = note_point if "Avantage" in type_point else -note_point
            new_entry = {
                "Solution": sol_selected, "Type": type_point, "Terme": terme,
                "Description": desc_point, "Note": note_point, "Valeur": valeur
            }
            st.session_state.analyse_detaillee = pd.concat(
                [st.session_state.analyse_detaillee, pd.DataFrame([new_entry])], 
                ignore_index=True
            )
            st.success("Ajouté !")

    # Affichage des résultats (se met à jour tout seul dès qu'on ajoute un argument)
    if not st.session_state.analyse_detaillee.empty:
        st.markdown("#### 📊 Résultats de l'analyse")
        df_analyse = st.session_state.analyse_detaillee
        
        # Calcul des scores
        scores = df_analyse.groupby("Solution")["Valeur"].sum().reset_index()
        scores = scores.sort_values(by="Valeur", ascending=False)
        
        # Le Podium
        st.dataframe(scores.set_index("Solution"), use_container_width=True)
        
        # Le Détail
        with st.expander("Voir le détail des arguments"):
            st.dataframe(df_analyse, use_container_width=True)
            if st.button("🗑️ Tout effacer pour recommencer l'analyse"):
                st.session_state.analyse_detaillee = pd.DataFrame(columns=["Solution", "Type", "Terme", "Description", "Note", "Valeur"])
                st.rerun()
else:
    st.info("👆 Remplissez la case 'Vos idées' à l'étape 3 pour activer l'analyse.")

st.divider()

# ==============================================================================
# BLOC 3 : DÉCISION & PLAN (Formulaire final de sauvegarde)
# ==============================================================================
with st.form("plan_final_form"):
    st.markdown("### 5. Décision finale")
    [cite_start]st.caption("Quelle solution choisissez-vous finalement ? [cite: 195-196]"),
    solution_choisie = st.text_input("Je décide de mettre en œuvre :")

    st.markdown("### 6. Préparation")
    c1, c2 = st.columns(2)
    with c1: obstacles = st.text_area("Obstacles possibles")
    with c2: ressources = st.text_area("Ressources nécessaires")

    st.markdown("### 7. Plan d'action")
    [cite_start]st.caption("Étapes concrètes et dates. [cite: 199-202]"),
    plan = st.text_area("Mon plan détaillé :", height=100)

    st.markdown("### 8. Évaluation")
    date_eval = st.date_input("Date de bilan", datetime.now() + timedelta(days=7))

    # --- BOUTON DE SAUVEGARDE GLOBALE ---
    submitted_final = st.form_submit_button("💾 ENREGISTRER LE PLAN D'ACTION")

    if submitted_final:
        new_row = {
            "Date": datetime.now().strftime("%Y-%m-%d"),
            "Problème": probleme,
            "Objectif": objectif,
            "Solution Choisie": solution_choisie,
            "Date Évaluation": str(date_eval)
        }
        st.session_state.data_problemes = pd.concat(
            [st.session_state.data_problemes, pd.DataFrame([new_row])],
            ignore_index=True
        )
        # On vide l'analyse pour le prochain problème
        st.session_state.analyse_detaillee = pd.DataFrame(columns=["Solution", "Type", "Terme", "Description", "Note", "Valeur"])
        st.success("Plan enregistré ! Retrouvez-le dans l'Historique.")

st.divider()
st.page_link("streamlit_app.py", label="Retour à l'accueil", icon="🏠")