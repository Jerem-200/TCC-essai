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
    def charger_progression(uid): return ["module0"] 
    def charger_etat_devoirs(uid): return {}

# --- CHARGEMENT DONNÉES ---
modules_debloques = charger_progression(current_user)
devoirs_exclus = charger_etat_devoirs(current_user)
df_history = charger_historique_complet(current_user)

st.title(f"Espace Patient - {current_user}")

# =========================================================
# LA GRANDE NAVIGATION (ORDRE MODIFIÉ)
# =========================================================
# Ma Progression est maintenant en PREMIER
tab_parcours, tab_outils, tab_sante = st.tabs([
    "🗺️ Ma Progression",
    "🛠️ Mes Outils & Exercices", 
    "📊 Mon Suivi de Santé" 
])

# =========================================================
# 1. MA PROGRESSION (RETOUR À L'ANCIEN DESIGN)
# =========================================================
with tab_parcours:
    st.markdown("### 📍 Mon cheminement")
    
    # On boucle sur tous les modules du protocole
    for code_mod, data in PROTOCOLE_BARLOW.items():
        
        # On affiche si débloqué
        if code_mod in modules_debloques:
            
            with st.expander(f"✅ {data['titre']}", expanded=False):
                
                # Sous-onglets internes au module
                t_seance, t_doc = st.tabs(["📖 Résumé Séance", "📂 Documents"])
                
                # --- A. RÉSUMÉ SÉANCE (AVEC COLONNES) ---
                with t_seance:
                    st.info(f"**Objectifs :** {data['objectifs']}")
                    
                    # Les 2 colonnes que vous aimiez bien
                    col_step, col_home = st.columns(2)
                    
                    with col_step:
                        st.markdown("#### 📝 Ce que nous avons vu")
                        if data['etapes_seance']:
                            for etape in data['etapes_seance']:
                                st.markdown(f"- **{etape['titre']}**")
                                if etape.get('details'):
                                    st.caption(f"_{etape.get('details')}_")
                        else:
                            st.caption("Introduction / Pas d'étapes listées.")
                    
                    with col_home:
                        st.markdown("#### 🏠 Travail à la maison")
                        exclus = devoirs_exclus.get(code_mod, [])
                        a_faire = False
                        
                        if data['taches_domicile']:
                            for j, dev in enumerate(data['taches_domicile']):
                                if j not in exclus:
                                    a_faire = True
                                    st.markdown(f"👉 **{dev['titre']}**")
                                    # Bouton téléchargement immédiat
                                    if dev.get('pdf') and os.path.exists(dev['pdf']):
                                        with open(dev['pdf'], "rb") as f:
                                            st.download_button("📥 Support", f, file_name=os.path.basename(dev['pdf']), key=f"d_home_{code_mod}_{j}")
                        
                        if not a_faire:
                            st.success("🎉 Rien de spécial pour la prochaine fois.")
                        else:
                            st.write("")
                            with st.expander("📸 Envoyer une photo"):
                                st.camera_input("Photo", key=f"cam_{code_mod}")

                # --- B. DOCUMENTS ---
                with t_doc:
                    st.write("Tous les fichiers du module :")
                    if data.get('pdfs_module'):
                        for p in data['pdfs_module']:
                            if os.path.exists(p):
                                with open(p, "rb") as f:
                                    st.download_button(f"📥 {os.path.basename(p)}", f, file_name=os.path.basename(p), key=f"da_{code_mod}_{os.path.basename(p)}")
                    else:
                        st.caption("Aucun document.")

        else:
            # Module verrouillé
            with st.container():
                st.markdown(f"🔒 **{data['titre']}** _(Verrouillé)_")
                st.divider()


