import streamlit as st
import os
import time
from protocole_config import PROTOCOLE_BARLOW, QUESTIONS_HEBDO # <--- Import modifié
from connect_db import load_data, sauvegarder_reponse_hebdo # <--- Import modifié

st.set_page_config(page_title="Mon Parcours", page_icon="🗺️")

# --- CSS pour masquer la sidebar par défaut si besoin ---
st.markdown("""
    <style>
        [data-testid="stSidebarNav"] {display: none;}
    </style>
""", unsafe_allow_html=True)

# --- Fonction de chargement progression (copie locale ou import si vous l'avez mis dans connect_db) ---
def charger_progression_locale(patient_id):
    try:
        data = load_data("Progression")
        if data:
            import pandas as pd
            df = pd.DataFrame(data)
            row = df[df["Patient"] == patient_id]
            if not row.empty:
                modules_str = str(row.iloc[0]["Modules_Actifs"])
                return [x.strip() for x in modules_str.split(",") if x.strip()]
    except: pass
    return ["intro"]

# --- SIDEBAR DE NAVIGATION ---
with st.sidebar:
    st.page_link("streamlit_app.py", label="🏠 Retour Accueil")
    st.divider()

# --- VERIFICATION CONNEXION ---
if "authentifie" not in st.session_state or not st.session_state.authentifie:
    st.warning("Veuillez vous connecter sur la page d'accueil.")
    st.stop()

patient_id = st.session_state.user_id
st.title("🗺️ Mon Parcours TCC")

# --- CHARGEMENT ---
modules_actifs = charger_progression_locale(patient_id)

# --- BOUCLE D'AFFICHAGE DES MODULES ---
for code_mod, data in PROTOCOLE_BARLOW.items():
    
    # On affiche le module seulement s'il est dans la liste des actifs
    if code_mod in modules_actifs:
        
        # Titre du module
        with st.expander(f"📘 {data['titre']}", expanded=True):
            
            # Onglets pour organiser le contenu
            tab_contenu, tab_quest = st.tabs(["📖 Contenu & Exercices", "📝 Bilans & Questionnaires"])
            
            # --- ONGLET 1 : CONTENU CLASSIQUE ---
            with tab_contenu:
                st.info(f"**Objectifs :** {data['objectifs']}")
                
                st.markdown("### 📄 Documents à consulter")
                found_doc = False
                if 'pdfs_module' in data and data['pdfs_module']:
                    for chemin in data['pdfs_module']:
                        nom_fichier = os.path.basename(chemin)
                        if os.path.exists(chemin):
                            found_doc = True
                            with open(chemin, "rb") as f:
                                st.download_button(f"📥 Télécharger {nom_fichier}", f, file_name=nom_fichier, key=f"dl_pat_{code_mod}_{nom_fichier}")
                
                if not found_doc:
                    st.caption("Pas de document PDF spécifique pour ce module.")

            # --- ONGLET 2 : QUESTIONNAIRES INTÉGRÉS (NOUVEAU) ---
            with tab_quest:
                st.markdown("##### Remplir un bilan pour ce module")
                st.caption("Sélectionnez un questionnaire ci-dessous si votre thérapeute vous l'a demandé.")
                
                # Sélecteur de questionnaire
                # On ajoute une clé unique basée sur le module pour éviter les conflits
                choix_q = st.selectbox("Choisir le questionnaire :", list(QUESTIONS_HEBDO.keys()), key=f"sel_q_{code_mod}")
                
                if choix_q:
                    config_q = QUESTIONS_HEBDO[choix_q]
                    
                    # Formulaire unique par module et par questionnaire
                    with st.form(key=f"form_{code_mod}_{choix_q}"):
                        st.markdown(f"**{config_q['titre']}**")
                        st.caption(config_q['description'])
                        
                        reponses = {}
                        score_total = 0
                        
                        # Type Echelle
                        if config_q['type'] == "scale_0_8":
                            for q in config_q['questions']:
                                st.write(q)
                                val = st.slider("Intensité", 0, 8, 0, key=f"sld_{code_mod}_{choix_q}_{q}")
                                reponses[q] = val
                                score_total += val
                        
                        # Type Texte
                        elif config_q['type'] == "text":
                            for q in config_q['questions']:
                                val = st.text_area(q, height=80, key=f"txt_{code_mod}_{choix_q}_{q}")
                                reponses[q] = val
                            score_total = -1

                        st.write("")
                        
                        if st.form_submit_button("Envoyer", type="primary"):
                            if sauvegarder_reponse_hebdo(patient_id, f"{code_mod} - {choix_q}", str(score_total), reponses):
                                st.success("✅ Enregistré !")
                                time.sleep(1)
                                st.rerun()

    else:
        # Module bloqué (optionnel, pour montrer ce qui vient après)
        with st.expander(f"🔒 {data['titre']} (Bientôt disponible)", expanded=False):
            st.caption("Ce module sera débloqué par votre thérapeute au fur et à mesure de votre progression.")