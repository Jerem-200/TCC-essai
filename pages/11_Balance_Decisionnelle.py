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
# 3. CALCULS & RÉSULTATS (TABLEAU MATRICIEL + GRAPHIQUE)
# ==============================================================================
if st.session_state.balance_items:
    st.divider()
    st.subheader("3. Bilan (Score Net)")
    
    # --- A. CALCULS ---
    score_net_actuel = 0
    score_net_nouveau = 0
    
    # On prépare les contenus pour le tableau
    # Structure : { "ACTUEL": {"AVANTAGE": [], "INCONVENIENT": []}, ... }
    contenu = {
        "ACTUEL": {"AVANTAGE": [], "INCONVENIENT": [], "Total": 0},
        "NOUVEAU": {"AVANTAGE": [], "INCONVENIENT": [], "Total": 0}
    }

    for item in st.session_state.balance_items:
        # 1. Calcul du score net
        valeur = item["Poids"]
        if item["Sens"] == "INCONVENIENT":
            valeur = -valeur
        
        if item["Camp"] == "ACTUEL":
            score_net_actuel += valeur
            contenu["ACTUEL"]["Total"] += valeur
        else:
            score_net_nouveau += valeur
            contenu["NOUVEAU"]["Total"] += valeur
            
        # 2. Préparation du texte pour le tableau (Ex: "• Ça détend (8)")
        texte_arg = f"• {item['Argument']} (<b>{item['Poids']}</b>)"
        contenu[item["Camp"]][item["Sens"]].append(texte_arg)

    # --- B. TABLEAU À DOUBLE ENTRÉE (HTML) ---
    st.write("#### 📊 Tableau de synthèse")
    
    nom_actuel = actuel if actuel else "Option Actuelle"
    nom_nouveau = nouveau if nouveau else "Option Nouvelle"

    # Fonction pour formater une cellule (Liste + Total)
    def format_cell(liste_args):
        if not liste_args: return "-"
        return "<br>".join(liste_args)

    # Création des données pour le tableau
    data_matrix = [
        {
            "Option": f"<b>{nom_actuel}</b><br>(Statu Quo)",
            "👍 Avantages": format_cell(contenu["ACTUEL"]["AVANTAGE"]),
            "👎 Inconvénients": format_cell(contenu["ACTUEL"]["INCONVENIENT"]),
            "Bilan": f"<b>{score_net_actuel}</b>"
        },
        {
            "Option": f"<b>{nom_nouveau}</b><br>(Changement)",
            "👍 Avantages": format_cell(contenu["NOUVEAU"]["AVANTAGE"]),
            "👎 Inconvénients": format_cell(contenu["NOUVEAU"]["INCONVENIENT"]),
            "Bilan": f"<b>{score_net_nouveau}</b>"
        }
    ]
    
    df_matrix = pd.DataFrame(data_matrix)
    
    # Affichage du tableau en HTML pour gérer les retours à la ligne <br> et le gras <b>
    # On cache l'index (colonne 0, 1) pour que ce soit propre
    html_table = df_matrix.to_html(escape=False, index=False, justify='center', border=0)
    st.markdown(html_table, unsafe_allow_html=True)
    
    st.write("") # Espace
    
    # --- C. CONCLUSION AUTOMATIQUE ---
    diff = score_net_nouveau - score_net_actuel
    if diff > 0:
        st.success(f"👉 **Le Changement l'emporte** (Différence : +{diff} pts)")
    elif diff < 0:
        st.warning(f"👉 **Le Statu Quo reste plus favorable** (Différence : +{abs(diff)} pts)")
    else:
        st.info("⚖️ **Égalité parfaite.**")

    # --- D. GRAPHIQUE VISUEL ---
    st.write("#### 📉 Comparaison visuelle")
    data_chart = pd.DataFrame({
        'Option': [nom_actuel, nom_nouveau],
        'Score Net': [score_net_actuel, score_net_nouveau]
    })
    
    chart = alt.Chart(data_chart).mark_bar().encode(
        x=alt.X('Option', axis=alt.Axis(labelAngle=0, title=None)),
        y=alt.Y('Score Net', title='Score Net'),
        color=alt.Color('Option', scale=alt.Scale(range=['#FF6B6B', '#4ECDC4']), legend=None),
        tooltip=['Option', 'Score Net']
    ).properties(height=250)
    
    rule = alt.Chart(pd.DataFrame({'y': [0]})).mark_rule(color='black').encode(y='y')
    st.altair_chart(chart + rule, use_container_width=True)

    # --- DÉTAIL / GESTION ---
    with st.expander("🗑️ Supprimer des arguments"):
        for i, item in enumerate(st.session_state.balance_items):
            c1, c2 = st.columns([6, 1])
            with c1:
                icon = "🟢" if item["Sens"] == "AVANTAGE" else "🔴"
                camp = "Actuel" if item["Camp"] == "ACTUEL" else "Nouveau"
                st.write(f"{icon} [{camp}] {item['Argument']} ({item['Poids']})")
            with c2:
                if st.button("🗑️", key=f"del_{i}"):
                    st.session_state.balance_items.pop(i)
                    st.rerun()
    
    # ==============================================================================
    # 4. DÉCISION FINALE & SAUVEGARDE AUTOMATIQUE
    # ==============================================================================
    st.subheader("4. Ma Décision")
    st.write("Au vu de ce bilan, quelle est votre conclusion ?")

    with st.form("decision_form"):
        decision = st.text_area("Je décide de...", placeholder="Ex: Essayer le changement sur une semaine...")
        
        # C'est ce bouton qui déclenche la sauvegarde Cloud
        submitted_decision = st.form_submit_button("✅ Valider la décision et Enregistrer")

        if submitted_decision:
            # On compile les arguments
            resume_args = " | ".join([f"{i['Camp']} ({i['Sens']}): {i['Argument']} [{i['Poids']}]" for i in st.session_state.balance_items])
            
            from connect_db import save_data
            patient = st.session_state.get("patient_id", "Anonyme")
            
            # SAUVEGARDE CLOUD
            # Ordre : Patient, Date, Option A, Option B, Score A, Score B, Arguments, Décision
            save_data("Balance", [
                patient,
                datetime.now().strftime("%Y-%m-%d"),
                actuel,
                nouveau,
                score_net_actuel,
                score_net_nouveau,
                resume_args,
                decision
            ])
            st.balloons()
            st.success("Votre balance et votre décision ont été enregistrées dans le Cloud ! ☁️")

    # Bouton de nettoyage
    if st.button("🗑️ Tout effacer pour recommencer"):
        st.session_state.balance_items = []
        st.rerun()

else:
    st.info("Commencez par ajouter des arguments ci-dessus.")

st.divider()
st.page_link("streamlit_app.py", label="Retour à l'accueil", icon="🏠")