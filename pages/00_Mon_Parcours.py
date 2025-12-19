import streamlit as st
import os
import time
import pandas as pd
import altair as alt
import json
from datetime import datetime

from protocole_config import PROTOCOLE_BARLOW, QUESTIONS_HEBDO 
from connect_db import load_data, sauvegarder_reponse_hebdo

# --- CONFIGURATION PAGE ---
st.set_page_config(page_title="Mon Parcours", page_icon="🗺️")

# Masquer la navigation latérale
st.markdown("""
    <style>
        [data-testid="stSidebarNav"] {display: none;}
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.page_link("streamlit_app.py", label="🏠 Retour Accueil")
    st.divider()

# --- SÉCURITÉ ---
if "authentifie" not in st.session_state or not st.session_state.authentifie:
    st.warning("🔒 Veuillez vous connecter.")
    st.stop()

current_user = st.session_state.get("user_id", "")

# --- FONCTIONS UTILITAIRES ---
# Fallback import
try:
    from streamlit_app import charger_progression, charger_etat_devoirs
except ImportError:
    def charger_progression(uid): 
        try:
            from connect_db import load_data
            import pandas as pd
            data = load_data("Progression")
            if data:
                df = pd.DataFrame(data)
                row = df[df["Patient"] == uid]
                if not row.empty:
                    return [x.strip() for x in str(row.iloc[0]["Modules_Actifs"]).split(",") if x.strip()]
        except: pass
        return ["module0"]
    def charger_etat_devoirs(uid): return {}

def charger_donnees_graphique(patient_id):
    try:
        raw_data = load_data("Reponses_Hebdo")
        if raw_data:
            df = pd.DataFrame(raw_data)
            df = df[df["Patient"] == patient_id].copy()
            if not df.empty:
                df["Date"] = pd.to_datetime(df["Date"])
                df["Score_Global"] = pd.to_numeric(df["Score_Global"], errors='coerce')
                def nettoyer_nom(x):
                    if " - " in str(x): return str(x).split(" - ")[1].split(" (")[0]
                    return str(x)
                df["Type"] = df["Questionnaire"].apply(nettoyer_nom)
                return df
    except: pass
    return pd.DataFrame()

# --- CHARGEMENT DONNÉES ---
modules_debloques = charger_progression(current_user)
devoirs_exclus = charger_etat_devoirs(current_user)
df_history = charger_donnees_graphique(current_user)

st.title("🗺️ Mon Parcours de Soin")

# =========================================================
# PARTIE 1 : SUIVI & BILANS (SORTIS DES MODULES)
# =========================================================
with st.expander("📊 **Mon Espace de Suivi (Questionnaires & Courbes)**", expanded=True):
    
    tab_bilan, tab_courbes = st.tabs(["📝 Remplir un bilan", "📈 Voir mes progrès"])
    
    # --- A. REMPLIR UN BILAN ---
    with tab_bilan:
        c_q1, c_q2 = st.columns([1, 2])
        
        with c_q1:
            choix_q = st.selectbox("1️⃣ Choisir le questionnaire :", list(QUESTIONS_HEBDO.keys()))
            

        with c_q2:
            if choix_q:
                config_q = QUESTIONS_HEBDO[choix_q]
                
                with st.form(key=f"form_global_{choix_q}"):
                    st.markdown(f"#### {config_q['titre']}")
                    st.caption(config_q['description'])
                    st.divider()
                    
                    reponses = {}
                    score_total = 0
                    nom_emotion = ""

                    # Demande nom émotion si besoin
                    if config_q.get("ask_emotion"):
                        nom_emotion = st.text_input("Emotion concernée (ex: Colère) :")
                        if nom_emotion: reponses["Emotion"] = nom_emotion
                    
                    # TYPES DE QUESTIONS
                    if config_q['type'] == "scale_0_8":
                        for q in config_q['questions']:
                            st.write(q)
                            val = st.slider("Note", 0, 8, 0, key=f"g_sld_{choix_q}_{q}")
                            reponses[q] = val
                            score_total += val
                    
                    elif config_q['type'] == "text":
                        for q in config_q['questions']:
                            val = st.text_area(q, height=80, key=f"g_txt_{choix_q}_{q}")
                            reponses[q] = val
                        score_total = -1
                    
                    elif config_q['type'] == "qcm_oasis":
                        for item in config_q['questions']:
                            st.markdown(f"**{item['label']}**")
                            choix = st.radio("Réponse", item['options'], key=f"g_rad_{choix_q}_{item['id']}", label_visibility="collapsed")
                            try: score_total += int(choix.split("=")[0].strip())
                            except: pass
                            reponses[item['label']] = choix

                    st.write("")
                    
                    if st.form_submit_button("Envoyer le bilan", type="primary"):
                        if config_q.get("ask_emotion") and not nom_emotion:
                            st.error("Indiquez l'émotion.")
                        else:
                            # Construction du nom pour l'historique
                            nom_final = choix_q                            
                            if nom_emotion: nom_final += f" ({nom_emotion})"

                            if sauvegarder_reponse_hebdo(current_user, nom_final, str(score_total), reponses):
                                st.success("✅ Bilan enregistré !")
                                time.sleep(1)
                                st.rerun()

    # --- B. VOIR LES COURBES ---
    with tab_courbes:
        if not df_history.empty:
            types_dispos = df_history["Type"].unique().tolist()
            choix_types = st.multiselect("Filtrer les échelles :", types_dispos, default=types_dispos[:2])
            
            if choix_types:
                df_chart = df_history[df_history["Type"].isin(choix_types)]
                chart = alt.Chart(df_chart).mark_line(point=True).encode(
                    x=alt.X('Date', title='Date', axis=alt.Axis(format='%d/%m')),
                    y=alt.Y('Score_Global', title='Score'),
                    color=alt.Color('Type', title='Échelle'),
                    tooltip=['Date', 'Type', 'Score_Global']
                ).properties(height=300).interactive()
                st.altair_chart(chart, use_container_width=True)
            else:
                st.info("Sélectionnez une échelle.")
        else:
            st.info("Aucune donnée disponible. Remplissez un premier bilan dans l'onglet voisin !")

st.write("---")

# =========================================================
# PARTIE 2 : LISTE DES MODULES (PROGRESSION)
# =========================================================
st.header("🗺️ Ma Progression")

for code_mod, data in PROTOCOLE_BARLOW.items():
    
    # Vérification si le module est débloqué
    if code_mod in modules_debloques:
        
        with st.expander(f"✅ {data['titre']}", expanded=False):
            
            # On prépare les onglets. S'il y a des exercices, on ajoute un onglet.
            liste_onglets = ["📖 Résumé Séance", "📂 Documents"]
            has_exos = "exercices" in data and data["exercices"]
            if has_exos:
                liste_onglets.append("📝 Exercices")
            
            tabs = st.tabs(liste_onglets)
            
            # --- ONGLET 1 : RÉSUMÉ SÉANCE ---
            with tabs[0]:
                st.info(f"**Objectifs :** {data['objectifs']}")
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("**📝 Ce que nous avons vu :**")
                    if data['etapes_seance']:
                        for etape in data['etapes_seance']:
                            st.markdown(f"- {etape['titre']}")
                    else: st.caption("N/A")
                with c2:
                    st.markdown("**🏠 Travail à la maison :**")
                    exclus = devoirs_exclus.get(code_mod, [])
                    a_faire = False
                    if data['taches_domicile']:
                        for j, dev in enumerate(data['taches_domicile']):
                            if j not in exclus:
                                a_faire = True
                                st.markdown(f"👉 **{dev['titre']}**")
                                if dev.get('pdf') and os.path.exists(dev['pdf']):
                                    with open(dev['pdf'], "rb") as f:
                                        st.download_button("📥 Support", f, file_name=os.path.basename(dev['pdf']), key=f"d_{code_mod}_{j}")
                    if not a_faire: st.caption("Rien de spécial.")
                    else:
                        st.write("")
                        with st.expander("📸 Envoyer une photo"):
                            st.camera_input("Photo", key=f"c_{code_mod}")

            # --- ONGLET 2 : DOCUMENTS ---
            with tabs[1]:
                if 'pdfs_module' in data and data['pdfs_module']:
                    for p in data['pdfs_module']:
                        if os.path.exists(p):
                            with open(p, "rb") as f:
                                st.download_button(f"📥 {os.path.basename(p)}", f, file_name=os.path.basename(p), key=f"da_{code_mod}_{os.path.basename(p)}")
                else: st.caption("Aucun document.")

            # --- ONGLET 3 : EXERCICES (NOUVEAU) ---
            if has_exos:
                with tabs[2]:
                    for exo in data["exercices"]:
                        st.subheader(exo["titre"])
                        st.caption(exo["description"])
                        
                        # --- LOGIQUE SPÉCIFIQUE : FICHE OBJECTIFS ---
                        if exo["type"] == "fiche_objectifs_traitement":
                            with st.form(key=f"form_exo_{code_mod}_{exo['id']}"):
                                st.markdown("Remplissez ce tableau pour clarifier vos objectifs.")
                                
                                # Le Problème Principal
                                st.markdown("#### 1. Le Problème")
                                st.caption("Comment vos émotions (tristesse, anxiété, etc.) ont-elles engendré des problèmes ?")
                                pb_principal = st.text_area("Problème principal :", height=100, key=f"pb_{code_mod}")
                                
                                st.divider()
                                
                                # Les Objectifs (On en propose 2 pour commencer)
                                st.markdown("#### 2. Objectifs & Étapes")
                                st.caption("Quels objectifs concrets pourraient résoudre ce problème ? Décomposez-les en étapes.")

                                c_obj1, c_obj2 = st.columns(2)
                                
                                # Objectif 1
                                with c_obj1:
                                    st.markdown("**Objectif Concret 1**")
                                    obj1 = st.text_input("Intitulé de l'objectif 1 :", key=f"o1_{code_mod}")
                                    st.markdown("_Les étapes nécessaires :_")
                                    steps1 = []
                                    for i in range(4):
                                        s = st.text_input(f"Étape {i+1}", key=f"s1_{i}_{code_mod}")
                                        steps1.append(s)

                                # Objectif 2
                                with c_obj2:
                                    st.markdown("**Objectif Concret 2**")
                                    obj2 = st.text_input("Intitulé de l'objectif 2 :", key=f"o2_{code_mod}")
                                    st.markdown("_Les étapes nécessaires :_")
                                    steps2 = []
                                    for i in range(4):
                                        s = st.text_input(f"Étape {i+1}", key=f"s2_{i}_{code_mod}")
                                        steps2.append(s)

                                st.write("")
                                if st.form_submit_button("💾 Enregistrer mes objectifs", type="primary"):
                                    # On structure les données pour la sauvegarde
                                    reponses_json = {
                                        "Problème Principal": pb_principal,
                                        "Objectif 1": obj1,
                                        "Etapes Objectif 1": [s for s in steps1 if s],
                                        "Objectif 2": obj2,
                                        "Etapes Objectif 2": [s for s in steps2 if s]
                                    }
                                    
                                    # On utilise la fonction générique de sauvegarde
                                    nom_sauvegarde = f"{code_mod} - {exo['titre']}"
                                    if sauvegarder_reponse_hebdo(current_user, nom_sauvegarde, "N/A", reponses_json):
                                        st.success("✅ Objectifs enregistrés ! Vous pouvez les retrouver dans l'onglet 'Documents' ou votre historique.")
                                        time.sleep(1)
                                        st.rerun()

    else:
        # Module verrouillé
        with st.container():
            st.markdown(f"🔒 **{data['titre']}** _(Verrouillé)_")
            st.divider()