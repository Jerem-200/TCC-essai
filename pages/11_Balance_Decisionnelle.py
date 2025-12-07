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
        f"👍 Avantages : {actuel if actuel else 'Actuel'}",
        f"👎 Inconvénients : {actuel if actuel else 'Actuel'}",
        f"👍 Avantages : {nouveau if nouveau else 'Alternatif'}",
        f"👎 Inconvénients : {nouveau if nouveau else 'Alternatif'}"
    ]
    quadrant = st.selectbox("Type d'argument :", options_type)
    
    col_arg, col_poids = st.columns([3, 1])
    with col_arg:
        argument = st.text_input("Argument :", placeholder="Ex: Ça me détend...")
    with col_poids:
        poids = st.slider("Importance (0-10)", 0, 10, 5)

    if st.form_submit_button("Ajouter"):
        if argument:
            # On stocke le type brut pour le tri plus tard
            # On simplifie le stockage du "Camp" pour l'affichage couleur
            if "Actuel" in quadrant: camp_visuel = "ACTUEL"
            else: camp_visuel = "NOUVEAU"
            
            st.session_state.balance_items.append({
                "FullType": quadrant, # Sert à identifier avantages/inconvénients
                "Argument": argument,
                "Poids": poids,
                "Camp": camp_visuel
            })
            st.rerun()
        else:
            st.warning("Veuillez écrire un argument.")

# ==============================================================================
# 3. CALCULS & RÉSULTATS (LOGIQUE MODIFIÉE : AVANTAGES - INCONVÉNIENTS)
# ==============================================================================
if st.session_state.balance_items:
    st.divider()
    st.subheader("3. Bilan (Score Net)")
    
    df = pd.DataFrame(st.session_state.balance_items)
    
    # --- CALCUL SCORES NETS ---
    # 1. Option Actuelle
    plus_actuel = 0
    moins_actuel = 0
    for i in st.session_state.balance_items:
        if "Avantages" in i["FullType"] and "Actuel" in i["FullType"]:
            plus_actuel += i["Poids"]
        elif "Inconvénients" in i["FullType"] and "Actuel" in i["FullType"]:
            moins_actuel += i["Poids"]
            
    score_net_actuel = plus_actuel - moins_actuel

    # 2. Option Nouvelle
    plus_nouveau = 0
    moins_nouveau = 0
    for i in st.session_state.balance_items:
        if "Avantages" in i["FullType"] and "Alternatif" in i["FullType"]:
            plus_nouveau += i["Poids"]
        elif "Inconvénients" in i["FullType"] and "Alternatif" in i["FullType"]:
            moins_nouveau += i["Poids"]
            
    score_net_nouveau = plus_nouveau - moins_nouveau
    
    # --- AFFICHAGE MÉTRIQUES ---
    col_m, col_c = st.columns(2)
    
    nom_actuel = actuel if actuel else "Option Actuelle"
    nom_nouveau = nouveau if nouveau else "Option Nouvelle"
    
    with col_m:
        st.metric(f"Bilan : {nom_actuel}", f"{score_net_actuel} pts", help=f"(+{plus_actuel}) - ({moins_actuel})")
        
    with col_c:
        st.metric(f"Bilan : {nom_nouveau}", f"{score_net_nouveau} pts", help=f"(+{plus_nouveau}) - ({moins_nouveau})")
    
    # Message de conclusion
    if score_net_nouveau > score_net_actuel:
        st.success(f"👉 Le changement semble plus bénéfique (Différence : {score_net_nouveau - score_net_actuel} pts)")
    elif score_net_actuel > score_net_nouveau:
        st.warning(f"👉 Le statu quo reste plus confortable pour l'instant (Différence : {score_net_actuel - score_net_nouveau} pts)")
    else:
        st.info("⚖️ Égalité parfaite entre les deux options.")

    # --- GRAPHIQUE ---
    st.write("")
    data_chart = pd.DataFrame({
        'Option': [nom_actuel, nom_nouveau],
        'Score Net': [score_net_actuel, score_net_nouveau]
    })
    
    # Barres verticales
    chart = alt.Chart(data_chart).mark_bar().encode(
        x=alt.X('Option', axis=alt.Axis(labelAngle=0, title=None)),
        y=alt.Y('Score Net', title='Score Net (Avantages - Inconvénients)'),
        color=alt.Color('Option', scale=alt.Scale(range=['#FF6B6B', '#4ECDC4']), legend=None),
        tooltip=['Option', 'Score Net']
    ).properties(height=300)
    
    # Ajout ligne zéro pour bien voir le positif/négatif
    rule = alt.Chart(pd.DataFrame({'y': [0]})).mark_rule(color='black').encode(y='y')
    
    st.altair_chart(chart + rule, use_container_width=True)
    
    # --- DÉTAIL ---
    with st.expander("Gérer / Supprimer des arguments", expanded=True):
        if not st.session_state.balance_items:
            st.info("Aucun argument.")
        else:
            for i, item in enumerate(st.session_state.balance_items):
                col_text, col_btn = st.columns([6, 1])
                with col_text:
                    # Icône selon Avantage/Inconvénient
                    if "Avantages" in item["FullType"]:
                        icon = "🟢 (+)"
                    else:
                        icon = "🔴 (-)"
                        
                    # On affiche proprement : 🟢 (+) Avantages Actuel : Argument (Note)
                    short_type = item["FullType"].split('(')[0].strip() # Garde juste le début du texte
                    st.write(f"{icon} **{short_type}** : {item['Argument']} (Poids: {item['Poids']})")
                with col_btn:
                    if st.button("🗑️", key=f"del_bal_{i}"):
                        st.session_state.balance_items.pop(i)
                        st.rerun()

    st.divider()
    
    # ==============================================================================
    # 4. SAUVEGARDE
    # ==============================================================================
    c_save, c_clear = st.columns([2, 1])
    
    with c_save:
        if st.button("💾 Enregistrer ce Bilan"):
            resume_args = " | ".join([f"{i['FullType']}: {i['Argument']} ({i['Poids']})" for i in st.session_state.balance_items])
            
            from connect_db import save_data
            patient = st.session_state.get("patient_id", "Anonyme")
            
            save_data("Balance", [
                patient,
                datetime.now().strftime("%Y-%m-%d"),
                actuel,
                nouveau,
                score_net_actuel,   # On sauve le score net
                score_net_nouveau,  # On sauve le score net
                resume_args
            ])
            st.success("Enregistré !")

    with c_clear:
        if st.button("🗑️ Tout effacer"):
            st.session_state.balance_items = []
            st.rerun()

else:
    st.info("Commencez par ajouter des arguments ci-dessus.")

st.divider()
st.page_link("streamlit_app.py", label="Retour à l'accueil", icon="🏠")