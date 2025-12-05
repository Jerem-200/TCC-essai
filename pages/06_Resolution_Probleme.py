import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Résolution de Problèmes", page_icon="💡")
st.title("💡 Résolution de Problèmes")

if "data_problemes" not in st.session_state: st.session_state.data_problemes = pd.DataFrame()
if "analyse_detaillee" not in st.session_state: st.session_state.analyse_detaillee = pd.DataFrame(columns=["Solution", "Type", "Note", "Valeur"])

with st.form("pb_form"):
    st.markdown("### 1. Définir")
    pb = st.text_area("Problème")
    obj = st.text_area("Objectif")
    
    st.markdown("### 2. Solutions")
    sols = st.text_area("Idées (une par ligne)")
    liste_sols = [s.strip() for s in sols.split('\n') if s.strip()]
    
    st.markdown("### 3. Analyse")
    if liste_sols:
        c1, c2, c3 = st.columns(3)
        with c1: sel_sol = st.selectbox("Solution", liste_sols)
        with c2: sel_type = st.selectbox("Type", ["Avantage (+)", "Inconvénient (-)"])
        with c3: sel_note = st.number_input("Note (0-10)", 0, 10, 5)
        
        if st.form_submit_button("Ajouter argument"):
            val = sel_note if "Avantage" in sel_type else -sel_note
            st.session_state.analyse_detaillee = pd.concat([st.session_state.analyse_detaillee, pd.DataFrame([{"Solution": sel_sol, "Type": sel_type, "Note": sel_note, "Valeur": val}])], ignore_index=True)
            st.success("Ajouté !")
            
        if not st.session_state.analyse_detaillee.empty:
            scores = st.session_state.analyse_detaillee.groupby("Solution")["Valeur"].sum().reset_index().sort_values("Valeur", ascending=False)
            st.dataframe(scores, use_container_width=True)
            if st.form_submit_button("Effacer analyse"):
                st.session_state.analyse_detaillee = pd.DataFrame()
                st.rerun()
    
    st.markdown("### 4. Décision & Plan")
    choix = st.text_input("Solution retenue")
    plan = st.text_area("Plan d'action")
    date_eval = st.date_input("Date Bilan", datetime.now() + timedelta(days=7))
    
    if st.form_submit_button("Enregistrer Plan"):
        st.session_state.data_problemes = pd.concat([st.session_state.data_problemes, pd.DataFrame([{"Date": str(datetime.now().date()), "Problème": pb, "Solution Choisie": choix}])], ignore_index=True)
        st.success("Plan Sauvegardé !")

st.divider()
st.page_link("streamlit_app.py", label="Retour à l'accueil", icon="🏠")