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

# Mémoire pour l'analyse détaillée (Pros/Cons)
if "analyse_detaillee" not in st.session_state:
    st.session_state.analyse_detaillee = pd.DataFrame(columns=[
        "Solution", "Type", "Terme", "Description", "Note", "Valeur"
    ])

# --- LE FORMULAIRE ---
with st.form("problem_solving_form"):
    
    # 1. & 2. ATTITUDE & DÉFINITION
    st.markdown("### 1. Définition du problème")
    [cite_start]st.caption("Définissez le problème de façon précise. [cite: 7-8]")
    probleme = st.text_area("Quel est le problème ?", placeholder="Qui ? Quoi ? Où ? Quand ?")
    
    # 3. OBJECTIFS
    st.markdown("### 2. Objectifs")
    objectif = st.text_area("Mon objectif réaliste :")

    st.divider()

    # 4. SOLUTIONS (Brainstorming)
    st.markdown("### 3. Recherche de solutions")
    [cite_start]st.caption("Listez vos solutions une par ligne. [cite: 13-15]")
    # On demande une solution par ligne pour pouvoir les détecter
    solutions_text = st.text_area("Vos idées (Une par ligne) :", height=100)
    
    # On transforme le texte en liste pour l'étape suivante
    liste_solutions = [s.strip() for s in solutions_text.split('\n') if s.strip()]

    st.divider()

    # ==============================================================================
    # 5. ANALYSE AVANCÉE (Calculateur)
    # ==============================================================================
    st.markdown("### 4. Analyse Avantages / Inconvénients")
    [cite_start]st.write("Analysez vos solutions pour trouver la meilleure. [cite: 19-21]")

    if len(liste_solutions) > 0:
        # --- A. AJOUTER UN POINT ---
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
            desc_point = st.text_input("Description (Ex: Coûte cher, Soulage vite...)")
        with c_note:
            note_point = st.number_input("Importance (0-10)", 0, 10, 5, help="0=Négligeable, 10=Crucial")

        # Bouton pour ajouter la ligne (Technique : on utilise un bouton hors du submit final)
        if st.form_submit_button("Ajouter cet argument au tableau"):
            # Calcul de la valeur (+ ou -)
            valeur = note_point if type_point == "Avantage (+)" else -note_point
            
            new_entry = {
                "Solution": sol_selected,
                "Type": type_point,
                "Terme": terme,
                "Description": desc_point,
                "Note": note_point,
                "Valeur": valeur
            }
            st.session_state.analyse_detaillee = pd.concat(
                [st.session_state.analyse_detaillee, pd.DataFrame([new_entry])], 
                ignore_index=True
            )
            st.success("Argument ajouté !")

        # --- B. TABLEAU RÉCAPITULATIF & SCORE ---
        if not st.session_state.analyse_detaillee.empty:
            st.divider()
            st.markdown("#### 📊 Comparatif des solutions")
            
            # 1. Calcul des scores par solution
            df_analyse = st.session_state.analyse_detaillee
            # On groupe par solution et on somme les 'Valeurs'
            scores = df_analyse.groupby("Solution")["Valeur"].sum().reset_index()
            scores = scores.sort_values(by="Valeur", ascending=False) # Le meilleur en haut
            
            # Affichage du podium
            st.dataframe(scores.set_index("Solution"), use_container_width=True)
            
            # Affichage du détail complet
            with st.expander("Voir le détail de tous les arguments"):
                st.dataframe(df_analyse[["Solution", "Type", "Terme", "Description", "Note"]], use_container_width=True)
            
            # Suggestion automatique
            meilleure_sol = scores.iloc[0]["Solution"]
            st.success(f"💡 D'après votre analyse, la solution recommandée est : **{meilleure_sol}** (Score: {scores.iloc[0]['Valeur']})")

    else:
        st.info("👆 Commencez par lister des solutions à l'étape 3 pour pouvoir les analyser.")

    st.divider()

    # ==============================================================================
    # SUITE DU FORMULAIRE CLASSIQUE
    # ==============================================================================

    # 6. CHOIX
    st.markdown("### 5. Décision finale")
    [cite_start]st.caption("Quelle solution choisissez-vous finalement ? [cite: 22-23]")
    # On pré-remplit éventuellement avec la meilleure solution calculée si possible, sinon libre
    solution_choisie = st.text_input("Je décide de mettre en œuvre :")

    # 7. OBSTACLES & RESSOURCES
    st.markdown("### 6. Préparation")
    c1, c2 = st.columns(2)
    with c1:
        obstacles = st.text_area("Obstacles possibles")
    with c2:
        ressources = st.text_area("Ressources nécessaires")

    st.divider()

    # 8. PLAN D'ACTION
    st.markdown("### 7. Plan d'action")
    [cite_start]st.caption("Étapes concrètes et dates. [cite: 26-30]")
    plan = st.text_area("Mon plan détaillé :", height=100)

    # 9. EVALUATION
    st.markdown("### 8. Évaluation future")
    [cite_start]st.caption("Date pour faire le bilan. [cite: 32-34]")
    date_eval = st.date_input("Date de bilan", datetime.now() + timedelta(days=7))

    # --- BOUTON FINAL ---
    submitted_final = st.form_submit_button("💾 ENREGISTRER MON PLAN D'ACTION")

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
        
        # Optionnel : On vide la table d'analyse pour le prochain problème
        # st.session_state.analyse_detaillee = pd.DataFrame(columns=["Solution", "Type", "Terme", "Description", "Note", "Valeur"])
        
        st.success("Plan enregistré avec succès ! Vous pouvez le retrouver dans l'Historique.")

st.divider()
if st.button("⬅️ Retour Accueil"):
    st.switch_page("streamlit_app.py")