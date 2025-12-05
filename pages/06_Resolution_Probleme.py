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

if "analyse_detaillee" not in st.session_state:
    st.session_state.analyse_detaillee = pd.DataFrame(columns=[
        "Solution", "Type", "Terme", "Description", "Note", "Valeur"
    ])

# --- LE FORMULAIRE ---
with st.form("problem_solving_form"):
    
    st.markdown("### 1. Définition du problème")
    probleme = st.text_area("Quel est le problème ?", placeholder="Qui ? Quoi ? Où ? Quand ?")
    
    st.markdown("### 2. Objectifs")
    objectif = st.text_area("Mon objectif réaliste :")

    st.divider()

    st.markdown("### 3. Recherche de solutions")
    st.caption("Listez vos solutions une par ligne.")
    solutions_text = st.text_area("Vos idées (Une par ligne) :", height=100)
    liste_solutions = [s.strip() for s in solutions_text.split('\n') if s.strip()]

    st.divider()

    # --- CALCULATEUR AVANTAGES / INCONVENIENTS ---
    st.markdown("### 4. Analyse Avantages / Inconvénients")
    
    if len(liste_solutions) > 0:
        st.markdown("#### ➕ Ajouter un argument")
        c_sol, c_type, c_term = st.columns(3)
        with c_sol:
            sol_selected = st.selectbox("Pour quelle solution ?", liste_solutions)
        with c_type:
            type_point = st.selectbox("Type", ["Avantage (+)", "Inconvénient (-)"])
        with c_term:
            terme = st.selectbox("Échéance", ["Court terme", "Moyen terme", "Long terme"])
        
        c_desc, c_note = st.columns([3, 1])
        with c_desc:
            desc_point = st.text_input("Description (Ex: Coûte cher...)")
        with c_note:
            note_point = st.number_input("Note (0-10)", 0, 10, 5)

        # Bouton intermédiaire pour ajouter l'argument sans valider tout le formulaire
        if st.form_submit_button("Ajouter cet argument"):
            valeur = note_point if type_point == "Avantage (+)" else -note_point
            new_entry = {
                "Solution": sol_selected, "Type": type_point, "Terme": terme,
                "Description": desc_point, "Note": note_point, "Valeur": valeur
            }
            st.session_state.analyse_detaillee = pd.concat(
                [st.session_state.analyse_detaillee, pd.DataFrame([new_entry])], ignore_index=True
            )
            st.success("Argument ajouté !")

        # Affichage du tableau comparatif
        if not st.session_state.analyse_detaillee.empty:
            st.markdown("#### 📊 Comparatif des solutions")
            df_analyse = st.session_state.analyse_detaillee
            scores = df_analyse.groupby("Solution")["Valeur"].sum().reset_index().sort_values(by="Valeur", ascending=False)
            
            st.dataframe(scores.set_index("Solution"), use_container_width=True)
            
            with st.expander("Voir le détail des arguments"):
                st.dataframe(df_analyse, use_container_width=True)
                # Petit bouton pour nettoyer si on s'est trompé
                if st.form_submit_button("Effacer l'analyse"):
                    st.session_state.analyse_detaillee = pd.DataFrame(columns=["Solution", "Type", "Terme", "Description", "Note", "Valeur"])
                    st.rerun()

    else:
        st.info("👆 Listez d'abord des solutions à l'étape 3.")

    st.divider()

    st.markdown("### 5. Décision finale")
    solution_choisie = st.text_input("Je décide de mettre en œuvre :")

    st.markdown("### 6. Plan d'action")
    plan = st.text_area("Mon plan détaillé :")

    st.markdown("### 7. Évaluation")
    date_eval = st.date_input("Date de bilan", datetime.now() + timedelta(days=7))

    # --- BOUTON FINAL ---
    submitted_final = st.form_submit_button("💾 ENREGISTRER LE PLAN")

    if submitted_final:
        new_row = {
            "Date": datetime.now().strftime("%Y-%m-%d"),
            "Problème": probleme, "Objectif": objectif,
            "Solution Choisie": solution_choisie, "Date Évaluation": str(date_eval)
        }
        st.session_state.data_problemes = pd.concat(
            [st.session_state.data_problemes, pd.DataFrame([new_row])], ignore_index=True
        )
        st.success("Plan enregistré !")

st.divider()
# Bouton compatible ancienne version
if st.button("⬅️ Retour Accueil"):
    st.switch_page("streamlit_app.py")