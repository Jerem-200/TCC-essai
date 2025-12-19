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
st.set_page_config(page_title="Mon Parcours", page_icon="🗺️", layout="wide")

# Masquer la navigation latérale par défaut
st.markdown("""
    <style>
        [data-testid="stSidebarNav"] {display: none;}
        .stSelectbox {margin-bottom: 20px;}
    </style>
""", unsafe_allow_html=True)

# --- FONCTIONS UTILITAIRES ---
def charger_donnees_graphique(patient_id):
    """Charge l'historique UNE SEULE FOIS pour éviter les lenteurs."""
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

# Import sécurisé (Fallback)
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

# --- SIDEBAR ---
with st.sidebar:
    st.page_link("streamlit_app.py", label="🏠 Retour Accueil")
    st.divider()

# --- SÉCURITÉ ---
if "authentifie" not in st.session_state or not st.session_state.authentifie:
    st.warning("🔒 Veuillez vous connecter.")
    st.stop()

current_user = st.session_state.get("user_id", "")

# --- 1. CHARGEMENT DES DONNÉES (UNE SEULE FOIS) ---
with st.spinner("Chargement de votre parcours..."):
    modules_debloques = charger_progression(current_user)
    devoirs_exclus = charger_etat_devoirs(current_user)
    # On charge l'historique graphique ici pour ne pas le refaire dans chaque onglet
    df_history_global = charger_donnees_graphique(current_user)

st.title("🗺️ Mon Parcours de Soin")

# --- 2. SÉLECTION DU MODULE (OPTIMISATION) ---
# On crée une liste des modules disponibles pour le menu déroulant
options_modules = {k: v['titre'] for k, v in PROTOCOLE_BARLOW.items() if k in modules_debloques}

# Si aucun module n'est sélectionné, on prend le dernier débloqué par défaut
default_ix = len(options_modules) - 1 if options_modules else 0

col_sel, col_vide = st.columns([1, 2])
with col_sel:
    module_choisi = st.selectbox(
        "📂 Sélectionnez le module à travailler :", 
        options=list(options_modules.keys()),
        format_func=lambda x: options_modules[x], # Affiche le titre joli au lieu du code
        index=default_ix
    )

st.divider()

