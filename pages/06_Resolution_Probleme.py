import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Résolution de Problèmes", page_icon="💡")

st.title("💡 Technique de Résolution de Problèmes")
st.info("Une méthode structurée pour transformer un problème en plan d'action.")

# --- INITIALISATION MÉMOIRE ---
if "data_problemes" not in st.session_state:
    st.session_state.data_problemes = pd.DataFrame(columns=[
        "Date", "Problème", "Objectif", "Solution Choisie", "Date Évaluation"
    ])

# --- LE FORMULAIRE ---
with st.form("problem_solving_form"):
    
    # 1. STOP & ATTITUDE
    st.markdown("### 1. Attitude Constructive")
    st.write("🛑 **STOP !** Prenez un moment. Voyez ce problème comme un **défi** ou une occasion d'apprendre plutôt que comme une menace.")
    
    st.divider()

    # 2. DÉFINIR
    st.markdown("### 2. Définir le problème")
    st.caption("Définissez le problème de façon précise, concrète et délimitée.")
    probleme = st.text_area("Quel est le problème ? (Quoi ? Qui ? Où ? Quand ?)", help="Évitez le vague. Si plusieurs problèmes, choisissez le plus urgent.")
    
    # 3. OBJECTIFS
    st.markdown("### 3. Objectifs")
    st.caption("Quels seraient les signes concrets que l'objectif est atteint ?")
    objectif = st.text_area("Mon objectif réaliste :")

    st.divider()

    # 4. SOLUTIONS (Brainstorming)
    st.markdown("### 4. Solutions possibles")
    st.caption("Dressez la liste de TOUTES les solutions possibles. Ne jugez pas encore !")
    solutions = st.text_area("Toutes mes idées (même les farfelues) :")

    # 5. ANALYSE
    with st.expander("⚖️ Étape 5 : Analyser Avantages / Inconvénients"):
        st.write("Pour les meilleures solutions, pesez le pour et le contre (court et long terme).")
        analyse = st.text_area("Vos notes d'analyse :")

    st.divider()

    # 6. CHOIX
    st.markdown("### 6. Décision")
    st.caption("Choisissez une solution. Acceptez qu'elle ne soit pas parfaite (accepter les inconvénients).")
    solution_choisie = st.text_input("La solution que je retiens :")

    # 7. OBSTACLES & RESSOURCES
    st.markdown("### 7. Préparation")
    st.caption("Identifiez ce qui pourrait bloquer et ce qui peut aider.")
    c1, c2 = st.columns(2)
    with c1:
        obstacles = st.text_area("Obstacles possibles")
    with c2:
        ressources = st.text_area("Ressources nécessaires")

    st.divider()

    # 8. PLAN D'ACTION
    st.markdown("### 8. Plan d'action")
    st.caption("Étapes concrètes et dates. La 1ère étape doit être facile !")
    plan = st.text_area("Mon plan détaillé (Quoi et Quand) :", height=150, placeholder="1. Faire ceci le...\n2. Appeler untel le...")

    # 9. EVALUATION
    st.markdown("### 9. Évaluation future")
    st.caption("Quand évaluerez-vous les résultats ?")
    date_eval = st.date_input("Date de bilan", datetime.now() + timedelta(days=7))

    submitted = st.form_submit_button("Enregistrer le Plan d'Action")

    if submitted:
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
        st.success("Plan enregistré ! Passez à l'action maintenant !")

st.divider()
st.page_link("streamlit_app.py", label="Retour à l'accueil", icon="🏠")