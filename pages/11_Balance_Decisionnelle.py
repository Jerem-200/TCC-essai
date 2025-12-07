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
    st.session_state.balance_items = [] # Liste pour stocker les arguments en cours

# ==============================================================================
# 1. DÉFINITION DU DILEMME
# ==============================================================================
st.subheader("1. Quel est le choix ?")

c1, c2 = st.columns(2)
with c1:
    actuel = st.text_input("Comportement Actuel (Statu Quo)", placeholder="Ex: Continuer à fumer")
with c2:
    nouveau = st.text_input("Nouveau Comportement (Changement)", placeholder="Ex: Arrêter de fumer")

st.divider()

# ==============================================================================
# 2. LA BALANCE (AJOUT DES ARGUMENTS)
# ==============================================================================
st.subheader("2. Peser les arguments")
st.write("Ajoutez les arguments un par un et donnez-leur un poids (importance).")

with st.form("ajout_argument_balance", clear_on_submit=True):
    # Choix du quadrant
    quadrant = st.selectbox("Type d'argument :", [
        f"👍 Avantages du comportement actuel",
        f"👎 Inconvénients du comportement actuel",
        f"👍 Avantages du comportement alternatif",
        f"👎 Inconvénients du comportement alternatif"
    ])
    
    col_arg, col_poids = st.columns([3, 1])
    with col_arg:
        argument = st.text_input("Argument :", placeholder="Ex: Ça me détend / C'est mauvais pour la santé")
    with col_poids:
        poids = st.slider("Importance (0-10)", 0, 10, 5)

    if st.form_submit_button("Ajouter à la balance"):
        if actuel and nouveau and argument:
            # On détermine le "Camp" (Pour le Changement ou Pour le Maintien ?)
            # LOGIQUE TCC : 
            # - Avantages Actuel = Maintien
            # - Inconvénients Actuel = Changement
            # - Avantages Nouveau = Changement
            # - Inconvénients Nouveau = Maintien
            
            camp = "Inconnu"
            if "Avantages à rester" in quadrant: camp = "MAINTIEN (Statu Quo)"
            elif "Inconvénients à rester" in quadrant: camp = "CHANGEMENT (Action)"
            elif "Avantages à changer" in quadrant: camp = "CHANGEMENT (Action)"
            elif "Inconvénients à changer" in quadrant: camp = "MAINTIEN (Statu Quo)"
            
            st.session_state.balance_items.append({
                "Type": quadrant,
                "Argument": argument,
                "Poids": poids,
                "Camp": camp
            })
            st.rerun()
        else:
            st.warning("Veuillez définir les comportements et l'argument.")

# ==============================================================================
# 3. RÉSULTATS VISUELS
# ==============================================================================
if st.session_state.balance_items:
    st.divider()
    st.subheader("3. Résultat de la pesée")
    
    df = pd.DataFrame(st.session_state.balance_items)
    
    # Calcul des scores totaux
    score_maintien = df[df["Camp"] == "MAINTIEN (Statu Quo)"]["Poids"].sum()
    score_changement = df[df["Camp"] == "CHANGEMENT (Action)"]["Poids"].sum()
    
    # Affichage des scores
    col_m, col_c = st.columns(2)
    with col_m:
        st.metric("Poids du Statu Quo", f"{score_maintien} pts")
        if score_maintien > score_changement:
            st.warning("Le maintien l'emporte pour l'instant.")
    with col_c:
        st.metric("Poids du Changement", f"{score_changement} pts")
        if score_changement > score_maintien:
            st.success("Le changement l'emporte !")
            
    # GRAPHIQUE COMPARATIF (Barres simples)
    data_chart = pd.DataFrame({
        'Option': ['Rester (Statu Quo)', 'Changer (Action)'],
        'Score Total': [score_maintien, score_changement],
        'Couleur': ['#FF6B6B', '#4ECDC4'] # Rouge / Vert
    })
    
    chart = alt.Chart(data_chart).mark_bar().encode(
        x=alt.X('Option', title=None),
        y='Score Total',
        color=alt.Color('Option', scale=alt.Scale(range=['#4ECDC4', '#FF6B6B']), legend=None),
        tooltip=['Option', 'Score Total']
    ).properties(height=300)
    
    st.altair_chart(chart, use_container_width=True)
    
    # TABLEAU DÉTAILLÉ
    with st.expander("Voir le détail des arguments"):
        st.dataframe(df, use_container_width=True)
        
        # Suppression individuelle
        options_del = {f"{row['Argument']} ({row['Poids']})": i for i, row in df.iterrows()}
        to_del = st.selectbox("Supprimer un argument", list(options_del.keys()))
        if st.button("🗑️ Supprimer"):
            st.session_state.balance_items.pop(options_del[to_del])
            st.rerun()

    st.divider()
    
    # ==============================================================================
    # 4. SAUVEGARDE
    # ==============================================================================
    if st.button("💾 Enregistrer cette Balance"):
        # On compile le texte pour qu'il tienne dans une cellule Excel
        resume_args = " | ".join([f"{i['Type']}: {i['Argument']} ({i['Poids']})" for i in st.session_state.balance_items])
        
        from connect_db import save_data
        patient = st.session_state.get("patient_id", "Anonyme")
        
        # Ordre : Patient, Date, Actuel, Nouveau, ScoreMaintien, ScoreChange, Details
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
        # On ne vide pas la liste pour laisser l'utilisateur voir son résultat

else:
    st.info("Commencez par ajouter des arguments ci-dessus.")

st.divider()
st.page_link("streamlit_app.py", label="Retour à l'accueil", icon="🏠")