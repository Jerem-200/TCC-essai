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
# 2. MES OUTILS (EXERCICES DYNAMIQUES)
# =========================================================
with tab_outils:
    
    # Recherche des exercices disponibles dans les modules débloqués
    liste_exos_dispos = []
    for m in modules_debloques:
        if m in PROTOCOLE_BARLOW and "exercices" in PROTOCOLE_BARLOW[m]:
            for exo in PROTOCOLE_BARLOW[m]["exercices"]:
                liste_exos_dispos.append({
                    "mod_code": m,
                    "mod_titre": PROTOCOLE_BARLOW[m]["titre"],
                    "exo_data": exo
                })

    # On trie par le code du module (module0, module1, module2...) pour garantir l'ordre
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
                                # 1. On vide les variables d'abord
                                st.session_state.temp_main_pb = ""
                                st.session_state.temp_objectives_list = []
                                
                                # 2. On lance la notification (qui survivra au rerun)
                                st.toast("✅ Exercice sauvegardé avec succès !", icon='🎉')
                                
                                # 3. On recharge immédiatement sans attendre
                                st.rerun()
            # ---------------------------------------------------------
            # TYPE 2 : FICHE ARC ÉMOTIONNEL (Module 2)
            # ---------------------------------------------------------
            elif exo_data["type"] == "fiche_arc_emotionnel":
                if "temp_arc_list" not in st.session_state: st.session_state.temp_arc_list = []

                st.markdown("#### ➕ Ajouter une situation")
                with st.form("form_add_arc", clear_on_submit=True):
                    st.markdown("**🅰️ Antécédents**")
                    col_a1, col_a2 = st.columns([1, 2])
                    with col_a1: date_evt = st.text_input("Date/Heure :")
                    with col_a2: antecedent = st.text_area("Déclencheur :", height=70)
                    
                    st.markdown("**⚡ Réponses**")
                    c_r1, c_r2, c_r3 = st.columns(3)
                    with c_r1: pensees = st.text_area("💭 Pensées", height=80)
                    with c_r2: sensations = st.text_area("💓 Sensations", height=80)
                    with c_r3: comportements = st.text_area("🏃 Comportements", height=80)

                    st.markdown("**🏁 Conséquences**")
                    c_c1, c_c2 = st.columns(2)
                    with c_c1: c_court = st.text_area("Court terme", height=60)
                    with c_c2: c_long = st.text_area("Long terme", height=60)

                    if st.form_submit_button("Ajouter"):
                        if antecedent:
                            st.session_state.temp_arc_list.append({
                                "date": date_evt, "antecedent": antecedent, "pensees": pensees,
                                "sensations": sensations, "comportements": comportements,
                                "c_court": c_court, "c_long": c_long
                            })
                            st.rerun()

                if st.session_state.temp_arc_list:
                    st.markdown("##### 📋 Situations :")
                    for i, arc in enumerate(st.session_state.temp_arc_list):
                        with st.expander(f"{arc['date']} - {arc['antecedent'][:30]}...", expanded=False):
                            st.write(f"**Déclencheur:** {arc['antecedent']}")
                            st.caption(f"Rép: {arc['pensees']} / {arc['sensations']} / {arc['comportements']}")
                            if st.button("Supprimer", key=f"del_arc_{i}"):
                                st.session_state.temp_arc_list.pop(i); st.rerun()
                    
                    if st.button("💾 Sauvegarder ARC", type="primary"):
                        payload = {
                            "type_exercice": "ARC Emotionnel", 
                            "liste_arc": st.session_state.temp_arc_list
                        }
                        
                        if sauvegarder_reponse_hebdo(current_user, f"Exercice - {exo_data['titre']}", "N/A", payload):
                            # 1. On vide la liste d'abord
                            st.session_state.temp_arc_list = []
                            
                            # 2. On affiche le Toast (qui reste affiché même après le rerun)
                            st.toast("✅ Fiche ARC sauvegardée avec succès !", icon='🎉')
                            
                            # 3. On recharge immédiatement (plus de time.sleep)
                            st.rerun()
            # ---------------------------------------------------------
            # TYPE 3 : PLEINE CONSCIENCE (Module 3) - NOUVEAU !
            # ---------------------------------------------------------
            elif exo_data["type"] == "fiche_pleine_conscience":
                
                # Initialisation liste temporaire
                if "temp_mindfulness_list" not in st.session_state:
                    st.session_state.temp_mindfulness_list = []

                st.markdown("#### ➕ Enregistrer une pratique")
                st.caption("Remplissez ce formulaire après votre écoute audio ou exercice.")

                with st.form("form_add_mindful", clear_on_submit=True):
                    
                    # Ligne 1 : Date et Type
                    c_m1, c_m2 = st.columns([1, 2])
                    with c_m1: 
                        date_m = st.text_input("Date :", value=datetime.now().strftime("%d/%m"))
                    with c_m2:
                        type_exo = st.selectbox("Choix de l'exercice :", 
                            ["Initiation à la méditation", "Induction d'humeur consciente", "Ancrage dans le présent"])

                    st.divider()
                    st.markdown("**Qu'avez-vous remarqué ?**")
                    
                    # Ligne 2 : Observations (3 colonnes)
                    c_obs1, c_obs2, c_obs3 = st.columns(3)
                    with c_obs1: obs_pensees = st.text_area("💭 Pensées", height=100)
                    with c_obs2: obs_sensations = st.text_area("💓 Sensations physiques", height=100)
                    with c_obs3: obs_comportements = st.text_area("🏃 Comportements/Impulsions", height=100)
                    
                    st.divider()
                    
                    # Ligne 3 : Scores (Sliders)
                    c_s1, c_s2 = st.columns(2)
                    with c_s1:
                        st.markdown("**Degré de réussite à ne pas juger ?**")
                        score_jugement = st.slider("0 (Pas du tout) à 10 (Extrêmement)", 0, 10, 5, key="sld_jugement")
                    with c_s2:
                        st.markdown("**Degré d'efficacité à vous ancrer ?**")
                        score_ancrage = st.slider("0 (Pas du tout) à 10 (Extrêmement)", 0, 10, 5, key="sld_ancrage")

                    if st.form_submit_button("Ajouter cette pratique"):
                        entree = {
                            "date": date_m,
                            "type_exo": type_exo,
                            "pensees": obs_pensees,
                            "sensations": obs_sensations,
                            "comportements": obs_comportements,
                            "score_jugement": score_jugement,
                            "score_ancrage": score_ancrage
                        }
                        st.session_state.temp_mindfulness_list.append(entree)
                        st.rerun()

            # ---------------------------------------------------------
            # TYPE 4 : FLEXIBILITÉ COGNITIVE (Module 4)
            # ---------------------------------------------------------
            elif exo_data["type"] == "fiche_flexibilite_cognitive":
                
                if "temp_flex_list" not in st.session_state:
                    st.session_state.temp_flex_list = []

                # Aide à la réflexion (Checklist de l'image)
                with st.expander("💡 Aide : Questions pour évaluer ma pensée"):
                    st.markdown("""
                    * 🤔 Suis-je certain que cela va m'arriver ?
                    * 📊 Quelle est la probabilité la plus réaliste ?
                    * 🔍 Quelles sont les explications alternatives ?
                    * 🎭 Est-ce que ma pensée est guidée par l'émotion du moment ?
                    * 🛠️ Si c'était vrai, comment je pourrais gérer ça ?
                    """)

                st.markdown("#### ➕ Analyser une pensée")
                with st.form("form_add_flex", clear_on_submit=True):
                    
                    # Ligne 1 : Déclencheur et Pensée
                    c1, c2 = st.columns(2)
                    with c1: 
                        declencheur = st.text_area("Déclencheur (Situation) :", height=80, placeholder="Ex: Mon patron ne m'a pas dit bonjour.")
                    with c2: 
                        pensee = st.text_area("Pensée Automatique :", height=80, placeholder="Ex: Il va me virer.")
                    
                    st.divider()
                    
                    # Ligne 2 : Piège et Alternative
                    c3, c4 = st.columns(2)
                    with c3: 
                        piege = st.text_input("Pensée piège ? (Optionnel)", placeholder="Ex: Catastrophisme, Lecture de pensée...")
                        # On ajoute le slider de croyance souvent utilisé en TCC
                        croyance = st.slider("A quel point j'y crois ? (0-100%)", 0, 100, 80)
                    with c4: 
                        alternative = st.text_area("✨ Autres interprétations / Pensée alternative :", height=100, placeholder="Peut-être qu'il est juste préoccupé...")

                    if st.form_submit_button("Ajouter cette analyse"):
                        if pensee:
                            st.session_state.temp_flex_list.append({
                                "declencheur": declencheur,
                                "pensee": pensee,
                                "piege": piege,
                                "croyance": croyance,
                                "alternative": alternative
                            })
                            st.rerun()
                        else:
                            st.error("La pensée est obligatoire.")

                # Affichage
                if st.session_state.temp_flex_list:
                    st.markdown("##### 📋 Analyses à enregistrer :")
                    for i, item in enumerate(st.session_state.temp_flex_list):
                        with st.expander(f"Pensée : {item['pensee'][:40]}...", expanded=False):
                            st.write(f"**Déclencheur:** {item['declencheur']}")
                            st.write(f"**Alternative:** {item['alternative']}")
                            st.caption(f"Croyance: {item['croyance']}% | Piège: {item['piege']}")
                            
                            if st.button("Supprimer", key=f"del_flex_{i}"):
                                st.session_state.temp_flex_list.pop(i)
                                st.rerun()

                    st.divider()
                    if st.button("💾 Sauvegarder Flexibilité", type="primary"):
                        payload = {
                            "type_exercice": "Flexibilité Cognitive",
                            "liste_flexibilite": st.session_state.temp_flex_list
                        }
                        if sauvegarder_reponse_hebdo(current_user, f"Exercice - {exo_data['titre']}", "N/A", payload):
                            st.toast("✅ Fiche sauvegardée !", icon="🎉")
                            st.session_state.temp_flex_list = []
                            st.rerun()

            # ---------------------------------------------------------
            # TYPE 5 : CONTRER COMPORTEMENTS (Module 5)
            # ---------------------------------------------------------
            elif exo_data["type"] == "fiche_contrer_comportements":
                
                if "temp_behavior_list" not in st.session_state:
                    st.session_state.temp_behavior_list = []

                st.markdown("#### ➕ Analyser un comportement")
                st.caption("Identifiez un comportement à changer et trouvez une alternative.")

                with st.form("form_add_behavior", clear_on_submit=True):
                    
                    # Colonnes 1 & 2 : Situation et Emotion
                    col_b1, col_b2 = st.columns(2)
                    with col_b1:
                        situation = st.text_area("Situation / Déclencheur :", height=80, placeholder="Ex: On me critique.")
                    with col_b2:
                        emotion = st.text_input("Emotion(s) ressentie(s) :", placeholder="Ex: Colère, Honte")
                    
                    st.divider()
                    
                    # Colonnes 3 & 4 : Comportements
                    col_b3, col_b4 = st.columns(2)
                    with col_b3:
                        comp_habituel = st.text_area("🔴 Comportement Emotionnel (Habituel) :", height=80, placeholder="Ex: Je crie et je pars.")
                    with col_b4:
                        comp_alternatif = st.text_area("🟢 Comportement Alternatif (Action Opposée) :", height=80, placeholder="Ex: Je reste calme et j'écoute.")

                    st.divider()
                    
                    # Colonnes 5 : Conséquences de l'alternatif
                    st.markdown("**🏁 Conséquences du comportement alternatif**")
                    col_b5, col_b6 = st.columns(2)
                    with col_b5:
                        cons_court = st.text_area("Court terme :", height=60, placeholder="C'est difficile, je tremble.")
                    with col_b6:
                        cons_long = st.text_area("Long terme :", height=60, placeholder="Je suis fier, relation préservée.")

                    if st.form_submit_button("Ajouter à ma liste"):
                        if situation and comp_habituel:
                            st.session_state.temp_behavior_list.append({
                                "situation": situation,
                                "emotion": emotion,
                                "comp_habituel": comp_habituel,
                                "comp_alternatif": comp_alternatif,
                                "cons_court": cons_court,
                                "cons_long": cons_long
                            })
                            st.rerun()
                        else:
                            st.error("La situation et le comportement habituel sont obligatoires.")

                # Affichage
                if st.session_state.temp_behavior_list:
                    st.markdown("##### 📋 Comportements à travailler :")
                    for i, item in enumerate(st.session_state.temp_behavior_list):
                        with st.expander(f"Situation : {item['situation'][:40]}...", expanded=False):
                            c1, c2 = st.columns(2)
                            with c1:
                                st.error(f"🔴 **Habitude :** {item['comp_habituel']}")
                                st.caption(f"Emotion : {item['emotion']}")
                            with c2:
                                st.success(f"🟢 **Alternative :** {item['comp_alternatif']}")
                                st.caption(f"LT : {item['cons_long']}")
                            
                            if st.button("Supprimer", key=f"del_beh_{i}"):
                                st.session_state.temp_behavior_list.pop(i)
                                st.rerun()

                    st.divider()
                    if st.button("💾 Sauvegarder cette fiche", type="primary"):
                        payload = {
                            "type_exercice": "Contrer Comportements",
                            "liste_comportements": st.session_state.temp_behavior_list
                        }
                        if sauvegarder_reponse_hebdo(current_user, f"Exercice - {exo_data['titre']}", "N/A", payload):
                            st.toast("✅ Fiche sauvegardée !", icon="🎉")
                            st.session_state.temp_behavior_list = []
                            st.rerun()


            # ---------------------------------------------------------
            # TYPE 6 : SENSATIONS PHYSIQUES (Module 6)
            # ---------------------------------------------------------
            elif exo_data["type"] == "fiche_sensations_physiques":
                
                if "temp_sensations_list" not in st.session_state:
                    st.session_state.temp_sensations_list = []

                st.markdown("#### 🌪️ Tester une induction")
                st.caption("Faites l'exercice (ex: Tourner sur soi-même 60s) puis notez ce que vous ressentez.")

                with st.form("form_add_sensation", clear_on_submit=True):
                    
                    # Choix de l'exercice
                    type_induction = st.selectbox("Procédure :", [
                        "Hyperventilation (60 sec)",
                        "Respirer à travers une paille fine (60 sec)",
                        "Tourner sur soi-même debout (60 sec)",
                        "Courir sur place (60 sec)",
                        "Autre"
                    ])
                    
                    if type_induction == "Autre":
                        type_induction = st.text_input("Précisez l'exercice :")

                    # Symptômes
                    symptomes = st.text_area("Symptômes ressentis :", height=80, placeholder="Ex: Tête qui tourne, chaleur, coeur rapide...")
                    
                    st.divider()
                    
                    # Scores
                    c_sc1, c_sc2 = st.columns(2)
                    with c_sc1:
                        score_malaise = st.slider("Malaise / Difficulté (0-10)", 0, 10, 0, help="0 = Pas de malaise, 10 = Malaise extrême")
                    with c_sc2:
                        score_resemblance = st.slider("Ressemblance avec mes émotions (0-10)", 0, 10, 0, help="0 = Rien à voir, 10 = Exactement comme mes crises")

                    if st.form_submit_button("Ajouter ce test"):
                        st.session_state.temp_sensations_list.append({
                            "exercice": type_induction,
                            "symptomes": symptomes,
                            "score_malaise": score_malaise,
                            "score_resemblance": score_resemblance
                        })
                        st.rerun()

                # Liste des tests
                if st.session_state.temp_sensations_list:
                    st.markdown("##### 📋 Tests réalisés :")
                    
                    # Note pédagogique
                    high_scores = [t for t in st.session_state.temp_sensations_list if t['score_malaise'] >= 5 and t['score_resemblance'] >= 5]
                    if high_scores:
                        st.info(f"💡 Vous avez identifié {len(high_scores)} exercice(s) pertinent(s) (Score > 5). Ce sont de bons candidats pour l'exposition !")

                    for i, item in enumerate(st.session_state.temp_sensations_list):
                        with st.expander(f"🌪️ {item['exercice']}", expanded=False):
                            st.write(f"**Symptômes :** {item['symptomes']}")
                            st.metric("Malaise", f"{item['score_malaise']}/10")
                            st.metric("Ressemblance", f"{item['score_resemblance']}/10")
                            
                            if st.button("Supprimer", key=f"del_sens_{i}"):
                                st.session_state.temp_sensations_list.pop(i)
                                st.rerun()

                    st.divider()
                    if st.button("💾 Sauvegarder mes tests", type="primary"):
                        payload = {
                            "type_exercice": "Sensations Physiques",
                            "liste_tests": st.session_state.temp_sensations_list
                        }
                        if sauvegarder_reponse_hebdo(current_user, f"Exercice - {exo_data['titre']}", "N/A", payload):
                            st.toast("✅ Tests sauvegardés !", icon="🎉")
                            st.session_state.temp_sensations_list = []
                            st.rerun()

            # ---------------------------------------------------------
            # TYPE 7 : HIÉRARCHIE D'EXPOSITION (Module 7)
            # ---------------------------------------------------------
            elif exo_data["type"] == "fiche_hierarchie_exposition":
                
                if "temp_hierarchy_list" not in st.session_state:
                    st.session_state.temp_hierarchy_list = []

                st.markdown("#### 📈 Construire ma hiérarchie")
                st.caption("Ajoutez des situations et classez-les de la plus difficile (1) à la moins difficile.")

                with st.form("form_add_hierarchy", clear_on_submit=True):
                    
                    # Ligne 1 : Rang et Description
                    col_h1, col_h2 = st.columns([1, 3])
                    with col_h1:
                        rang = st.number_input("Rang (1 = Le pire)", min_value=1, value=1)
                    with col_h2:
                        situation = st.text_area("Description de la situation anxiogène :", height=80)
                    
                    st.divider()
                    
                    # Ligne 2 : Scores
                    col_h3, col_h4 = st.columns(2)
                    with col_h3:
                        score_evit = st.slider("Score d'Évitement (0-10)", 0, 10, 5)
                    with col_h4:
                        score_detr = st.slider("Score de Détresse (0-10)", 0, 10, 5)

                    if st.form_submit_button("Ajouter à la liste"):
                        if situation:
                            st.session_state.temp_hierarchy_list.append({
                                "rang": rang,
                                "situation": situation,
                                "score_evit": score_evit,
                                "score_detr": score_detr
                            })
                            # On trie automatiquement la liste par rang (croissant)
                            st.session_state.temp_hierarchy_list.sort(key=lambda x: x["rang"])
                            st.rerun()
                        else:
                            st.error("La description est obligatoire.")

                # Affichage
                if st.session_state.temp_hierarchy_list:
                    st.markdown("##### 📋 Ma Hiérarchie (Du pire au moins pire) :")
                    for i, item in enumerate(st.session_state.temp_hierarchy_list):
                        # Couleur conditionnelle selon le rang pour un effet visuel
                        icon = "🔴" if item['rang'] == 1 else "🟠" if item['rang'] <= 3 else "🟡"
                        
                        with st.expander(f"{icon} Rang {item['rang']} : {item['situation'][:40]}...", expanded=False):
                            st.write(f"**Situation :** {item['situation']}")
                            c1, c2 = st.columns(2)
                            with c1: st.metric("Évitement", f"{item['score_evit']}/10")
                            with c2: st.metric("Détresse", f"{item['score_detr']}/10")
                            
                            if st.button("Supprimer", key=f"del_hier_{i}"):
                                st.session_state.temp_hierarchy_list.pop(i)
                                st.rerun()

                    st.divider()
                    if st.button("💾 Sauvegarder ma hiérarchie", type="primary"):
                        payload = {
                            "type_exercice": "Hiérarchie Exposition",
                            "liste_hierarchie": st.session_state.temp_hierarchy_list
                        }
                        if sauvegarder_reponse_hebdo(current_user, f"Exercice - {exo_data['titre']}", "N/A", payload):
                            st.toast("✅ Hiérarchie sauvegardée !", icon="🎉")
                            st.session_state.temp_hierarchy_list = []
                            st.rerun()

            # ---------------------------------------------------------
            # TYPE 8 : ENREGISTREMENT EXPOSITION (Module 7)
            # ---------------------------------------------------------
            elif exo_data["type"] == "fiche_enregistrement_exposition":
                
                st.markdown("#### 🎬 Nouvelle séance d'exposition")
                
                with st.form("form_expo_session"):
                    
                    # --- PARTIE 1 : PRÉPARATION ---
                    with st.expander("1. Préparation avant l'exposition", expanded=True):
                        col_e1, col_e2 = st.columns([1, 3])
                        with col_e1: 
                            date_exp = st.text_input("Date :", value=datetime.now().strftime("%d/%m/%Y"))
                        with col_e2:
                            activite = st.text_area("Exercice d'exposition (Description) :", height=70, placeholder="Ex: Aller au centre commercial pendant 30 min.")
                        
                        st.divider()
                        
                        c_p1, c_p2 = st.columns(2)
                        with c_p1:
                            pens_auto = st.text_area("🔴 Pensées automatiques négatives :", height=100, placeholder="Ex: Je vais m'évanouir.")
                            comp_emo = st.text_area("🔴 Comportements émotionnels (à éviter) :", height=100, placeholder="Ex: S'asseoir, appeler un ami, partir vite.")
                        with c_p2:
                            pens_alt = st.text_area("🟢 Pensées alternatives (Flexibles) :", height=100, placeholder="Ex: C'est désagréable mais pas dangereux.")
                            comp_alt = st.text_area("🟢 Comportements alternatifs (à faire) :", height=100, placeholder="Ex: Rester debout, respirer calmement.")
                        
                        st.markdown("**🧘 Intention Pleine Conscience :**")
                        st.caption("Souvenez-vous d'adopter une attitude non jugeante et de rester ancré dans le présent.")

                    # --- PARTIE 2 : DÉBRIEFING ---
                    with st.expander("2. Débriefing après l'exposition", expanded=True):
                        
                        emotions_felt = st.text_input("Quelles émotions avez-vous ressenties ?")
                        
                        st.markdown("**Décomposez votre expérience :**")
                        c_d1, c_d2, c_d3 = st.columns(3)
                        with c_d1: d_pensees = st.text_area("Pensées pendant l'expo :", height=80)
                        with c_d2: d_sensations = st.text_area("Sensations physiques :", height=80)
                        with c_d3: d_comport = st.text_area("Comportements :", height=80)
                        
                        st.divider()
                        st.markdown("**Scores d'évaluation (0 - 10) :**")
                        s1, s2, s3 = st.columns(3)
                        with s1: sc_pc = st.slider("Pleine Conscience (Ressentir émotions)", 0, 10, 5)
                        with s2: sc_flex = st.slider("Flexibilité Cognitive (Pensées)", 0, 10, 5)
                        with s3: sc_act = st.slider("Contrer comportements (Adopter alternatives)", 0, 10, 5)
                        
                        st.divider()
                        st.markdown("**Apprentissages :**")
                        appris_tache = st.text_area("Qu'avez-vous appris sur la tâche/situation ?", height=70)
                        appris_capa = st.text_area("Qu'avez-vous appris sur votre capacité à faire face ?", height=70)
                        next_time = st.text_area("Que ferez-vous différemment la prochaine fois ?", height=70)

                    submitted = st.form_submit_button("💾 Enregistrer cette séance d'exposition", type="primary")
                    
                    if submitted:
                        if activite:
                            payload = {
                                "type_exercice": "Enregistrement Exposition",
                                "date": date_exp,
                                "activite": activite,
                                "preparation": {
                                    "pens_auto": pens_auto, "pens_alt": pens_alt,
                                    "comp_emo": comp_emo, "comp_alt": comp_alt
                                },
                                "debrief": {
                                    "emotions": emotions_felt,
                                    "pensees": d_pensees, "sensations": d_sensations, "comportements": d_comport,
                                    "scores": {"pc": sc_pc, "flex": sc_flex, "action": sc_act},
                                    "appris_tache": appris_tache, "appris_capa": appris_capa, "next_time": next_time
                                }
                            }
                            if sauvegarder_reponse_hebdo(current_user, f"Exercice - {exo_data['titre']}", "N/A", payload):
                                st.toast("✅ Séance enregistrée !", icon="🎉")
                                st.rerun()
                        else:
                            st.error("Veuillez décrire l'exercice d'exposition.")


            # ---------------------------------------------------------
            # TYPE 9 : ÉVALUATION DES PROGRÈS (Module 8)
            # ---------------------------------------------------------
            elif exo_data["type"] == "fiche_evaluation_progres":
                
                st.markdown("#### 🏆 Bilan de fin de module")
                st.caption("Faites le point sur chaque compétence apprise.")

                with st.form("form_bilan_progres"):
                    
                    # 1. Pleine Conscience
                    st.markdown("##### 🧘 1. Pleine Conscience Émotionnelle")
                    pc_progres = st.text_area("Quelles améliorations spécifiques ?", height=80, key="pc_p")
                    pc_futur = st.text_area("Pistes d'amélioration continue ?", height=80, key="pc_f")
                    st.divider()

                    # 2. Flexibilité Cognitive
                    st.markdown("##### 🧠 2. Flexibilité Cognitive")
                    flex_progres = st.text_area("Quelles améliorations spécifiques ?", height=80, key="flex_p")
                    flex_futur = st.text_area("Pistes d'amélioration continue ?", height=80, key="flex_f")
                    st.divider()

                    # 3. Sensations Physiques
                    st.markdown("##### 🌪️ 3. Confronter les sensations physiques")
                    sens_progres = st.text_area("Quelles améliorations spécifiques ?", height=80, key="sens_p")
                    sens_futur = st.text_area("Pistes d'amélioration continue ?", height=80, key="sens_f")
                    st.divider()

                    # 4. Comportements
                    st.markdown("##### 🛡️ 4. Contrer l'évitement émotionnel")
                    comp_progres = st.text_area("Quelles améliorations spécifiques ?", height=80, key="comp_p")
                    comp_futur = st.text_area("Pistes d'amélioration continue ?", height=80, key="comp_f")

                    if st.form_submit_button("💾 Enregistrer mon bilan", type="primary"):
                        payload = {
                            "type_exercice": "Evaluation Progres",
                            "date": datetime.now().strftime("%d/%m/%Y"),
                            "pleine_conscience": {"progres": pc_progres, "futur": pc_futur},
                            "flexibilite": {"progres": flex_progres, "futur": flex_futur},
                            "sensations": {"progres": sens_progres, "futur": sens_futur},
                            "comportements": {"progres": comp_progres, "futur": comp_futur}
                        }
                        if sauvegarder_reponse_hebdo(current_user, f"Exercice - {exo_data['titre']}", "N/A", payload):
                            st.toast("✅ Bilan enregistré !", icon="🎉")
                            st.rerun()

            # ---------------------------------------------------------
            # TYPE 10 : PLAN DE MAINTIEN (Module 8)
            # ---------------------------------------------------------
            elif exo_data["type"] == "fiche_plan_maintien":
                
                st.markdown("#### 📅 Mon plan pour continuer")
                st.caption("Remplissez ce plan pour définir comment vous utiliserez vos compétences à l'avenir.")

                with st.form("form_plan_maintien"):
                    
                    # On utilise des Tabs pour ne pas avoir une page kilométrique
                    tab_pc, tab_flex, tab_sens, tab_comp = st.tabs(["🧘 Pleine Conscience", "🧠 Flexibilité", "🌪️ Sensations", "🛡️ Comportements"])
                    
                    with tab_pc:
                        st.info("Pleine conscience émotionnelle")
                        pc_1 = st.text_area("Comment cela aidera vos objectifs long terme ?", height=100, key="pc_1")
                        pc_2 = st.text_area("Plan de pratique spécifique ?", height=100, key="pc_2")
                        pc_3 = st.text_area("Comment s'engager à le respecter ?", height=100, key="pc_3")

                    with tab_flex:
                        st.info("Flexibilité cognitive")
                        flex_1 = st.text_area("Comment cela aidera vos objectifs long terme ?", height=100, key="fx_1")
                        flex_2 = st.text_area("Plan de pratique spécifique ?", height=100, key="fx_2")
                        flex_3 = st.text_area("Comment s'engager à le respecter ?", height=100, key="fx_3")

                    with tab_sens:
                        st.info("Confrontation aux sensations physiques")
                        sens_1 = st.text_area("Comment cela aidera vos objectifs long terme ?", height=100, key="sn_1")
                        sens_2 = st.text_area("Plan de pratique spécifique ?", height=100, key="sn_2")
                        sens_3 = st.text_area("Comment s'engager à le respecter ?", height=100, key="sn_3")

                    with tab_comp:
                        st.info("Contrer les comportements émotionnels")
                        comp_1 = st.text_area("Comment cela aidera vos objectifs long terme ?", height=100, key="cp_1")
                        comp_2 = st.text_area("Plan de pratique spécifique ?", height=100, key="cp_2")
                        comp_3 = st.text_area("Comment s'engager à le respecter ?", height=100, key="cp_3")

                    if st.form_submit_button("💾 Sauvegarder mon plan", type="primary"):
                        payload = {
                            "type_exercice": "Plan Maintien",
                            "date": datetime.now().strftime("%d/%m/%Y"),
                            "pleine_conscience": {"aide": pc_1, "plan": pc_2, "engagement": pc_3},
                            "flexibilite": {"aide": flex_1, "plan": flex_2, "engagement": flex_3},
                            "sensations": {"aide": sens_1, "plan": sens_2, "engagement": sens_3},
                            "comportements": {"aide": comp_1, "plan": comp_2, "engagement": comp_3}
                        }
                        if sauvegarder_reponse_hebdo(current_user, f"Exercice - {exo_data['titre']}", "N/A", payload):
                            st.toast("✅ Plan enregistré !", icon="🎉")
                            st.rerun()