# --- 3. AFFICHAGE DU MODULE SÉLECTIONNÉ ---
if module_choisi:
    code_mod = module_choisi
    data = PROTOCOLE_BARLOW[code_mod]

    # Titre du module
    st.header(f"📘 {data['titre']}")

    # Les onglets
    tab_proc, tab_docs, tab_exos, tab_suivi = st.tabs(["📖 Ma Séance", "📂 Documents", "📝 Mes Exercices", "📈 Suivi"])
    
    # --- ONGLET 1 : DÉROULÉ ---
    with tab_proc:
        st.info(f"**Objectifs :** {data['objectifs']}")
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### 📝 Ce que nous avons vu")
            if data['etapes_seance']:
                for etape in data['etapes_seance']:
                    st.markdown(f"- **{etape['titre']}**")
                    if etape.get('details'): st.caption(f"&nbsp;&nbsp;_{etape.get('details')}_")
            else: st.write("Pas d'étape spécifique.")

        with c2:
            st.markdown("### 🏠 Travail à la maison")
            exclus_ici = devoirs_exclus.get(code_mod, [])
            a_faire = False
            if data['taches_domicile']:
                for j, dev in enumerate(data['taches_domicile']):
                    if j not in exclus_ici:
                        a_faire = True
                        st.markdown(f"👉 **{dev['titre']}**")
                        if dev.get('pdf') and os.path.exists(dev['pdf']):
                            with open(dev['pdf'], "rb") as f:
                                st.download_button(f"📥 Télécharger", f, file_name=os.path.basename(dev['pdf']), key=f"dl_dev_{code_mod}_{j}")
            if not a_faire: st.success("🎉 Aucun devoir.")
            else:
                st.write("")
                with st.expander("📸 Envoyer une photo de mon travail"):
                    st.camera_input("Prendre une photo", key=f"cam_{code_mod}")

    # --- ONGLET 2 : DOCUMENTS ---
    with tab_docs:
        st.write("Tous les fichiers du module :")
        if 'pdfs_module' in data and data['pdfs_module']:
            col_docs = st.columns(3)
            for idx, path in enumerate(data['pdfs_module']):
                if os.path.exists(path):
                    with open(path, "rb") as f:
                        col_docs[idx % 3].download_button(f"📥 {os.path.basename(path)}", f, file_name=os.path.basename(path), key=f"dl_all_{code_mod}_{os.path.basename(path)}")
        else: st.info("Aucun document.")

    # --- ONGLET 3 : EXERCICES ---
    with tab_exos:
        st.markdown("##### 📝 Remplir un bilan")
        choix_q = st.selectbox("Choisir l'exercice :", list(QUESTIONS_HEBDO.keys()), key=f"sel_q_{code_mod}")
        
        if choix_q:
            config_q = QUESTIONS_HEBDO[choix_q]
            with st.form(key=f"form_exo_{code_mod}_{choix_q}"):
                st.markdown(f"**{config_q['titre']}**")
                st.caption(config_q['description'])
                
                reponses = {}
                score_total = 0
                nom_emotion = ""

                # Nom émotion
                if config_q.get("ask_emotion"):
                    nom_emotion = st.text_input("Nom de l'émotion concernée :", key=f"emo_name_{code_mod}_{choix_q}")
                    if nom_emotion: reponses["Émotion identifiée"] = nom_emotion
                
                # Types de questions
                if config_q['type'] == "scale_0_8":
                    for q in config_q['questions']:
                        st.write(q)
                        val = st.slider("Intensité", 0, 8, 0, key=f"sld_{code_mod}_{choix_q}_{q}")
                        reponses[q] = val
                        score_total += val
                
                elif config_q['type'] == "text":
                    for q in config_q['questions']:
                        val = st.text_area(q, height=100, key=f"txt_{code_mod}_{choix_q}_{q}")
                        reponses[q] = val
                    score_total = -1
                
                elif config_q['type'] == "qcm_oasis":
                    for item in config_q['questions']:
                        st.markdown(f"**{item['label']}**")
                        choix = st.radio("Réponse :", item['options'], key=f"rad_{code_mod}_{choix_q}_{item['id']}", label_visibility="collapsed")
                        try: score_total += int(choix.split("=")[0].strip())
                        except: pass
                        reponses[item['label']] = choix

                st.write("")
                if st.form_submit_button("Envoyer", type="primary"):
                    if config_q.get("ask_emotion") and not nom_emotion:
                        st.error("Veuillez indiquer le nom de l'émotion.")
                    else:
                        nom_final = f"{code_mod} - {choix_q}"
                        if nom_emotion: nom_final += f" ({nom_emotion})"
                        if sauvegarder_reponse_hebdo(current_user, nom_final, str(score_total), reponses):
                            st.success("✅ Enregistré !")
                            time.sleep(1)
                            st.rerun()

    # --- ONGLET 4 : SUIVI ---
    with tab_suivi:
        st.markdown("##### 📈 Mes Progrès")
        if not df_history_global.empty:
            types_dispos = df_history_global["Type"].unique().tolist()
            # On essaie de pré-selectionner le type correspondant à l'exercice en cours si possible
            default_sel = types_dispos[:2]
            
            type_voir = st.multiselect("Afficher les courbes de :", types_dispos, default=default_sel, key=f"multi_{code_mod}")
            
            if type_voir:
                df_chart = df_history_global[df_history_global["Type"].isin(type_voir)]
                
                chart = alt.Chart(df_chart).mark_line(point=True).encode(
                    x=alt.X('Date', title='Date', axis=alt.Axis(format='%d/%m')),
                    y=alt.Y('Score_Global', title='Score'),
                    color=alt.Color('Type', title='Échelle'),
                    tooltip=['Date', 'Type', 'Score_Global']
                ).properties(height=350).interactive()
                
                st.altair_chart(chart, use_container_width=True)
            else:
                st.info("Sélectionnez une échelle.")
        else:
            st.info("Aucune donnée pour le moment.")

else:
    st.info("Aucun module débloqué pour le moment.")