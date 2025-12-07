import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime

st.set_page_config(page_title="Balance Décisionnelle", page_icon="⚖️")

# --- VIGILE ---
if "authentifie" not in st.session_state or not st.session_state.authentifie:
    st.warning("⛔ Veuillez vous connecter sur la page d'accueil.")
    st.switch_page("streamlit_app.py")
    st.stop()

st.title("⚖️ Balance Décisionnelle")
st.info("Un outil pour peser le pour et le contre d'un changement de comportement.")

# --- INITIALISATION MÉMOIRE ---
if "balance_items" not in st.session_state:
    st.session_state.balance_items = [] 

# ==============================================================================
# 1. DÉFINITION DU DILEMME
# ==============================================================================
st.subheader("1. Quel est le choix ?")

c1, c2 = st.columns(2)
with c1:
    actuel = st.text_input("Comportement Actuel", placeholder="Ex: Continuer à fumer")
with c2:
    nouveau = st.text_input("Comportement alternatif", placeholder="Ex: Arrêter de fumer")

st.divider()

# ==============================================================================
# 2. LA BALANCE (AJOUT DES ARGUMENTS)
# ==============================================================================
st.subheader("2. Peser les arguments")
st.write("Ajoutez les arguments un par un.")

with st.form("ajout_argument_balance", clear_on_submit=True):
    quadrant = st.selectbox("Type d'argument :", [
        f"👍 Avantages du comportement actuel ({actuel})",
        f"👎 Inconvénients du comportement actuel ({actuel})",
        f"👍 Avantages du comportement alternatif ({nouveau})",
        f"👎 Inconvénients du comportement alternatif ({nouveau})"
    ])
    
    col_arg, col_poids = st.columns([3, 1])
    with col_arg:
        argument = st.text_input("Argument :", placeholder="Ex: Ça me détend...")
    with col_poids:
        poids = st.slider("Importance (0-10)", 0, 10, 5)

    if st.form_submit_button("Ajouter à la balance"):
        if argument:
            # Logique TCC pour déterminer le camp
            if "Avantages à rester" in quadrant: camp = "MAINTIEN (Statu Quo)"
            elif "Inconvénients à rester" in quadrant: camp = "CHANGEMENT (Action)"
            elif "Avantages à changer" in quadrant: camp = "CHANGEMENT (Action)"
            elif "Inconvénients à changer" in quadrant: camp = "MAINTIEN (Statu Quo)"
            else: camp = "Inconnu"
            
            st.session_state.balance_items.append({
                "Type": quadrant,
                "Argument": argument,
                "Poids": poids,
                "Camp": camp
            })
            st.rerun()
        else:
            st.warning("Écrivez un argument.")

# ==============================================================================
# 3. RÉSULTATS VISUELS (CORRIGÉ)
# ==============================================================================
if st.session_state.balance_items:
    st.divider()
    st.subheader("3. Résultat de la pesée")
    
    df = pd.DataFrame(st.session_state.balance_items)
    
    # Calcul des scores
    score_maintien = df[df["Camp"] == "MAINTIEN (Statu Quo)"]["Poids"].sum()
    score_changement = df[df["Camp"] == "CHANGEMENT (Action)"]["Poids"].sum()
    
    # Affichage des métriques
    col_m, col_c = st.columns(2)
    with col_m:
        st.metric("Poids du Statu Quo", f"{score_maintien} pts")
        if score_maintien > score_changement:
            st.warning("Le maintien l'emporte.")
    with col_c:
        st.metric("Poids du Changement", f"{score_changement} pts")
        if score_changement > score_maintien:
            st.success("Le changement l'emporte !")
            
    # --- GRAPHIQUE CORRIGÉ ---
    st.write("") # Petit espace
    
    # On prépare les données proprement
    data_chart = pd.DataFrame({
        'Option': ['Rester (Statu Quo)', 'Changer (Action)'],
        'Score': [score_maintien, score_changement]
    })
    
    # Base du graphique
    base = alt.Chart(data_chart).encode(
        x=alt.X('Option', axis=alt.Axis(labelAngle=0, title=None)),
        y=alt.Y('Score', title='Poids total'),
        tooltip=['Option', 'Score']
    )
    
    # Les barres (Couleurs forcées via domain/range pour être sûr que ça ne bouge pas)
    bars = base.mark_bar().encode(
        color=alt.Color('Option', scale=alt.Scale(
            domain=['Rester (Statu Quo)', 'Changer (Action)'],
            range=['#FF6B6B', '#4ECDC4']  # Rouge vs Vert
        ), legend=None)
    )
    
    # Les chiffres au dessus des barres (Pour bien voir le contenu)
    text = base.mark_text(dy=-10, fontSize=14, fontWeight='bold').encode(
        text='Score'
    )
    
    st.altair_chart(bars + text, use_container_width=True)
    
    # --- TABLEAU DÉTAILLÉ ---
    with st.expander("Gérer / Supprimer des arguments"):
        if not st.session_state.balance_items:
            st.info("Aucun argument.")
        else:
            st.write("Liste des arguments :")
            for i, item in enumerate(st.session_state.balance_items):
                col_text, col_btn = st.columns([6, 1])
                with col_text:
                    icon = "🔴" if "MAINTIEN" in item["Camp"] else "🟢"
                    st.write(f"{icon} **{item['Type']}** : {item['Argument']} (Poids: {item['Poids']})")
                with col_btn:
                    if st.button("🗑️", key=f"del_bal_{i}"):
                        st.session_state.balance_items.pop(i)
                        st.rerun()

    st.divider()
    
    # ==============================================================================
    # 4. SAUVEGARDE
    # ==============================================================================
    if st.button("💾 Enregistrer cette Balance"):
        resume_args = " | ".join([f"{i['Type']}: {i['Argument']} ({i['Poids']})" for i in st.session_state.balance_items])
        
        from connect_db import save_data
        patient = st.session_state.get("patient_id", "Anonyme")
        
        save_data("Balance", [
            patient,
            datetime.now().strftime("%Y-%m-%d"),
            actuel,
            nouveau,
            score_maintien,
            score_changement,
            resume_args
        ])
        
        st.success("Balance enregistrée ! Vous pouvez la retrouver dans le fichier global.")

else:
    st.info("Commencez par ajouter des arguments ci-dessus.")

st.divider()
st.page_link("streamlit_app.py", label="Retour à l'accueil", icon="🏠")