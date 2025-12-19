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
    """Charge tout l'historique et prépare la colonne 'Type' pour les graphiques"""
    try:
        raw = load_data("Reponses_Hebdo")
        if raw:
            df = pd.DataFrame(raw)
            df = df[df["Patient"] == uid].copy()
            if not df.empty:
                df["Date"] = pd.to_datetime(df["Date"])
                
                # --- CORRECTION ICI : ON CRÉE LA COLONNE 'Type' ---
                # On force le score en numérique
                df["Score_Global"] = pd.to_numeric(df["Score_Global"], errors='coerce')

                def nettoyer_nom(x):
                    s = str(x)
                    # Si c'est lié à un module "module1 - Anxiété", on garde "Anxiété"
                    if " - " in s: 
                        s = s.split(" - ")[1]
                    # On retire les parenthèses de détails "Anxiété (Colère)" -> "Anxiété"
                    return s.split(" (")[0]
                
                df["Type"] = df["Questionnaire"].apply(nettoyer_nom)
                # --------------------------------------------------
                
                return df
    except Exception as e:
        print(f"Erreur chargement histo: {e}")
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
# LA GRANDE NAVIGATION
# =========================================================
tab_parcours, tab_outils, tab_sante = st.tabs([
    "🗺️ Ma Progression",
    "🛠️ Mes Outils & Exercices", 
    "📊 Mon Suivi de Santé" 
])

# =========================================================
# 1. MA PROGRESSION
# =========================================================
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
                        a_faire = False
                        if data['taches_domicile']:
                            for j, dev in enumerate(data['taches_domicile']):
                                if j not in exclus:
                                    a_faire = True
                                    st.markdown(f"👉 **{dev['titre']}**")
                                    if dev.get('pdf') and os.path.exists(dev['pdf']):
                                        with open(dev['pdf'], "rb") as f:
                                            st.download_button("📥 Support", f, file_name=os.path.basename(dev['pdf']), key=f"d_home_{code_mod}_{j}")
                        if not a_faire: st.success("🎉 Rien de spécial.")
                        else:
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
                    else: st.caption("Aucun document.")
        else:
            with st.container():
                st.markdown(f"🔒 **{data['titre']}** _(Verrouillé)_")
                st.divider()