# =========================================================
# 3. MON SUIVI DE SANTÉ
# =========================================================
with tab_bilan:
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
    
# =========================================================
# 4. MON HISTORIQUE (NOUVEL ONGLET CENTRALISÉ)
# =========================================================
with tab_historique:
    st.subheader("📜 Historique Complet")
    
    if not df_history.empty:
        
        # --- A. GRAPHIQUES & TABLEAUX (Scores) ---
        st.markdown("#### 📈 Évolution des Scores (Questionnaires)")
        
        # On filtre pour ne garder que les questionnaires (on exclut les exercices)
        df_charts = df_history[~df_history["Questionnaire"].str.contains("Exercice", na=False)]
        
        if not df_charts.empty:
            # Sélecteur de courbes
            types_dispos = df_charts["Type"].unique().tolist()
            choix_types = st.multiselect("Afficher les courbes de :", types_dispos, default=types_dispos[:2] if len(types_dispos)>0 else None)
            
            if choix_types:
                # Graphique Altair
                df_viz = df_charts[df_charts["Type"].isin(choix_types)]
                chart = alt.Chart(df_viz).mark_line(point=True).encode(
                    x=alt.X('Date', axis=alt.Axis(format='%d/%m')),
                    y='Score_Global',
                    color='Type',
                    tooltip=['Date', 'Type', 'Score_Global']
                ).properties(height=300).interactive()
                st.altair_chart(chart, use_container_width=True)
            
            # Tableau de données
            with st.expander("📊 Voir le tableau détaillé des scores", expanded=False):
                st.dataframe(
                    df_charts[["Date", "Questionnaire", "Score_Global"]].sort_values("Date", ascending=False),
                    use_container_width=True,
                    hide_index=True
                )
        else:
            st.info("Aucun questionnaire rempli pour le moment.")

        st.divider()

