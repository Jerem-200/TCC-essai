import streamlit as st
import os
import time
import pandas as pd
import altair as alt
import json
from datetime import datetime

from protocole_config import PROTOCOLE_BARLOW, QUESTIONS_HEBDO 
from connect_db import load_data, sauvegarder_reponse_hebdo, supprimer_reponse

# --- CONFIGURATION ---
st.set_page_config(page_title="Mon Espace Santé", page_icon="🧘", layout="wide")

st.markdown("""
    <style>
        [data-testid="stSidebarNav"] {display: none;}
        .stExpander {border: 1px solid #ddd; border-radius: 5px;}
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.page_link("streamlit_app.py", label="🏠 Accueil")
    st.divider()

# --- SÉCURITÉ ---
if "authentifie" not in st.session_state or not st.session_state.authentifie:
    st.warning("🔒 Connexion requise.")
    st.stop()

current_user = st.session_state.user_id

# --- FONCTIONS UTILITAIRES (CACHE) ---
def charger_historique_complet(uid):
    """Charge tout l'historique pour l'onglet Suivi et Historique Exercices"""
    try:
        raw = load_data("Reponses_Hebdo")
        if raw:
            df = pd.DataFrame(raw)
            df = df[df["Patient"] == uid].copy()
            if not df.empty:
                df["Date"] = pd.to_datetime(df["Date"])
                return df
    except: pass
    return pd.DataFrame()

# Import helpers progression
try:
    from streamlit_app import charger_progression, charger_etat_devoirs
except ImportError:
    # Fallback simplifié
    def charger_progression(uid): return ["module0", "module1"] # Pour test
    def charger_etat_devoirs(uid): return {}

# --- CHARGEMENT DONNÉES ---
modules_debloques = charger_progression(current_user)
devoirs_exclus = charger_etat_devoirs(current_user)
df_history = charger_historique_complet(current_user)

st.title(f"Espace Patient - {current_user}")

# =========================================================
# LA GRANDE NAVIGATION (3 PILIERS)
# =========================================================
tab_sante, tab_outils, tab_parcours = st.tabs([
    "📊 Mon Suivi de Santé", 
    "🛠️ Mes Outils & Exercices", 
    "🗺️ Ma Progression"
])

# =========================================================
# 1. MON SUIVI DE SANTÉ (Questionnaires)
# =========================================================
with tab_sante:
    c1, c2 = st.columns([1, 2])
    
    with c1:
        st.subheader("📝 Bilan Hebdo")
        st.info("Sélectionnez une échelle à remplir :")
        choix_q = st.radio("Questionnaire :", list(QUESTIONS_HEBDO.keys()), label_visibility="collapsed")
    
    with c2:
        # --- FORMULAIRE QUESTIONNAIRE ---
        if choix_q:
            config = QUESTIONS_HEBDO[choix_q]
            with st.container(border=True):
                st.markdown(f"**{config['titre']}**")
                st.caption(config['description'])
                
                with st.form(f"form_sante_{choix_q}"):
                    reponses = {}
                    score = 0
                    
                    # Logique d'affichage (Similaire à avant)
                    if config.get("ask_emotion"):
                        emo = st.text_input("Emotion (ex: Colère) :")
                        if emo: reponses["Emotion"] = emo
                    
                    if config['type'] == "scale_0_8":
                        for q in config['questions']:
                            val = st.slider(q, 0, 8, 0)
                            reponses[q] = val
                            score += val
                    elif config['type'] == "qcm_oasis":
                        for item in config['questions']:
                            res = st.radio(item['label'], item['options'])
                            try: score += int(res.split("=")[0])
                            except: pass
                            reponses[item['label']] = res
                    
                    if st.form_submit_button("Enregistrer", type="primary"):
                        if sauvegarder_reponse_hebdo(current_user, choix_q, str(score), reponses):
                            st.success("Sauvegardé !")
                            time.sleep(1)
                            st.rerun()
    
    st.divider()
    st.subheader("📈 Mes Courbes")
    if not df_history.empty:
        # Filtre simple : on exclut les exercices complexes (ceux qui ont "Exercice" dans le nom ou type text)
        # Ici on suppose que tout ce qui est dans QUESTIONS_HEBDO est affichable
        types_graph = [t for t in df_history["Questionnaire"].unique() if t in QUESTIONS_HEBDO]
        sel_graph = st.multiselect("Afficher :", types_graph, default=types_graph[:2] if types_graph else None)
        
        if sel_graph:
            sub_df = df_history[df_history["Questionnaire"].isin(sel_graph)]
            chart = alt.Chart(sub_df).mark_line(point=True).encode(
                x='Date', y='Score_Global', color='Questionnaire', tooltip=['Date', 'Score_Global']
            ).interactive()
            st.altair_chart(chart, use_container_width=True)


# =========================================================
# 2. MES OUTILS (EXERCICES DYNAMIQUES)
# =========================================================
with tab_outils:
    
    # A. SÉLECTEUR D'EXERCICE
    # On cherche tous les exercices disponibles dans les modules débloqués
    liste_exos_dispos = []
    for m in modules_debloques:
        if m in PROTOCOLE_BARLOW and "exercices" in PROTOCOLE_BARLOW[m]:
            for exo in PROTOCOLE_BARLOW[m]["exercices"]:
                liste_exos_dispos.append({
                    "mod_code": m,
                    "mod_titre": PROTOCOLE_BARLOW[m]["titre"],
                    "exo_data": exo
                })
    
    col_menu, col_work = st.columns([1, 2])
    
    with col_menu:
        st.subheader("Choix de l'outil")
        if not liste_exos_dispos:
            st.warning("Aucun exercice disponible pour l'instant.")
            exo_choisi = None
        else:
            # Création des labels pour le selectbox
            options_map = {f"{x['mod_code']} - {x['exo_data']['titre']}": x for x in liste_exos_dispos}
            choix_cle = st.radio("Exercices disponibles :", list(options_map.keys()))
            exo_choisi = options_map[choix_cle]

    with col_work:
        if exo_choisi:
            exo_data = exo_choisi["exo_data"]
            st.markdown(f"### {exo_data['titre']}")
            st.info(exo_data['description'])
            
            # --- LOGIQUE DYNAMIQUE : FICHE OBJECTIFS ---
            if exo_data["type"] == "fiche_objectifs_traitement":
                
                # 1. Initialisation de la session pour stocker la liste temporaire
                if "temp_objectifs" not in st.session_state:
                    st.session_state.temp_objectives = []
                
                # 2. Zone d'ajout (Formulaire temporaire)
                with st.container(border=True):
                    st.markdown("#### ➕ Ajouter un nouvel objectif")
                    
                    col_input1, col_input2 = st.columns(2)
                    with col_input1:
                        new_pb = st.text_area("Problème lié :", height=70, placeholder="Ex: L'anxiété m'empêche de sortir.")
                    with col_input2:
                        new_obj = st.text_area("Objectif concret :", height=70, placeholder="Ex: Aller au cinéma une fois par mois.")
                    
                    new_steps = st.text_area("Étapes (une par ligne) :", height=70, placeholder="1. Choisir le film\n2. Acheter le billet...")
                    
                    if st.button("Ajouter cet objectif à ma liste"):
                        if new_obj:
                            # On ajoute à la liste en session
                            st.session_state.temp_objectives.append({
                                "probleme": new_pb,
                                "objectif": new_obj,
                                "etapes": new_steps.split('\n')
                            })
                            st.rerun() # On recharge pour afficher dans la liste ci-dessous
                        else:
                            st.error("L'objectif ne peut pas être vide.")

                # 3. Affichage de la liste en cours de construction
                st.markdown("#### 📋 Votre liste actuelle :")
                if st.session_state.temp_objectives:
                    for i, item in enumerate(st.session_state.temp_objectives):
                        with st.expander(f"Objectif {i+1}: {item['objectif']}", expanded=True):
                            st.write(f"**Problème :** {item['probleme']}")
                            st.write("**Étapes :**")
                            for s in item['etapes']:
                                if s.strip(): st.write(f"- {s}")
                            
                            # Bouton pour retirer un élément de la liste temporaire
                            if st.button(f"🗑️ Retirer", key=f"del_temp_{i}"):
                                st.session_state.temp_objectives.pop(i)
                                st.rerun()
                    
                    # 4. Bouton de SAUVEGARDE FINALE (Cloud)
                    st.divider()
                    if st.button("💾 Sauvegarder définitivement cet exercice", type="primary"):
                        # Préparation du JSON complet
                        payload = {
                            "type_exercice": "Objectifs Traitement",
                            "contenu": st.session_state.temp_objectives
                        }
                        nom_save = f"Exercice - {exo_data['titre']}"
                        
                        if sauvegarder_reponse_hebdo(current_user, nom_save, "N/A", payload):
                            st.success("Exercice sauvegardé dans l'historique !")
                            st.session_state.temp_objectives = [] # Reset
                            time.sleep(1)
                            st.rerun()
                else:
                    st.caption("Aucun objectif ajouté pour le moment.")

    # --- HISTORIQUE DES EXERCICES (BAS DE PAGE) ---
    st.divider()
    with st.expander("📜 Historique de mes exercices réalisés", expanded=False):
        # On filtre l'historique pour ne garder que les exercices (ceux qui commencent par 'Exercice')
        if not df_history.empty:
            df_exos = df_history[df_history["Questionnaire"].str.contains("Exercice", na=False)].copy()
            
            if not df_exos.empty:
                for idx, row in df_exos.iterrows():
                    col_date, col_nom, col_act = st.columns([1, 3, 1])
                    with col_date: st.write(row["Date"].strftime("%d/%m/%Y"))
                    with col_nom: st.write(f"**{row['Questionnaire']}**")
                    with col_act:
                        # Bouton de suppression
                        if st.button("Supprimer", key=f"del_hist_{idx}"):
                            # Note: nécessite la fonction supprimer_reponse configurée en Etape 1
                            supprimer_reponse(current_user, row["Date"], row["Questionnaire"])
                            st.rerun()
                    
                    # Affichage du détail (JSON)
                    with st.expander("Voir le détail"):
                        try:
                            details = json.loads(row["Details_Json"])
                            if "contenu" in details: # Structure liste d'objectifs
                                for item in details["contenu"]:
                                    st.markdown(f"**🎯 {item['objectif']}**")
                                    st.caption(f"Pb: {item['probleme']}")
                                    for s in item.get('etapes', []): st.write(f"- {s}")
                                    st.write("---")
                            else:
                                st.json(details)
                        except:
                            st.write("Erreur lecture détail.")
            else:
                st.info("Aucun exercice sauvegardé.")


# =========================================================
# 3. MA PROGRESSION (VUE SIMPLIFIÉE)
# =========================================================
with tab_parcours:
    st.markdown("### 🗺️ Mon cheminement")
    
    for code_mod, data in PROTOCOLE_BARLOW.items():
        if code_mod in modules_debloques:
            with st.expander(f"✅ {data['titre']}", expanded=False):
                # Contenu passif uniquement
                st.info(data['objectifs'])
                
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("**Résumé séance :**")
                    if data['etapes_seance']:
                        for e in data['etapes_seance']: st.write(f"- {e['titre']}")
                
                with c2:
                    st.markdown("**Documents :**")
                    if data.get('pdfs_module'):
                        for p in data['pdfs_module']:
                            if os.path.exists(p):
                                with open(p, "rb") as f:
                                    st.download_button(f"📥 {os.path.basename(p)}", f, file_name=os.path.basename(p), key=f"d_p_{code_mod}_{os.path.basename(p)}")
                    else:
                        st.caption("Aucun.")
        else:
            st.markdown(f"🔒 **{data['titre']}**")