# =========================================================
# 2. MES OUTILS
# =========================================================
# =========================================================
# 2. MES OUTILS (EXERCICES DYNAMIQUES)
# =========================================================
with tab_outils:
    
    # Recherche des exercices disponibles
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
            st.warning("⚠️ Aucun exercice trouvé.")
            st.info("💡 Astuce : Les exercices apparaissent ici une fois que votre thérapeute a débloqué le module correspondant.")
            exo_choisi = None
        else:
            options_map = {f"{x['mod_code']} - {x['exo_data']['titre']}": x for x in liste_exos_dispos}
            choix_cle = st.radio("Exercices disponibles :", list(options_map.keys()))
            exo_choisi = options_map[choix_cle]

    with col_work:
        if exo_choisi:
            exo_data = exo_choisi["exo_data"]
            st.markdown(f"### {exo_data['titre']}")
            st.info(exo_data['description'])
            
            # ---------------------------------------------------------
            # TYPE 1 : FICHE OBJECTIFS (Module 1)
            # ---------------------------------------------------------
            if exo_data["type"] == "fiche_objectifs_traitement":
                if "temp_main_pb" not in st.session_state: st.session_state.temp_main_pb = ""
                if "temp_objectives_list" not in st.session_state: st.session_state.temp_objectives_list = []
                
                st.markdown("#### 1️⃣ Le Problème Principal")
                def update_pb(): st.session_state.temp_main_pb = st.session_state.widget_main_pb
                st.text_area("Votre problème principal :", value=st.session_state.temp_main_pb, height=70, key="widget_main_pb", on_change=update_pb)

                st.divider()
                st.markdown("#### 2️⃣ Ajouter des Objectifs")
                with st.form("form_add_obj", clear_on_submit=True):
                    c_obj, c_step = st.columns(2)
                    with c_obj: new_obj_txt = st.text_input("Nouvel Objectif :")
                    with c_step: new_steps_txt = st.text_area("Étapes (une par ligne) :", height=80)
                    if st.form_submit_button("➕ Ajouter"):
                        if new_obj_txt:
                            st.session_state.temp_objectives_list.append({"objectif": new_obj_txt, "etapes": [s.strip() for s in new_steps_txt.split('\n') if s.strip()]})
                            st.rerun()
                
                if st.session_state.temp_objectives_list:
                    st.markdown("##### 📋 Liste à enregistrer :")
                    for i, item in enumerate(st.session_state.temp_objectives_list):
                        with st.expander(f"🎯 {item['objectif']}", expanded=False):
                            for s in item['etapes']: st.write(f"- {s}")
                            if st.button("Supprimer", key=f"del_obj_{i}"):
                                st.session_state.temp_objectives_list.pop(i)
                                st.rerun()
                    
                    st.divider()
                    if st.button("💾 Sauvegarder définitivement", type="primary"):
                        if not st.session_state.temp_main_pb: st.error("Définissez le problème principal.")
                        else:
                            payload = {
                                "type_exercice": "Objectifs Traitement",
                                "probleme_principal": st.session_state.temp_main_pb,
                                "liste_objectifs": st.session_state.temp_objectives_list
                            }
                            if sauvegarder_reponse_hebdo(current_user, f"Exercice - {exo_data['titre']}", "N/A", payload):
                                st.success("✅ Sauvegardé !"); st.session_state.temp_main_pb = ""; st.session_state.temp_objectives_list = []; time.sleep(1); st.rerun()

            # ---------------------------------------------------------
            # TYPE 2 : FICHE ARC ÉMOTIONNEL (Module 2) - NOUVEAU !
            # ---------------------------------------------------------
            elif exo_data["type"] == "fiche_arc_emotionnel":
                
                # Initialisation liste temporaire
                if "temp_arc_list" not in st.session_state:
                    st.session_state.temp_arc_list = []

                st.markdown("#### ➕ Ajouter une situation")
                st.caption("Décrivez une expérience récente. (Remplissez et cliquez sur 'Ajouter')")

                with st.form("form_add_arc", clear_on_submit=True):
                    
                    # 1. ANTÉCÉDENTS
                    st.markdown("**🅰️ Antécédents (Le Déclencheur)**")
                    col_a1, col_a2 = st.columns([1, 2])
                    with col_a1: 
                        date_evt = st.text_input("Date/Heure :", placeholder="Lundi matin...")
                    with col_a2: 
                        antecedent = st.text_area("Qu'est-ce qui a déclenché l'émotion ?", height=70, placeholder="Situation, événement, pensée...")
                    
                    st.divider()
                    
                    # 2. RÉPONSES (3 Composantes)
                    st.markdown("**⚡ Réponses (L'expérience émotionnelle)**")
                    c_r1, c_r2, c_r3 = st.columns(3)
                    with c_r1: pensees = st.text_area("💭 Pensées", height=100, placeholder="Ce que je me suis dit...")
                    with c_r2: sensations = st.text_area("💓 Sensations", height=100, placeholder="Coeur qui bat, chaleur...")
                    with c_r3: comportements = st.text_area("🏃 Comportements", height=100, placeholder="Ce que j'ai fait (ou évité)...")

                    st.divider()

                    # 3. CONSÉQUENCES
                    st.markdown("**🏁 Conséquences**")
                    c_c1, c_c2 = st.columns(2)
                    with c_c1: c_court = st.text_area("Court terme (Avantages ?)", height=70, placeholder="Soulagement immédiat ?")
                    with c_c2: c_long = st.text_area("Long terme (Inconvénients ?)", height=70, placeholder="Augmentation anxiété future ?")

                    if st.form_submit_button("Ajouter cette situation à ma fiche"):
                        if antecedent:
                            entree = {
                                "date": date_evt,
                                "antecedent": antecedent,
                                "pensees": pensees,
                                "sensations": sensations,
                                "comportements": comportements,
                                "c_court": c_court,
                                "c_long": c_long
                            }
                            st.session_state.temp_arc_list.append(entree)
                            st.rerun()
                        else:
                            st.error("L'antécédent est obligatoire pour comprendre la situation.")

                # AFFICHAGE DE LA LISTE EN COURS
                if st.session_state.temp_arc_list:
                    st.markdown("##### 📋 Situations à enregistrer :")
                    for i, arc in enumerate(st.session_state.temp_arc_list):
                        with st.expander(f"Situation {i+1} : {arc['date']} - {arc['antecedent'][:40]}...", expanded=False):
                            c1, c2, c3 = st.columns(3)
                            with c1: st.info(f"**Antécédent:**\n{arc['antecedent']}")
                            with c2: st.warning(f"**Réponses:**\n💭 {arc['pensees']}\n💓 {arc['sensations']}\n🏃 {arc['comportements']}")
                            with c3: st.error(f"**Conséquences:**\nCT: {arc['c_court']}\nLT: {arc['c_long']}")
                            
                            if st.button("Supprimer", key=f"del_arc_{i}"):
                                st.session_state.temp_arc_list.pop(i)
                                st.rerun()
                    
                    st.divider()
                    if st.button("💾 Sauvegarder définitivement cette fiche ARC", type="primary"):
                        payload = {
                            "type_exercice": "ARC Emotionnel",
                            "liste_arc": st.session_state.temp_arc_list
                        }
                        if sauvegarder_reponse_hebdo(current_user, f"Exercice - {exo_data['titre']}", "N/A", payload):
                            st.success("✅ Fiche ARC sauvegardée dans le cloud !")
                            st.session_state.temp_arc_list = []
                            time.sleep(1)
                            st.rerun()

    # --- HISTORIQUE EXERCICES (LECTURE DU CLOUD) ---
    st.divider()
    with st.expander("📜 Historique de mes exercices réalisés", expanded=False):
        if not df_history.empty and "Questionnaire" in df_history.columns:
            # Filtre pour ne garder que les exercices
            df_exos = df_history[df_history["Questionnaire"].str.contains("Exercice", na=False)].copy()
            if not df_exos.empty:
                for idx, row in df_exos.iterrows():
                    c_d, c_n, c_a = st.columns([1, 3, 1])
                    with c_d: st.write(row["Date"].strftime("%d/%m/%Y"))
                    with c_n: st.write(f"**{row['Questionnaire']}**")
                    with c_a:
                        if st.button("Supprimer", key=f"del_h_{idx}"):
                            supprimer_reponse(current_user, row["Date"], row["Questionnaire"])
                            st.rerun()
                    
                    with st.expander("Voir le détail"):
                        try:
                            d = json.loads(row["Details_Json"])
                            
                            # A. Format ARC Emotionnel
                            if "liste_arc" in d:
                                for arc in d["liste_arc"]:
                                    st.markdown(f"**📅 {arc['date']}**")
                                    # Affichage en colonnes pour la lecture
                                    k1, k2, k3 = st.columns(3)
                                    with k1: 
                                        st.caption("ANTÉCÉDENT")
                                        st.write(arc['antecedent'])
                                    with k2: 
                                        st.caption("RÉPONSES")
                                        st.write(f"💭 {arc['pensees']}")
                                        st.write(f"💓 {arc['sensations']}")
                                        st.write(f"🏃 {arc['comportements']}")
                                    with k3:
                                        st.caption("CONSÉQUENCES")
                                        st.write(f"CT: {arc['c_court']}")
                                        st.write(f"LT: {arc['c_long']}")
                                    st.divider()

                            # B. Format Objectifs
                            elif "probleme_principal" in d:
                                st.info(f"**Problème :** {d['probleme_principal']}")
                                if "liste_objectifs" in d:
                                    for it in d["liste_objectifs"]:
                                        st.markdown(f"**🎯 {it['objectif']}**")
                                        for s in it.get('etapes', []): st.write(f"- {s}")
                                        st.write("---")
                            
                            # C. Format Brut (Fallback)
                            else: st.json(d)
                        except: st.write("Erreur lecture.")
            else: st.info("Aucun exercice sauvegardé.")
        else: st.info("Historique vide.")

# =========================================================
# 3. MON SUIVI DE SANTÉ
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
    
    if not df_history.empty and "Type" in df_history.columns:
        # On exclut les exercices de l'affichage graphique
        types_graph = [t for t in df_history["Type"].unique() if "Exercice" not in str(t)]
        
        if types_graph:
            sel_graph = st.multiselect("Afficher :", types_graph, default=types_graph[:2])
            
            if sel_graph:
                sub_df = df_history[df_history["Type"].isin(sel_graph)]
                chart = alt.Chart(sub_df).mark_line(point=True).encode(
                    x=alt.X('Date', axis=alt.Axis(format='%d/%m')), 
                    y='Score_Global', 
                    color='Type', 
                    tooltip=['Date', 'Score_Global']
                ).interactive()
                st.altair_chart(chart, use_container_width=True)
            else:
                st.info("Sélectionnez une courbe ci-dessus.")
        else:
            st.info("Aucune donnée chiffrée (questionnaires) disponible.")
    else:
        st.info("Historique vide. Remplissez un questionnaire pour voir vos progrès !")