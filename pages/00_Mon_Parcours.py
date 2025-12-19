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
            
            # Optionnel : Lier à un module pour l'historique
            # On ne propose que les modules débloqués
            liste_mods = [f"{k} : {v['titre']}" for k, v in PROTOCOLE_BARLOW.items() if k in modules_debloques]
            mod_concerne = st.selectbox("2️⃣ Module concerné (Optionnel) :", ["Aucun / Général"] + liste_mods)
        
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
                            if mod_concerne and "Aucun" not in mod_concerne:
                                code_simple = mod_concerne.split(":")[0].strip()
                                nom_final = f"{code_simple} - {choix_q}"
                            
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

# On boucle sur TOUS les modules du protocole
for code_mod, data in PROTOCOLE_BARLOW.items():
    
    # Si débloqué
    if code_mod in modules_debloques:
        
        # Affichage classique (Expander) qui montre bien la liste verticale
        with st.expander(f"✅ {data['titre']}", expanded=False):
            
            t_seance, t_doc = st.tabs(["📖 Résumé Séance", "📂 Documents"])
            
            # Contenu léger (Texte uniquement = Très rapide)
            with t_seance:
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

            with t_doc:
                if 'pdfs_module' in data and data['pdfs_module']:
                    for p in data['pdfs_module']:
                        if os.path.exists(p):
                            with open(p, "rb") as f:
                                st.download_button(f"📥 {os.path.basename(p)}", f, file_name=os.path.basename(p), key=f"da_{code_mod}_{os.path.basename(p)}")
                else: st.caption("Aucun document.")

    else:
        # Module bloqué
        with st.container():
            st.markdown(f"🔒 **{data['titre']}** _(Verrouillé)_")
            st.divider()