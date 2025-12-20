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
    """Charge tout l'historique et prépare la colonne 'Type'"""
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
# LA GRANDE NAVIGATION (4 ONGLETS)
# =========================================================
tab_parcours, tab_outils, tab_bilan, tab_historique = st.tabs([
    "🗺️ Ma Progression",
    "🛠️ Mes Outils", 
    "📝 Bilan Hebdo",
    "📜 Mon Historique"
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
                        else: st.caption("Introduction / Pas d'étapes listées.")
                    
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
# 2. MES OUTILS (ACTION UNIQUEMENT)
# =========================================================
with tab_outils:
    
    # Recherche des exercices
    liste_exos_dispos = []
    for m in modules_debloques:
        if m in PROTOCOLE_BARLOW and "exercices" in PROTOCOLE_BARLOW[m]:
            for exo in PROTOCOLE_BARLOW[m]["exercices"]:
                liste_exos_dispos.append({
                    "mod_code": m,
                    "mod_titre": PROTOCOLE_BARLOW[m]["titre"],
                    "exo_data": exo
                })
    # Tri logique
    liste_exos_dispos.sort(key=lambda x: x['mod_code'])
    
    col_menu, col_work = st.columns([1, 2])
    
    with col_menu:
        st.subheader("Choix de l'outil")
        if not liste_exos_dispos:
            st.warning("⚠️ Aucun exercice trouvé.")
            st.info("Les exercices apparaîtront ici quand vous débloquerez les modules.")
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
            
            # --- TOUS LES FORMULAIRES D'EXERCICES ---
            
            # 1. FICHE OBJECTIFS
            if exo_data["type"] == "fiche_objectifs_traitement":
                if "temp_main_pb" not in st.session_state: st.session_state.temp_main_pb = ""
                if "temp_objectives_list" not in st.session_state: st.session_state.temp_objectives_list = []
                
                st.markdown("#### 1️⃣ Le Problème Principal")
                def update_pb(): st.session_state.temp_main_pb = st.session_state.widget_main_pb
                st.text_area("Problème :", value=st.session_state.temp_main_pb, height=70, key="widget_main_pb", on_change=update_pb)
                st.divider()
                st.markdown("#### 2️⃣ Ajouter des Objectifs")
                with st.form("form_add_obj", clear_on_submit=True):
                    c_o1, c_o2 = st.columns(2)
                    with c_o1: new_obj = st.text_input("Objectif :")
                    with c_o2: new_steps = st.text_area("Étapes :", height=80)
                    if st.form_submit_button("➕ Ajouter"):
                        st.session_state.temp_objectives_list.append({"objectif": new_obj, "etapes": [s.strip() for s in new_steps.split('\n') if s.strip()]})
                        st.rerun()
                
                if st.session_state.temp_objectives_list:
                    st.markdown("##### 📋 Liste :")
                    for i, it in enumerate(st.session_state.temp_objectives_list):
                        st.write(f"🎯 **{it['objectif']}**"); st.caption(str(it['etapes']))
                    if st.button("💾 Sauvegarder", type="primary"):
                        payload = {"type_exercice": "Objectifs Traitement", "probleme_principal": st.session_state.temp_main_pb, "liste_objectifs": st.session_state.temp_objectives_list}
                        if sauvegarder_reponse_hebdo(current_user, f"Exercice - {exo_data['titre']}", "N/A", payload):
                            st.toast("✅ Sauvegardé !", icon="🎉"); st.session_state.temp_main_pb = ""; st.session_state.temp_objectives_list = []; st.rerun()

            # 2. ARC EMOTIONNEL
            elif exo_data["type"] == "fiche_arc_emotionnel":
                if "temp_arc_list" not in st.session_state: st.session_state.temp_arc_list = []
                st.markdown("#### ➕ Ajouter une situation")
                with st.form("form_add_arc", clear_on_submit=True):
                    c1, c2 = st.columns([1, 2]); c1.text_input("Date", key="arc_d"); c2.text_area("Déclencheur", key="arc_a", height=70)
                    r1, r2, r3 = st.columns(3); r1.text_area("Pensées", key="arc_p"); r2.text_area("Sensations", key="arc_s"); r3.text_area("Comportements", key="arc_c")
                    k1, k2 = st.columns(2); k1.text_area("Csq Court terme", key="arc_cc"); k2.text_area("Csq Long terme", key="arc_cl")
                    if st.form_submit_button("Ajouter"):
                        st.session_state.temp_arc_list.append({"date": st.session_state.arc_d, "antecedent": st.session_state.arc_a, "pensees": st.session_state.arc_p, "sensations": st.session_state.arc_s, "comportements": st.session_state.arc_c, "c_court": st.session_state.arc_cc, "c_long": st.session_state.arc_cl})
                        st.rerun()
                
                if st.session_state.temp_arc_list:
                    st.write(f"📋 {len(st.session_state.temp_arc_list)} situations prêtes.")
                    if st.button("💾 Sauvegarder ARC", type="primary"):
                        payload = {"type_exercice": "ARC Emotionnel", "liste_arc": st.session_state.temp_arc_list}
                        if sauvegarder_reponse_hebdo(current_user, f"Exercice - {exo_data['titre']}", "N/A", payload):
                            st.toast("✅ Sauvegardé !", icon="🎉"); st.session_state.temp_arc_list = []; st.rerun()

            # 3. PLEINE CONSCIENCE
            elif exo_data["type"] == "fiche_pleine_conscience":
                if "temp_mindfulness_list" not in st.session_state: st.session_state.temp_mindfulness_list = []
                st.markdown("#### ➕ Pratique")
                with st.form("form_pc", clear_on_submit=True):
                    c1, c2 = st.columns([1, 2]); c1.text_input("Date", key="pc_d"); c2.selectbox("Exercice", ["Initiation", "Induction", "Ancrage"], key="pc_t")
                    o1, o2, o3 = st.columns(3); o1.text_area("Pensées", key="pc_p"); o2.text_area("Sensations", key="pc_s"); o3.text_area("Actions", key="pc_a")
                    s1, s2 = st.columns(2); s1.slider("Non-jugement", 0, 10, 5, key="pc_sj"); s2.slider("Ancrage", 0, 10, 5, key="pc_sa")
                    if st.form_submit_button("Ajouter"):
                        st.session_state.temp_mindfulness_list.append({"date": st.session_state.pc_d, "type_exo": st.session_state.pc_t, "pensees": st.session_state.pc_p, "sensations": st.session_state.pc_s, "comportements": st.session_state.pc_a, "score_jugement": st.session_state.pc_sj, "score_ancrage": st.session_state.pc_sa})
                        st.rerun()
                
                if st.session_state.temp_mindfulness_list:
                    st.write(f"📋 {len(st.session_state.temp_mindfulness_list)} pratiques.")
                    if st.button("💾 Sauvegarder", type="primary"):
                        payload = {"type_exercice": "Pleine Conscience", "liste_pratiques": st.session_state.temp_mindfulness_list}
                        if sauvegarder_reponse_hebdo(current_user, f"Exercice - {exo_data['titre']}", "N/A", payload):
                            st.toast("✅ Sauvegardé !", icon="🎉"); st.session_state.temp_mindfulness_list = []; st.rerun()

            # 4. FLEXIBILITÉ
            elif exo_data["type"] == "fiche_flexibilite_cognitive":
                if "temp_flex_list" not in st.session_state: st.session_state.temp_flex_list = []
                st.markdown("#### ➕ Analyse")
                with st.form("form_flex", clear_on_submit=True):
                    c1, c2 = st.columns(2); c1.text_area("Déclencheur", key="fl_d"); c2.text_area("Pensée", key="fl_p")
                    c3, c4 = st.columns(2); c3.text_input("Piège", key="fl_pi"); c3.slider("Croyance", 0, 100, 80, key="fl_cr"); c4.text_area("Alternative", key="fl_al")
                    if st.form_submit_button("Ajouter"):
                        st.session_state.temp_flex_list.append({"declencheur": st.session_state.fl_d, "pensee": st.session_state.fl_p, "piege": st.session_state.fl_pi, "croyance": st.session_state.fl_cr, "alternative": st.session_state.fl_al})
                        st.rerun()
                
                if st.session_state.temp_flex_list:
                    st.write(f"📋 {len(st.session_state.temp_flex_list)} analyses.")
                    if st.button("💾 Sauvegarder", type="primary"):
                        payload = {"type_exercice": "Flexibilité Cognitive", "liste_flexibilite": st.session_state.temp_flex_list}
                        if sauvegarder_reponse_hebdo(current_user, f"Exercice - {exo_data['titre']}", "N/A", payload):
                            st.toast("✅ Sauvegardé !", icon="🎉"); st.session_state.temp_flex_list = []; st.rerun()

            # 5. CONTRER COMPORTEMENTS
            elif exo_data["type"] == "fiche_contrer_comportements":
                if "temp_behavior_list" not in st.session_state: st.session_state.temp_behavior_list = []
                st.markdown("#### ➕ Analyse")
                with st.form("form_beh", clear_on_submit=True):
                    c1, c2 = st.columns(2); c1.text_area("Situation", key="bh_s"); c2.text_input("Emotion", key="bh_e")
                    c3, c4 = st.columns(2); c3.text_area("Habitude", key="bh_h"); c4.text_area("Alternative", key="bh_a")
                    c5, c6 = st.columns(2); c5.text_area("Csq Court", key="bh_cc"); c6.text_area("Csq Long", key="bh_cl")
                    if st.form_submit_button("Ajouter"):
                        st.session_state.temp_behavior_list.append({"situation": st.session_state.bh_s, "emotion": st.session_state.bh_e, "comp_habituel": st.session_state.bh_h, "comp_alternatif": st.session_state.bh_a, "cons_court": st.session_state.bh_cc, "cons_long": st.session_state.bh_cl})
                        st.rerun()
                
                if st.session_state.temp_behavior_list:
                    if st.button("💾 Sauvegarder", type="primary"):
                        payload = {"type_exercice": "Contrer Comportements", "liste_comportements": st.session_state.temp_behavior_list}
                        if sauvegarder_reponse_hebdo(current_user, f"Exercice - {exo_data['titre']}", "N/A", payload):
                            st.toast("✅ Sauvegardé !", icon="🎉"); st.session_state.temp_behavior_list = []; st.rerun()

            # 6. SENSATIONS
            elif exo_data["type"] == "fiche_sensations_physiques":
                if "temp_sensations_list" not in st.session_state: st.session_state.temp_sensations_list = []
                st.markdown("#### 🌪️ Test")
                with st.form("form_sens", clear_on_submit=True):
                    sel = st.selectbox("Exercice", ["Hyperventilation", "Paille", "Tourner", "Courir", "Autre"], key="sn_t")
                    st.text_area("Symptômes", key="sn_s")
                    c1, c2 = st.columns(2); c1.slider("Malaise", 0, 10, 0, key="sn_m"); c2.slider("Ressemblance", 0, 10, 0, key="sn_r")
                    if st.form_submit_button("Ajouter"):
                        st.session_state.temp_sensations_list.append({"exercice": sel, "symptomes": st.session_state.sn_s, "score_malaise": st.session_state.sn_m, "score_resemblance": st.session_state.sn_r})
                        st.rerun()
                
                if st.session_state.temp_sensations_list:
                    if st.button("💾 Sauvegarder", type="primary"):
                        payload = {"type_exercice": "Sensations Physiques", "liste_tests": st.session_state.temp_sensations_list}
                        if sauvegarder_reponse_hebdo(current_user, f"Exercice - {exo_data['titre']}", "N/A", payload):
                            st.toast("✅ Sauvegardé !", icon="🎉"); st.session_state.temp_sensations_list = []; st.rerun()

            # 7. HIERARCHIE
            elif exo_data["type"] == "fiche_hierarchie_exposition":
                if "temp_hierarchy_list" not in st.session_state: st.session_state.temp_hierarchy_list = []
                st.markdown("#### 📈 Situation")
                with st.form("form_hier", clear_on_submit=True):
                    c1, c2 = st.columns([1, 3]); c1.number_input("Rang", 1, 100, 1, key="hr_r"); c2.text_area("Situation", key="hr_s")
                    c3, c4 = st.columns(2); c3.slider("Evitement", 0, 10, 5, key="hr_e"); c4.slider("Détresse", 0, 10, 5, key="hr_d")
                    if st.form_submit_button("Ajouter"):
                        st.session_state.temp_hierarchy_list.append({"rang": st.session_state.hr_r, "situation": st.session_state.hr_s, "score_evit": st.session_state.hr_e, "score_detr": st.session_state.hr_d})
                        st.session_state.temp_hierarchy_list.sort(key=lambda x: x["rang"])
                        st.rerun()
                
                if st.session_state.temp_hierarchy_list:
                    st.write(f"📋 {len(st.session_state.temp_hierarchy_list)} situations.")
                    if st.button("💾 Sauvegarder", type="primary"):
                        payload = {"type_exercice": "Hiérarchie Exposition", "liste_hierarchie": st.session_state.temp_hierarchy_list}
                        if sauvegarder_reponse_hebdo(current_user, f"Exercice - {exo_data['titre']}", "N/A", payload):
                            st.toast("✅ Sauvegardé !", icon="🎉"); st.session_state.temp_hierarchy_list = []; st.rerun()

            # 8. ENREGISTREMENT EXPO
            elif exo_data["type"] == "fiche_enregistrement_exposition":
                st.markdown("#### 🎬 Séance")
                with st.form("form_expo"):
                    st.caption("Préparation")
                    c1, c2 = st.columns([1, 3]); c1.text_input("Date", key="ex_d"); c2.text_area("Exercice", key="ex_a")
                    c3, c4 = st.columns(2); c3.text_area("Pensées/Comport. Négatifs", key="ex_n"); c4.text_area("Alternatifs", key="ex_p")
                    st.caption("Débriefing")
                    st.text_input("Emotions", key="ex_e")
                    d1, d2 = st.columns(2); d1.text_area("Observations", key="ex_o"); d2.text_area("Apprentissages", key="ex_ap")
                    s1, s2, s3 = st.columns(3); s1.slider("PC", 0, 10, 5, key="ex_s1"); s2.slider("Flex", 0, 10, 5, key="ex_s2"); s3.slider("Action", 0, 10, 5, key="ex_s3")
                    
                    if st.form_submit_button("💾 Enregistrer"):
                        payload = {
                            "type_exercice": "Enregistrement Exposition", "date": st.session_state.ex_d, "activite": st.session_state.ex_a,
                            "preparation": {"neg": st.session_state.ex_n, "pos": st.session_state.ex_p},
                            "debrief": {"emotions": st.session_state.ex_e, "obs": st.session_state.ex_o, "appris": st.session_state.ex_ap, "scores": [st.session_state.ex_s1, st.session_state.ex_s2, st.session_state.ex_s3]}
                        }
                        if sauvegarder_reponse_hebdo(current_user, f"Exercice - {exo_data['titre']}", "N/A", payload):
                            st.toast("✅ Sauvegardé !", icon="🎉"); st.rerun()

            # 9. EVALUATION PROGRES
            elif exo_data["type"] == "fiche_evaluation_progres":
                st.markdown("#### 🏆 Bilan")
                with st.form("form_bilan"):
                    st.text_area("Pleine Conscience (Progrès/Futur)", key="bi_1")
                    st.text_area("Flexibilité (Progrès/Futur)", key="bi_2")
                    st.text_area("Sensations (Progrès/Futur)", key="bi_3")
                    st.text_area("Comportements (Progrès/Futur)", key="bi_4")
                    if st.form_submit_button("💾 Enregistrer"):
                        payload = {"type_exercice": "Evaluation Progres", "data": [st.session_state.bi_1, st.session_state.bi_2, st.session_state.bi_3, st.session_state.bi_4]}
                        if sauvegarder_reponse_hebdo(current_user, f"Exercice - {exo_data['titre']}", "N/A", payload):
                            st.toast("✅ Sauvegardé !", icon="🎉"); st.rerun()

            # 10. PLAN MAINTIEN
            elif exo_data["type"] == "fiche_plan_maintien":
                st.markdown("#### 📅 Plan")
                with st.form("form_plan"):
                    t1, t2, t3, t4 = st.tabs(["PC", "Flex", "Sens", "Comp"])
                    with t1: st.text_area("Plan PC", key="pl_1")
                    with t2: st.text_area("Plan Flex", key="pl_2")
                    with t3: st.text_area("Plan Sens", key="pl_3")
                    with t4: st.text_area("Plan Comp", key="pl_4")
                    if st.form_submit_button("💾 Enregistrer"):
                        payload = {"type_exercice": "Plan Maintien", "data": [st.session_state.pl_1, st.session_state.pl_2, st.session_state.pl_3, st.session_state.pl_4]}
                        if sauvegarder_reponse_hebdo(current_user, f"Exercice - {exo_data['titre']}", "N/A", payload):
                            st.toast("✅ Sauvegardé !", icon="🎉"); st.rerun()


# =========================================================
# 3. BILAN HEBDO (ACTION UNIQUEMENT)
# =========================================================
with tab_bilan:
    col_select, col_form = st.columns([1, 2])
    
    with col_select:
        st.info("Sélectionnez le questionnaire :")
        choix_q = st.radio("Questionnaire :", list(QUESTIONS_HEBDO.keys()))
    
    with col_form:
        if choix_q:
            config_q = QUESTIONS_HEBDO[choix_q]
            with st.form(key=f"form_global_{choix_q}"):
                st.markdown(f"#### {config_q['titre']}")
                st.caption(config_q['description'])
                st.divider()
                
                reponses = {}
                score_total = 0
                nom_emotion = ""

                if config_q.get("ask_emotion"):
                    nom_emotion = st.text_input("Émotion concernée (ex: Colère, Honte) :")
                    if nom_emotion: reponses["Emotion"] = nom_emotion
                
                if config_q['type'] == "qcm_oasis":
                    for item in config_q['questions']:
                        st.markdown(f"**{item['label']}**")
                        choix = st.radio("Rép", item['options'], key=f"g_rad_{choix_q}_{item['id']}", label_visibility="collapsed")
                        try: score_total += int(choix.split("=")[0].strip())
                        except: pass
                        reponses[item['label']] = choix

                st.write("")
                
                if st.form_submit_button("Envoyer le bilan", type="primary"):
                    if config_q.get("ask_emotion") and not nom_emotion:
                        st.error("Indiquez l'émotion.")
                    else:
                        nom_final = choix_q
                        if nom_emotion: nom_final += f" ({nom_emotion})"

                        if sauvegarder_reponse_hebdo(current_user, nom_final, str(score_total), reponses):
                            st.toast("✅ Bilan enregistré !", icon="🎉")
                            time.sleep(0.5)
                            st.rerun()


# =========================================================
# 4. MON HISTORIQUE (CONSULTATION)
# =========================================================
with tab_historique:
    st.subheader("📜 Historique Complet")
    
    if not df_history.empty:
        
        # --- A. GRAPHIQUES ---
        st.markdown("#### 📈 Évolution des Scores")
        # On filtre pour ne garder que les questionnaires (pas les exercices)
        df_charts = df_history[~df_history["Questionnaire"].str.contains("Exercice", na=False)]
        
        if not df_charts.empty:
            types_dispos = df_charts["Type"].unique().tolist()
            choix_types = st.multiselect("Afficher les courbes de :", types_dispos, default=types_dispos[:2] if len(types_dispos)>0 else None)
            
            if choix_types:
                df_viz = df_charts[df_charts["Type"].isin(choix_types)]
                chart = alt.Chart(df_viz).mark_line(point=True).encode(
                    x=alt.X('Date', axis=alt.Axis(format='%d/%m')),
                    y='Score_Global',
                    color='Type',
                    tooltip=['Date', 'Type', 'Score_Global']
                ).properties(height=300).interactive()
                st.altair_chart(chart, use_container_width=True)
        else:
            st.info("Aucun questionnaire rempli pour le moment.")

        st.divider()

        # --- B. TABLEAU DÉTAILLÉ (Questionnaires) ---
        with st.expander("📊 Voir le tableau des scores (Questionnaires)", expanded=False):
            if not df_charts.empty:
                st.dataframe(
                    df_charts[["Date", "Questionnaire", "Score_Global"]].sort_values("Date", ascending=False),
                    use_container_width=True,
                    hide_index=True
                )
            else: st.write("Rien à afficher.")

        st.divider()

        # --- C. JOURNAL DES EXERCICES ---
        st.markdown("#### 🛠️ Journal des Exercices")
        # On filtre pour ne garder QUE les exercices
        df_exos = df_history[df_history["Questionnaire"].str.contains("Exercice", na=False)].copy()
        
        if not df_exos.empty:
            for idx, row in df_exos.sort_values("Date", ascending=False).iterrows():
                with st.expander(f"{row['Date'].strftime('%d/%m')} - {row['Questionnaire']}"):
                    col_del, col_content = st.columns([1, 5])
                    with col_del:
                        if st.button("Supprimer", key=f"hist_del_{idx}"):
                            supprimer_reponse(current_user, row["Date"], row["Questionnaire"])
                            st.rerun()
                    
                    with col_content:
                        try:
                            d = json.loads(row["Details_Json"])
                            # Affichage brut mais lisible du JSON pour l'instant (ou logique spécifique si besoin)
                            if "probleme_principal" in d: # Objectifs
                                st.write(f"**Problème:** {d['probleme_principal']}")
                                for o in d.get('liste_objectifs', []): st.write(f"- {o['objectif']}")
                            elif "liste_arc" in d: # ARC
                                for a in d['liste_arc']: st.write(f"**{a['antecedent']}** -> {a['pensees']}")
                            elif "liste_pratiques" in d: # PC
                                for p in d['liste_pratiques']: st.write(f"🧘 {p['type_exo']} : {p['pensees']}")
                            elif "liste_flexibilite" in d: # Flex
                                for f in d['liste_flexibilite']: st.write(f"🔴 {f['pensee']} -> 🟢 {f['alternative']}")
                            elif "liste_comportements" in d: # Comport
                                for c in d['liste_comportements']: st.write(f"🔴 {c['comp_habituel']} -> 🟢 {c['comp_alternatif']}")
                            elif "liste_tests" in d: # Sensations
                                for t in d['liste_tests']: st.write(f"🌪️ {t['exercice']} (Malaise: {t['score_malaise']})")
                            elif "liste_hierarchie" in d: # Hierarchie
                                for h in d['liste_hierarchie']: st.write(f"{h['rang']}. {h['situation']}")
                            elif "activite" in d: # Enreg Expo
                                st.write(f"🎬 {d['activite']}")
                            elif "pleine_conscience" in d: # Bilan/Plan
                                st.write("Bilan complet enregistré.")
                            else:
                                st.json(d)
                        except: st.write("Détails non lisibles.")
        else:
            st.info("Aucun exercice réalisé pour le moment.")

    else:
        st.info("Votre historique est vide. Commencez par remplir un bilan ou un exercice !")