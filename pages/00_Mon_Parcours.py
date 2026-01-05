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

# --- FONCTIONS UTILITAIRES ---
def charger_historique_complet(uid):
    try:
        raw = load_data("Reponses_Hebdo")
        if raw:
            df = pd.DataFrame(raw)
            df = df[df["Patient"] == uid].copy()
            if not df.empty:
                df["Date"] = pd.to_datetime(df["Date"])
                df["Score_Global"] = pd.to_numeric(df["Score_Global"], errors='coerce')
                def nettoyer_nom(x):
                    s = str(x)
                    if " - " in s: s = s.split(" - ")[1]
                    return s.split(" (")[0]
                df["Type"] = df["Questionnaire"].apply(nettoyer_nom)
                return df
    except Exception as e:
        print(f"Erreur histo: {e}")
    return pd.DataFrame()

try:
    from streamlit_app import charger_progression, charger_etat_devoirs
except ImportError:
    def charger_progression(uid): return ["module0"] 
    def charger_etat_devoirs(uid): return {}

modules_debloques = charger_progression(current_user)
devoirs_exclus = charger_etat_devoirs(current_user)
df_history = charger_historique_complet(current_user)

st.title(f"Espace Patient - {current_user}")

# =========================================================
# LES 4 ONGLETS (STRUCTURE IDENTIQUE À AVANT)
# =========================================================
tab_parcours, tab_outils, tab_bilan, tab_historique = st.tabs([
    "🗺️ Ma Progression", "🛠️ Mes Outils", "📝 Bilan Hebdo", "📜 Mon Historique"
])

# 1. MA PROGRESSION (Code inchangé)
with tab_parcours:
    st.markdown("### 📍 Mon cheminement")
    for code_mod, data in PROTOCOLE_BARLOW.items():
        if code_mod in modules_debloques:
            with st.expander(f"✅ {data['titre']}", expanded=False):
                t_seance, t_doc = st.tabs(["📖 Résumé Séance", "📂 Documents"])
                with t_seance:
                    st.info(f"**Objectifs :** {data['objectifs']}")
                    col_step, col_home = st.columns(2)
                    with col_step:
                        st.markdown("#### 📝 Ce que nous avons vu")
                        if data['etapes_seance']:
                            for etape in data['etapes_seance']:
                                st.markdown(f"- **{etape['titre']}**")
                                if etape.get('details'): st.caption(f"_{etape.get('details')}_")
                        else: st.caption("Pas d'étapes listées.")
                    with col_home:
                        st.markdown("#### 🏠 Travail à la maison")
                        exclus = devoirs_exclus.get(code_mod, [])
                        if data['taches_domicile']:
                            for j, dev in enumerate(data['taches_domicile']):
                                if j not in exclus:
                                    st.markdown(f"👉 **{dev['titre']}**")
                                    if dev.get('pdf') and os.path.exists(dev['pdf']):
                                        with open(dev['pdf'], "rb") as f:
                                            st.download_button("📥 Support", f, file_name=os.path.basename(dev['pdf']), key=f"d_home_{code_mod}_{j}")
                            st.write("")
                            with st.expander("📸 Envoyer une photo"):
                                st.camera_input("Photo", key=f"cam_{code_mod}")
                with t_doc:
                    st.write("Tous les fichiers du module :")
                    if data.get('pdfs_module'):
                        for p in data['pdfs_module']:
                            if os.path.exists(p):
                                with open(p, "rb") as f:
                                    st.download_button(f"📥 {os.path.basename(p)}", f, file_name=os.path.basename(p), key=f"da_{code_mod}_{os.path.basename(p)}")
        else:
            with st.container():
                st.markdown(f"🔒 **{data['titre']}** _(Verrouillé)_")
                st.divider()