# =========================================================
# 2. MES OUTILS (EXERCICES DYNAMIQUES)
# =========================================================
with tab_outils:
    
    # A. SÉLECTEUR D'EXERCICE
    # On cherche tous les exercices disponibles DANS LES MODULES DÉBLOQUÉS
    liste_exos_dispos = []
    
    for m in modules_debloques:
        # On vérifie si le module existe dans la config ET s'il a une liste 'exercices'
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
            st.warning("⚠️ Aucun exercice trouvé.")
            st.caption("Les exercices apparaîtront ici quand vous débloquerez les modules correspondants (ex: Module 1).")
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
                
                # 1. Initialisation session
                if "temp_objectives" not in st.session_state:
                    st.session_state.temp_objectives = []
                
                # 2. Formulaire d'ajout
                with st.container(border=True):
                    st.markdown("#### ➕ Ajouter un nouvel objectif")
                    
                    c_in1, c_in2 = st.columns(2)
                    with c_in1:
                        new_pb = st.text_area("Problème lié :", height=70, placeholder="Ex: Anxiété sociale")
                    with c_in2:
                        new_obj = st.text_area("Objectif concret :", height=70, placeholder="Ex: Parler à un collègue")
                    
                    new_steps = st.text_area("Étapes (une par ligne) :", height=70, placeholder="1. Dire bonjour\n2. Poser une question...")
                    
                    if st.button("Ajouter à la liste"):
                        if new_obj:
                            st.session_state.temp_objectives.append({
                                "probleme": new_pb,
                                "objectif": new_obj,
                                "etapes": new_steps.split('\n')
                            })
                            st.rerun()
                        else:
                            st.error("L'objectif est vide.")

                # 3. Affichage liste
                st.markdown("#### 📋 Votre liste :")
                if st.session_state.temp_objectives:
                    for i, item in enumerate(st.session_state.temp_objectives):
                        with st.expander(f"{i+1}. {item['objectif']}", expanded=True):
                            st.write(f"**Pb:** {item['probleme']}")
                            for s in item['etapes']:
                                if s.strip(): st.write(f"- {s}")
                            if st.button("Supprimer", key=f"del_tmp_{i}"):
                                st.session_state.temp_objectives.pop(i)
                                st.rerun()
                    
                    st.divider()
                    if st.button("💾 Sauvegarder l'exercice", type="primary"):
                        payload = {"type_exercice": "Objectifs Traitement", "contenu": st.session_state.temp_objectives}
                        nom_save = f"Exercice - {exo_data['titre']}"
                        if sauvegarder_reponse_hebdo(current_user, nom_save, "N/A", payload):
                            st.success("Sauvegardé !")
                            st.session_state.temp_objectives = [] 
                            time.sleep(1)
                            st.rerun()
                else:
                    st.caption("Liste vide.")

    # --- HISTORIQUE EXERCICES ---
    st.divider()
    with st.expander("📜 Historique de mes exercices réalisés", expanded=False):
        if not df_history.empty:
            # On filtre pour ne garder que ce qui contient "Exercice"
            df_exos = df_history[df_history["Questionnaire"].str.contains("Exercice", na=False)].copy()
            
            if not df_exos.empty:
                for idx, row in df_exos.iterrows():
                    c_d, c_n, c_a = st.columns([1, 3, 1])
                    with c_d: st.write(row["Date"].strftime("%d/%m"))
                    with c_n: st.write(f"**{row['Questionnaire']}**")
                    with c_a:
                        if st.button("Supprimer", key=f"del_h_{idx}"):
                            supprimer_reponse(current_user, row["Date"], row["Questionnaire"])
                            st.rerun()
                    
                    with st.expander("Voir le détail"):
                        try:
                            d = json.loads(row["Details_Json"])
                            if "contenu" in d:
                                for it in d["contenu"]:
                                    st.markdown(f"**🎯 {it['objectif']}**")
                                    st.caption(f"Pb: {it['probleme']}")
                                    for s in it.get('etapes', []): st.write(f"- {s}")
                                    st.write("---")
                            else: st.json(d)
                        except: st.write("Erreur lecture.")
            else: st.info("Aucun exercice sauvegardé.")


# =========================================================
# 3. MON SUIVI DE SANTÉ (QUESTIONNAIRES)
# =========================================================
with tab_sante:
    c1, c2 = st.columns([1, 2])
    
    with c1:
        st.subheader("📝 Bilan Hebdo")
        st.info("Sélectionnez une échelle à remplir :")
        choix_q = st.radio("Questionnaire :", list(QUESTIONS_HEBDO.keys()), label_visibility="collapsed")
    
    with c2:
        if choix_q:
            config = QUESTIONS_HEBDO[choix_q]
            with st.container(border=True):
                st.markdown(f"**{config['titre']}**")
                st.caption(config['description'])
                
                with st.form(f"form_sante_{choix_q}"):
                    reponses = {}
                    score = 0
                    
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
                            # On gère l'affichage dynamique si émotion spécifiée
                            lbl = item['label']
                            res = st.radio(lbl, item['options'])
                            try: score += int(res.split("=")[0])
                            except: pass
                            reponses[lbl] = res
                    
                    if st.form_submit_button("Enregistrer", type="primary"):
                        nom_final = choix_q
                        if config.get("ask_emotion") and "Emotion" in reponses:
                            nom_final += f" ({reponses['Emotion']})"
                            
                        if sauvegarder_reponse_hebdo(current_user, nom_final, str(score), reponses):
                            st.success("Sauvegardé !")
                            time.sleep(1)
                            st.rerun()
    
    st.divider()
    st.subheader("📈 Mes Courbes")
    if not df_history.empty:
        # On exclut les exercices de l'affichage graphique
        types_graph = [t for t in df_history["Type"].unique() if "Exercice" not in t]
        sel_graph = st.multiselect("Afficher :", types_graph, default=types_graph[:2] if types_graph else None)
        
        if sel_graph:
            sub_df = df_history[df_history["Type"].isin(sel_graph)]
            chart = alt.Chart(sub_df).mark_line(point=True).encode(
                x=alt.X('Date', axis=alt.Axis(format='%d/%m')), 
                y='Score_Global', 
                color='Type', 
                tooltip=['Date', 'Score_Global']
            ).interactive()
            st.altair_chart(chart, use_container_width=True)