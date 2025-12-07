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
st.info("Comparez les deux options en soustrayant les inconvénients aux avantages.")

# --- INITIALISATION ---
if "balance_items" not in st.session_state:
    st.session_state.balance_items = []

# Nettoyage préventif
if st.session_state.balance_items:
    if "Camp" in st.session_state.balance_items[0]:
        if "Statu Quo" in st.session_state.balance_items[0]["Camp"]: 
            st.session_state.balance_items = []
            st.rerun()

# ==============================================================================
# 1. DÉFINITION
# ==============================================================================
st.subheader("1. Les deux options")

c1, c2 = st.columns(2)
with c1:
    actuel = st.text_input("Comportement Actuel", placeholder="Ex: Continuer à fumer", key="bd_actuel")
with c2:
    nouveau = st.text_input("Comportement Alternatif", placeholder="Ex: Arrêter de fumer", key="bd_nouveau")

st.divider()

# ==============================================================================
# 2. AJOUT ARGUMENTS
# ==============================================================================
st.subheader("2. Ajouter des poids")
st.write("Notez l'importance de chaque argument sur 10.")

with st.form("ajout_argument_balance", clear_on_submit=True):
    options_type = [
        f"👍 Avantages : {actuel if actuel else 'Option Actuelle'}",
        f"👎 Inconvénients : {actuel if actuel else 'Option Actuelle'}",
        f"👍 Avantages : {nouveau if nouveau else 'Option Nouvelle'}",
        f"👎 Inconvénients : {nouveau if nouveau else 'Option Nouvelle'}"
    ]
    quadrant = st.selectbox("Type d'argument :", options_type)
    
    col_arg, col_poids = st.columns([3, 1])
    with col_arg:
        argument = st.text_input("Argument :", placeholder="Ex: Ça me détend...")
    with col_poids:
        poids = st.slider("Importance (0-10)", 0, 10, 5)

    if st.form_submit_button("Ajouter"):
        if argument:
            # Identification Camp et Sens
            if f": {actuel if actuel else 'Option Actuelle'}" in quadrant:
                camp_code = "ACTUEL"
            else:
                camp_code = "NOUVEAU"
            
            if "👍" in quadrant:
                sens_code = "AVANTAGE"
            else:
                sens_code = "INCONVENIENT"
            
            st.session_state.balance_items.append({
                "FullType": quadrant,
                "Camp": camp_code,
                "Sens": sens_code,
                "Argument": argument,
                "Poids": poids
            })
            st.rerun()
        else:
            st.warning("Veuillez écrire un argument.")

# ==============================================================================
# 3. CALCULS & RÉSULTATS
# ==============================================================================
if st.session_state.balance_items:
    st.divider()
    st.subheader("3. Bilan (Score Net)")
    
    # --- CALCUL DES SCORES NETS ---
    score_net_actuel = 0
    score_net_nouveau = 0
    
    for item in st.session_state.balance_items:
        valeur = item["Poids"]
        if item["Sens"] == "INCONVENIENT":
            valeur = -valeur
            
        if item["Camp"] == "ACTUEL":
            score_net_actuel += valeur
        elif item["Camp"] == "NOUVEAU":
            score_net_nouveau += valeur

    # --- AFFICHAGE MÉTRIQUES ---
    col_m, col_c = st.columns(2)
    nom_actuel = actuel if actuel else "Option Actuelle"
    nom_nouveau = nouveau if nouveau else "Option Nouvelle"
    
    with col_m:
        st.metric(f"Bilan : {nom_actuel}", f"{score_net_actuel} pts")
    with col_c:
        st.metric(f"Bilan : {nom_nouveau}", f"{score_net_nouveau} pts")
    
    # --- GRAPHIQUE ---
    st.write("")
    data_chart = pd.DataFrame({
        'Option': [nom_actuel, nom_nouveau],
        'Score Net': [score_net_actuel, score_net_nouveau]
    })
    
    chart = alt.Chart(data_chart).mark_bar().encode(
        x=alt.X('Option', axis=alt.Axis(labelAngle=0, title=None)),
        y=alt.Y('Score Net', title='Score Net'),
        color=alt.Color('Option', scale=alt.Scale(range=['#FF6B6B', '#4ECDC4']), legend=None),
        tooltip=['Option', 'Score Net']
    ).properties(height=300)
    
    rule = alt.Chart(pd.DataFrame({'y': [0]})).mark_rule(color='black').encode(y='y')
    st.altair_chart(chart + rule, use_container_width=True)
    
    # --- DÉTAIL ---
    with st.expander("Gérer / Supprimer des arguments", expanded=False):
        for i, item in enumerate(st.session_state.balance_items):
            col_text, col_btn = st.columns([6, 1])
            with col_text:
                icon = "🟢 (+)" if item["Sens"] == "AVANTAGE" else "🔴 (-)"
                camp_str = "Actuel" if item["Camp"] == "ACTUEL" else "Nouveau"
                st.write(f"{icon} **[{camp_str}]** {item['Argument']} (Poids: {item['Poids']})")
            with col_btn:
                if st.button("🗑️", key=f"del_bal_{i}"):
                    st.session_state.balance_items.pop(i)
                    st.rerun()

    st.divider()
    
    # ==============================================================================
    # 4. CONCLUSION & SAUVEGARDE (CORRIGÉ AVEC LES BONS NOMS DE VARIABLES)
    # ==============================================================================
    st.subheader("4. Conclusion")

    diff = score_net_nouveau - score_net_actuel
    
    if diff > 0:
        st.success(f"✅ **Conclusion : Le CHANGEMENT est plus favorable** (+{diff} pts).\n\nLes avantages à changer dépassent le coût de rester dans la situation actuelle.")
    elif diff < 0:
        st.warning(f"🛑 **Conclusion : Le MAINTIEN est plus favorable** (+{abs(diff)} pts).\n\nPour l'instant, le coût du changement semble trop élevé par rapport aux bénéfices actuels.")
    else:
        st.info("⚖️ **Conclusion : Ambivalence parfaite.** (0 pts de différence).")

    # Zone des boutons
    c_save, c_clear = st.columns([2, 1])
    
    with c_save:
        if st.button("☁️ Enregistrer ce résultat dans le Cloud"):
            resume_args = " | ".join([f"{i['Camp']} ({i['Sens']}): {i['Argument']} [{i['Poids']}]" for i in st.session_state.balance_items])
            
            from connect_db import save_data
            patient = st.session_state.get("patient_id", "Anonyme")
            
            # On utilise bien les variables score_net_...
            save_data("Balance", [
                patient,
                datetime.now().strftime("%Y-%m-%d"),
                actuel,
                nouveau,
                score_net_actuel,
                score_net_nouveau,
                resume_args
            ])
            st.success("Sauvegarde réussie ! ☁️")

    with c_clear:
        if st.button("🗑️ Tout effacer"):
            st.session_state.balance_items = []
            st.rerun()

else:
    st.info("Commencez par ajouter des arguments ci-dessus.")

st.divider()
st.page_link("streamlit_app.py", label="Retour à l'accueil", icon="🏠")