# 2. MES OUTILS (LE LANCEUR LÉGER)
with tab_outils:
    liste_exos_dispos = []
    for m in modules_debloques:
        if m in PROTOCOLE_BARLOW and "exercices" in PROTOCOLE_BARLOW[m]:
            for exo in PROTOCOLE_BARLOW[m]["exercices"]:
                liste_exos_dispos.append({"mod_code": m, "exo_data": exo})
    
    liste_exos_dispos.sort(key=lambda x: x['mod_code'])
    
    col_menu, col_work = st.columns([1, 2])
    with col_menu:
        st.subheader("Choix de l'outil")
        if not liste_exos_dispos:
            st.warning("⚠️ Aucun exercice trouvé.")
        else:
            options_map = {f"{x['mod_code']} - {x['exo_data']['titre']}": x for x in liste_exos_dispos}
            choix_cle = st.radio("Exercices disponibles :", list(options_map.keys()))
            exo_choisi = options_map[choix_cle]

    with col_work:
        if 'exo_choisi' in locals() and exo_choisi:
            st.markdown(f"### {exo_choisi['exo_data']['titre']}")
            st.info(exo_choisi['exo_data']['description'])
            
            # C'EST ICI QUE CA CHANGE POUR ÊTRE RAPIDE
            st.write("---")
            if st.button("🚀 Lancer cet exercice", key=f"btn_{exo_choisi['exo_data']['id']}", type="primary", use_container_width=True):
                st.session_state["exercice_actif"] = exo_choisi
                st.switch_page("pages/21_Barlow_Exercice.py")

# 3. BILAN HEBDO (Code inchangé)
with tab_bilan:
    c1, c2 = st.columns([1, 2])
    with c1:
        st.subheader("📝 Bilan Hebdo")
        choix_q = st.radio("Questionnaire :", list(QUESTIONS_HEBDO.keys()), label_visibility="collapsed")
    with c2:
        if choix_q:
            config = QUESTIONS_HEBDO[choix_q]
            with st.container(border=True):
                st.markdown(f"**{config['titre']}**")
                st.caption(config['description'])
                with st.form(f"form_sante_{choix_q}"):
                    reponses = {}; score = 0
                    if config.get("ask_emotion"):
                        emo = st.text_input("Emotion (ex: Colère) :")
                        if emo: reponses["Emotion"] = emo
                    if config['type'] == "scale_0_8":
                        for q in config['questions']:
                            val = st.slider(q, 0, 8, 0)
                            reponses[q] = val; score += val
                    elif config['type'] == "qcm_oasis":
                        for item in config['questions']:
                            lbl = item['label']; res = st.radio(lbl, item['options'])
                            try: score += int(res.split("=")[0])
                            except: pass
                            reponses[lbl] = res
                    if st.form_submit_button("Enregistrer", type="primary"):
                        nom_final = choix_q
                        if config.get("ask_emotion") and "Emotion" in reponses: nom_final += f" ({reponses['Emotion']})"
                        if sauvegarder_reponse_hebdo(current_user, nom_final, str(score), reponses):
                            st.success("Sauvegardé !"); time.sleep(1); st.rerun()

# 4. HISTORIQUE (Code inchangé)
with tab_historique:
    st.subheader("📜 Historique Complet")
    if not df_history.empty:
        st.markdown("#### 📈 Évolution des Scores")
        df_charts = df_history[~df_history["Questionnaire"].str.contains("Exercice", na=False)]
        if not df_charts.empty:
            types = df_charts["Type"].unique().tolist()
            choix = st.multiselect("Afficher :", types, default=types[:2] if types else None)
            if choix:
                df_viz = df_charts[df_charts["Type"].isin(choix)]
                chart = alt.Chart(df_viz).mark_line(point=True).encode(
                    x=alt.X('Date', axis=alt.Axis(format='%d/%m')), y='Score_Global', color='Type', tooltip=['Date', 'Type', 'Score_Global']
                ).properties(height=300).interactive()
                st.altair_chart(chart, use_container_width=True)
            with st.expander("📊 Tableau détaillé"):
                st.dataframe(df_charts[["Date", "Questionnaire", "Score_Global"]].sort_values("Date", ascending=False), use_container_width=True, hide_index=True)
        
        st.divider()
        st.markdown("#### 🛠️ Journal des Exercices")
        df_exos = df_history[df_history["Questionnaire"].str.contains("Exercice", na=False)].copy()
        if not df_exos.empty:
            for idx, row in df_exos.sort_values("Date", ascending=False).iterrows():
                with st.expander(f"🗓️ {row['Date'].strftime('%d/%m')} - {row['Questionnaire']}"):
                    col_del, col_content = st.columns([1, 5])
                    with col_del:
                        if st.button("🗑️ Supprimer", key=f"hist_del_{idx}", type="primary"):
                            supprimer_reponse(current_user, row["Date"], row["Questionnaire"])
                            st.rerun()
                    with col_content:
                        try:
                            d = json.loads(row["Details_Json"])
                            st.json(d) # Affichage simple du JSON pour l'instant pour ne pas surcharger le code
                        except: st.error("Erreur lecture")
        else: st.info("Aucun exercice réalisé.")
    else:
        st.info("Historique vide.")