# --- B. JOURNAL DES EXERCICES ---
        st.markdown("#### 🛠️ Journal des Exercices (Détails)")
        
        # On filtre pour ne garder QUE les exercices
        df_exos = df_history[df_history["Questionnaire"].str.contains("Exercice", na=False)].copy()
        
        if not df_exos.empty:
            # Boucle d'affichage inversée (plus récent en haut)
            for idx, row in df_exos.sort_values("Date", ascending=False).iterrows():
                
                with st.expander(f"🗓️ {row['Date'].strftime('%d/%m')} - {row['Questionnaire']}"):
                    
                    # Création de deux colonnes : 
                    # Col 1 (Petite) : Pour le bouton supprimer
                    # Col 2 (Grande) : Pour afficher le contenu de l'exercice
                    col_del, col_content = st.columns([1, 5])
                    
                    with col_del:
                        st.write("") # Petit espace pour aligner le bouton verticalement
                        # Bouton rouge (type="primary") pour la suppression
                        if st.button("🗑️ Supprimer", key=f"hist_del_{idx}", type="primary"):
                            supprimer_reponse(current_user, row["Date"], row["Questionnaire"])
                            st.rerun()
                    
                    with col_content:
                        try:
                            d = json.loads(row["Details_Json"])
                            
                            # --- AFFICHAGE SELON LE TYPE D'EXERCICE ---
                            
                            # 1. Objectifs
                            if "probleme_principal" in d:
                                st.info(f"**Problème :** {d['probleme_principal']}")
                                for o in d.get('liste_objectifs', []):
                                    st.write(f"🎯 **{o['objectif']}**")
                                    if 'etapes' in o and o['etapes']: st.caption(f"Étapes : {', '.join(o['etapes'])}")

                            # 2. ARC Emotionnel
                            elif "liste_arc" in d:
                                for a in d['liste_arc']:
                                    st.markdown(f"⚡ **{a['antecedent']}**")
                                    st.caption(f"💭 {a['pensees']} | 💓 {a['sensations']} | 🏃 {a['comportements']}")
                                    st.write(f"🏁 Csq: {a['c_court']}")
                                    st.divider()

                            # 3. Pleine Conscience
                            elif "liste_pratiques" in d:
                                for p in d['liste_pratiques']:
                                    st.markdown(f"🧘 **{p['type_exo']}**")
                                    st.write(f"💭 {p['pensees']} | 💓 {p['sensations']}")
                                    st.caption(f"Scores : Non-jugement {p['score_jugement']}/10 | Ancrage {p['score_ancrage']}/10")
                                    st.divider()

                            # 4. Flexibilité
                            elif "liste_flexibilite" in d:
                                for f in d['liste_flexibilite']:
                                    st.write(f"Situation : {f['declencheur']}")
                                    st.write(f"🔴 {f['pensee']}  ➡️  🟢 **{f['alternative']}**")
                                    st.divider()

                            # 5. Contrer Comportements
                            elif "liste_comportements" in d:
                                for c in d['liste_comportements']:
                                    st.write(f"Situation : {c['situation']}")
                                    st.write(f"🔴 {c['comp_habituel']}  ➡️  🟢 **{c['comp_alternatif']}**")
                                    st.divider()

                            # 6. Sensations Physiques
                            elif "liste_tests" in d:
                                for t in d['liste_tests']:
                                    st.markdown(f"🌪️ **{t['exercice']}**")
                                    st.write(f"Symptômes : {t['symptomes']}")
                                    st.caption(f"Malaise: {t['score_malaise']}/10 | Ressemblance: {t['score_resemblance']}/10")
                                    st.divider()

                            # 7. Hiérarchie
                            elif "liste_hierarchie" in d:
                                st.table(pd.DataFrame(d['liste_hierarchie'])[['rang', 'situation', 'score_evit', 'score_detr']])

                            # 8. Enregistrement Exposition
                            elif "activite" in d:
                                st.write(f"🎬 **Expo : {d['activite']}**")
                                c_av, c_ap = st.columns(2)
                                with c_av:
                                    st.caption("AVANT")
                                    st.write(f"🔴 {d['preparation']['pens_auto']}")
                                    st.write(f"🟢 {d['preparation']['pens_alt']}")
                                with c_ap:
                                    st.caption("APRÈS")
                                    st.write(f"Emotions : {d['debrief']['emotions']}")
                                    st.write(d['debrief']['appris_capa'])

                            # 9. Bilan / Plan (Types simples)
                            elif "pleine_conscience" in d: 
                                st.success("Bilan/Plan enregistré")
                                st.json(d)

                            # Fallback (Autres types)
                            else:
                                st.json(d)

                        except Exception as e:
                            st.error(f"Erreur lecture : {e}")
        else:
            st.info("Aucun exercice réalisé pour le moment.")

    else:
        st.info("Votre historique est vide. Commencez par remplir un bilan ou un exercice !")