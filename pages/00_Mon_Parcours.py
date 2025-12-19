import streamlit as st
import os
import time  # <--- Ajouté pour gérer le rechargement après sauvegarde
from protocole_config import PROTOCOLE_BARLOW, QUESTIONS_HEBDO 
from connect_db import load_data, sauvegarder_reponse_hebdo

# Import sécurisé (On garde ta logique de sécurité)
try:
    from streamlit_app import charger_progression, charger_etat_devoirs
except ImportError:
    # Fallback si l'import direct échoue (copie de sécurité)
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

st.set_page_config(page_title="Mon Parcours", page_icon="🗺️")

# Masquer la navigation latérale par défaut
st.markdown("""
    <style>
        [data-testid="stSidebarNav"] {display: none;}
    </style>
""", unsafe_allow_html=True)

# Sidebar de navigation
with st.sidebar:
    st.page_link("streamlit_app.py", label="🏠 Retour Accueil")
    st.divider()

if "authentifie" not in st.session_state or not st.session_state.authentifie:
    st.warning("🔒 Veuillez vous connecter.")
    st.stop()

# --- FORCER LE CHARGEMENT DES DONNÉES FRAÎCHES ---
current_user = st.session_state.get("user_id", "")
modules_debloques = charger_progression(current_user) # Charge depuis la DB
devoirs_exclus = charger_etat_devoirs(current_user)

st.title("🗺️ Mon Parcours de Soin")

# --- BOUCLE MODULES ---
for code_mod, data in PROTOCOLE_BARLOW.items():
    
    # Vérification stricte si le module est dans la liste chargée
    if code_mod in modules_debloques:
        
        # Par défaut, on ferme tout
        with st.expander(f"✅ {data['titre']}", expanded=False):
            
            # --- MODIFICATION ICI : AJOUT DU 3ème ONGLET ---
            tab_proc, tab_docs, tab_exos = st.tabs(["📖 Ma Séance", "📂 Documents", "📝 Mes Exercices"])
            
            # ONGLET 1 : DÉROULÉ SIMPLIFIÉ
            with tab_proc:
                st.info(f"**Objectifs :** {data['objectifs']}")
                
                # Tâches à domicile (Filtrées)
                st.markdown("##### 🏠 À faire pour la prochaine fois")
                exclus_ici = devoirs_exclus.get(code_mod, [])
                a_faire = False
                
                if data['taches_domicile']:
                    for j, dev in enumerate(data['taches_domicile']):
                        if j not in exclus_ici:
                            a_faire = True
                            st.write(f"👉 **{dev['titre']}**")
                            if dev.get('pdf') and os.path.exists(dev['pdf']):
                                with open(dev['pdf'], "rb") as f:
                                    st.download_button("Télécharger", f, file_name=os.path.basename(dev['pdf']), key=f"dl_dev_{code_mod}_{j}")
                
                if not a_faire:
                    st.success("🎉 Aucun devoir spécifique.")
                else:
                    st.write("")
                    with st.expander("📸 Envoyer mon travail"):
                        st.camera_input("Prendre une photo", key=f"cam_{code_mod}")

            # ONGLET 2 : TOUS LES DOCS (Liste plate)
            with tab_docs:
                st.write("Tous les fichiers du module :")
                if 'pdfs_module' in data and data['pdfs_module']:
                    for path in data['pdfs_module']:
                        name = os.path.basename(path)
                        if os.path.exists(path):
                            with open(path, "rb") as f:
                                st.download_button(f"📥 {name}", f, file_name=name, key=f"dl_pat_all_{code_mod}_{name}")
                else:
                    st.info("Aucun document.")

            # --- ONGLET 3 : MES EXERCICES (NOUVEAU) ---
            with tab_exos:
                st.markdown("##### 📝 Remplir un bilan ou un exercice")
                st.caption("Sélectionnez le questionnaire ci-dessous pour le remplir numériquement.")

                # Sélecteur de questionnaire avec clé unique par module
                choix_q = st.selectbox("Choisir l'exercice :", list(QUESTIONS_HEBDO.keys()), key=f"sel_q_{code_mod}")
                
                if choix_q:
                    config_q = QUESTIONS_HEBDO[choix_q]
                    
                    # Formulaire unique
                    with st.form(key=f"form_exo_{code_mod}_{choix_q}"):
                        st.markdown(f"**{config_q['titre']}**")
                        st.caption(config_q['description'])
                        
                        reponses = {}
                        score_total = 0
                        
                        # Cas A : Échelles numériques
                        if config_q['type'] == "scale_0_8":
                            for q in config_q['questions']:
                                st.write(q)
                                # Slider unique
                                val = st.slider("Intensité", 0, 8, 0, key=f"sld_{code_mod}_{choix_q}_{q}")
                                reponses[q] = val
                                score_total += val
                        
                        # Cas B : Texte libre
                        elif config_q['type'] == "text":
                            for q in config_q['questions']:
                                # Text area unique
                                val = st.text_area(q, height=100, key=f"txt_{code_mod}_{choix_q}_{q}")
                                reponses[q] = val
                            score_total = -1

                        st.write("")
                        
                        if st.form_submit_button("Envoyer", type="primary"):
                            # On sauvegarde avec une référence au module actuel
                            nom_enregistrement = f"{code_mod} - {choix_q}"
                            
                            if sauvegarder_reponse_hebdo(current_user, nom_enregistrement, str(score_total), reponses):
                                st.success("✅ Enregistré avec succès !")
                                time.sleep(1)
                                st.rerun()

    else:
        with st.container(border=True):
            st.write(f"🔒 **{data['titre']}**")
            st.caption("Verrouillé par votre thérapeute.")