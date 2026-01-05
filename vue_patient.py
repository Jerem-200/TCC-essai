import streamlit as st
import pandas as pd
import time
import os
import json
import altair as alt
from datetime import datetime

from protocole_config import PROTOCOLE_BARLOW, QUESTIONS_HEBDO
from connect_db import (
    charger_progression, charger_etat_devoirs, charger_suivi_global,
    charger_outils_autorises, sauvegarder_progression,
    sauvegarder_etat_devoirs, sauvegarder_suivi_global,
    sauvegarder_reponse_hebdo, supprimer_reponse, load_data
)

@st.cache_data(ttl=300)
def charger_historique_local(uid):
    raw = load_data("Reponses_Hebdo")
    if raw:
        df = pd.DataFrame(raw)
        if "Patient" in df.columns:
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
    return pd.DataFrame()

def afficher_vue_patient(patient_id):
    
    # 1. DONNÉES
    outils_autorises = charger_outils_autorises(patient_id)
    progression = charger_progression(patient_id)
    devoirs = charger_etat_devoirs(patient_id)
    valides, notes_therapeute = charger_suivi_global(patient_id)
    df_history = charger_historique_local(patient_id)
    
    st.title(f"👋 Espace de {patient_id}")

    # 2. NAVIGATION INTELLIGENTE
    # Liste des onglets principaux
    liste_onglets = [
        "🏠 Tableau de Bord", 
        "🗺️ Protocole", 
        "📅 Agendas", 
        "🛠️ Outils & Exos", 
        "📊 Échelles", 
        "📤 Export"
    ]
    
    # Calcul de l'index par défaut selon d'où on vient
    default_idx = 0
    cible = st.session_state.get("target_tab", None)
    if cible in liste_onglets:
        default_idx = liste_onglets.index(cible)
        st.session_state["target_tab"] = None # On reset après utilisation

    # On utilise Radio au lieu de Tabs pour contrôler l'index
    onglet_actif = st.radio("Menu Principal", liste_onglets, index=default_idx, horizontal=True, label_visibility="collapsed")
    st.divider()

    # ======================================================
    # VUE 1 : TABLEAU DE BORD
    # ======================================================
    if onglet_actif == "🏠 Tableau de Bord":
        st.markdown("### 📌 Ma situation aujourd'hui")
        c1, c2, c3 = st.columns(3)
        nb_valides = len(valides)
        with c1: 
            st.metric("Modules Terminés", f"{nb_valides} / {len(PROTOCOLE_BARLOW)}")
            st.progress(nb_valides / len(PROTOCOLE_BARLOW))
        with c2:
            st.metric("Outils Débloqués", f"{len(outils_autorises)}")
        with c3:
            st.info("💡 **Conseil** : Pensez à votre bilan hebdo.")

        st.divider()
        st.subheader("📒 Mon Journal de Séance")
        with st.form("form_note_seance"):
            col_d, col_t = st.columns([1, 3])
            with col_d: date_note = st.date_input("Date", value=datetime.now())
            with col_t: contenu_note = st.text_area("Résumé :", height=100)
            if st.form_submit_button("💾 Enregistrer"):
                payload = {"type": "note_personnelle", "contenu": contenu_note}
                sauvegarder_reponse_hebdo(patient_id, f"Note Séance - {date_note}", "Perso", payload)
                st.success("Note enregistrée !")
                time.sleep(1)
                st.rerun()

    # ======================================================
    # VUE 2 : PROTOCOLE (Structure imbriquée)
    # ======================================================
    elif onglet_actif == "🗺️ Protocole":
        st.header("🗺️ Mon Parcours TCC")
        
        # Sous-menus du protocole
        sous_onglets = ["📍 Progression", "🚀 Lanceur Rapide", "📝 Bilan Hebdo", "📜 Historique"]
        
        # Gestion du retour "Lanceur rapide"
        idx_sub = 0
        if st.session_state.get("retour_outils", False): # Ancien drapeau si tu l'utilises encore
            idx_sub = 1
            st.session_state["retour_outils"] = False
            
        choix_sub = st.radio("Sous-menu", sous_onglets, index=idx_sub, horizontal=True)
        st.write("")

        # --- A. PROGRESSION ---
        if choix_sub == "📍 Progression":
            if "last_active_module" not in st.session_state: st.session_state.last_active_module = "module0"

            for code_mod, data in PROTOCOLE_BARLOW.items():
                is_done = code_mod in valides
                icon = "✅" if is_done else "🟦"
                expanded = (code_mod == st.session_state.last_active_module)
                
                if code_mod in progression:
                    with st.expander(f"{icon} {data['titre']}", expanded=expanded):
                        t_seance, t_docs = st.tabs(["📖 Séance", "📂 Documents"])
                        
                        with t_seance:
                            st.info(f"**Objectifs :** {data['objectifs']}")
                            with st.form(key=f"form_proto_{code_mod}"):
                                checklist_results = []
                                
                                if data['examen_devoirs']:
                                    st.markdown("**1️⃣ Retour sur les tâches**")
                                    for idx, task in enumerate(data['examen_devoirs']):
                                        chk = st.checkbox(task['titre'], key=f"chk_ex_{code_mod}_{idx}")
                                        checklist_results.append(chk)
                                st.write("---")

                                st.markdown("**2️⃣ Contenu de la séance**")
                                for idx, etape in enumerate(data['etapes_seance']):
                                    chk = st.checkbox(etape['titre'], key=f"chk_st_{code_mod}_{idx}", help=etape.get('details'))
                                    checklist_results.append(chk)
                                st.write("---")
                                
                                liste_devoirs_temp = []
                                if data['taches_domicile']:
                                    st.markdown("**3️⃣ Travail à la maison**")
                                    current_excluded = devoirs.get(code_mod, [])
                                    for j, dev in enumerate(data['taches_domicile']):
                                        is_checked = (j not in current_excluded)
                                        val = st.checkbox(dev['titre'], value=is_checked, key=f"chk_hw_{code_mod}_{j}")
                                        liste_devoirs_temp.append(val)
                                        if dev.get('pdf'): st.caption(f"📄 {os.path.basename(dev['pdf'])}")
                                    st.write("---")

                                st.markdown("**4️⃣ Notes & Commentaires**")
                                note_precedente = notes_therapeute.get(code_mod, "")
                                nouvelle_note = st.text_area("Observations :", value=note_precedente, height=100)

                                if st.form_submit_button("💾 Sauvegarder l'avancement", type="primary"):
                                    if data['taches_domicile']:
                                        exclus = [k for k, v in enumerate(liste_devoirs_temp) if not v]
                                        devoirs[code_mod] = exclus
                                        sauvegarder_etat_devoirs(patient_id, devoirs)
                                    
                                    notes_therapeute[code_mod] = nouvelle_note
                                    
                                    all_ok = all(checklist_results) if checklist_results else True
                                    if all_ok and code_mod not in valides: valides.append(code_mod)
                                    elif not all_ok and code_mod in valides: valides.remove(code_mod)
                                    
                                    sauvegarder_suivi_global(patient_id, valides, notes_therapeute)
                                    st.session_state.last_active_module = code_mod
                                    time.sleep(0.5)
                                    st.rerun()

                            # Boutons Exercices (Clés uniques !)
                            if data.get('exercices'):
                                st.info("👇 **Outils pour ce module :**")
                                for k, exo in enumerate(data['exercices']):
                                    if st.button(f"🚀 Lancer : {exo['titre']}", key=f"btn_nav_exo_{code_mod}_{k}"):
                                        st.session_state["exercice_actif"] = {"mod_code": code_mod, "exo_data": exo}
                                        st.switch_page("pages/21_Barlow_Exercice.py")

                        with t_docs:
                            if data.get('pdfs_module'):
                                for p in data['pdfs_module']:
                                    if os.path.exists(p):
                                        with open(p, "rb") as f:
                                            st.download_button(f"📥 {os.path.basename(p)}", f, file_name=os.path.basename(p), key=f"dl_{code_mod}_{os.path.basename(p)}")
                            else: st.caption("Aucun document.")
                else:
                    with st.container(): st.write(f"🔒 **{data['titre']}** (Verrouillé)"); st.divider()

        # --- B. LANCEUR RAPIDE ---
        elif choix_sub == "🚀 Lanceur Rapide":
            st.subheader("Accès direct aux outils")
            liste_exos_dispos = []
            for m in progression:
                if m in PROTOCOLE_BARLOW and "exercices" in PROTOCOLE_BARLOW[m]:
                    for exo in PROTOCOLE_BARLOW[m]["exercices"]:
                        liste_exos_dispos.append({"mod_code": m, "exo_data": exo})
            
            if not liste_exos_dispos: st.warning("Aucun outil débloqué.")
            else:
                for k, item in enumerate(liste_exos_dispos):
                    exo = item["exo_data"]
                    if st.button(f"👉 {item['mod_code']} - {exo['titre']}", key=f"btn_fast_{k}", use_container_width=True):
                        st.session_state["exercice_actif"] = item
                        st.switch_page("pages/21_Barlow_Exercice.py")

        # --- C. BILAN HEBDO ---
        elif choix_sub == "📝 Bilan Hebdo":
            st.subheader("Bilan Hebdomadaire")
            choix_q = st.selectbox("Questionnaire :", list(QUESTIONS_HEBDO.keys()))
            if choix_q:
                cfg = QUESTIONS_HEBDO[choix_q]
                with st.form(f"form_bilan_{choix_q}"):
                    rep = {}
                    score = 0
                    if cfg.get("ask_emotion"): rep["Emotion"] = st.text_input("Emotion :")
                    if cfg['type'] == "scale_0_8":
                        for q in cfg['questions']:
                            val = st.slider(q, 0, 8, 0)
                            rep[q] = val
                            score += val
                    
                    if st.form_submit_button("Enregistrer"):
                        lbl = choix_q
                        if "Emotion" in rep: lbl += f" ({rep['Emotion']})"
                        sauvegarder_reponse_hebdo(patient_id, lbl, str(score), rep)
                        st.success("Sauvegardé !")
                        charger_historique_local.clear()

        # --- D. HISTORIQUE ---
        elif choix_sub == "📜 Historique":
            st.subheader("Historique")
            if not df_history.empty:
                df_charts = df_history[~df_history["Questionnaire"].str.contains("Exercice", na=False)]
                if not df_charts.empty:
                    chart = alt.Chart(df_charts).mark_line(point=True).encode(x='Date', y='Score_Global', color='Type').interactive()
                    st.altair_chart(chart, use_container_width=True)
                
                for idx, row in df_history.sort_values("Date", ascending=False).iterrows():
                    with st.expander(f"{row['Date'].strftime('%d/%m')} - {row['Questionnaire']}"):
                        c_del, c_cont = st.columns([1, 5])
                        with c_del:
                            if st.button("🗑️", key=f"del_h_p_{idx}"):
                                supprimer_reponse(patient_id, row["Date"], row["Questionnaire"])
                                charger_historique_local.clear()
                                st.rerun()
                        with c_cont:
                            try: st.json(json.loads(row["Details_Json"]))
                            except: st.write(row["Details_Json"])
            else: st.info("Historique vide.")

    # ======================================================
    # VUE 3 : AGENDAS
    # ======================================================
    elif onglet_actif == "📅 Agendas":
        st.header("📅 Mes Agendas")
        col_a1, col_a2 = st.columns(2)
        with col_a1:
            if "sommeil" in outils_autorises:
                if st.button("🌙 Agenda Sommeil", use_container_width=True): st.switch_page("pages/10_Agenda_Sommeil.py")
            if "conso" in outils_autorises:
                if st.button("🍷 Agenda Consos", use_container_width=True): st.switch_page("pages/13_Agenda_Consos.py")
        with col_a2:
            if "activites" in outils_autorises:
                if st.button("📝 Registre Activités", use_container_width=True): st.switch_page("pages/05_Registre_Activites.py")
            if "compulsions" in outils_autorises:
                if st.button("🛑 Agenda Compulsions", use_container_width=True): st.switch_page("pages/14_Agenda_Compulsions.py")

    # ======================================================
    # VUE 4 : OUTILS
    # ======================================================
    elif onglet_actif == "🛠️ Outils & Exos":
        st.header("🛠️ Boîte à outils")
        c1, c2, c3 = st.columns(3)
        with c1:
            if "beck" in outils_autorises:
                if st.button("🧩 Beck", use_container_width=True): st.switch_page("pages/01_Colonnes_Beck.py")
            if "sorc" in outils_autorises:
                if st.button("🔍 SORC", use_container_width=True): st.switch_page("pages/12_Analyse_SORC.py")
        with c2:
            if "problemes" in outils_autorises:
                if st.button("💡 Résolution", use_container_width=True): st.switch_page("pages/06_Resolution_Probleme.py")
            if "balance" in outils_autorises:
                if st.button("⚖️ Balance", use_container_width=True): st.switch_page("pages/11_Balance_Decisionnelle.py")
        with c3:
            if "expo" in outils_autorises:
                if st.button("🧗 Exposition", use_container_width=True): st.switch_page("pages/09_Exposition.py")
            if "relax" in outils_autorises:
                if st.button("🧘 Relaxation", use_container_width=True): st.switch_page("pages/07_Relaxation.py")

    # ======================================================
    # VUE 5 : ÉCHELLES
    # ======================================================
    elif onglet_actif == "📊 Échelles":
        st.header("📊 Mesures")
        liste_ech = [("phq9", "PHQ-9"), ("gad7", "GAD-7"), ("who5", "WHO-5"), ("isi", "ISI"), ("peg", "PEG"), ("wsas", "WSAS")]
        cols = st.columns(3)
        for i, (code, titre) in enumerate(liste_ech):
            if code in outils_autorises:
                with cols[i%3]:
                    # Map manuel des pages si besoin
                    page_map = {"phq9": "15", "gad7": "16", "isi": "17", "peg": "18", "wsas": "19", "who5": "20"}
                    if st.button(titre, key=f"btn_e_{code}", use_container_width=True): 
                        st.switch_page(f"pages/{page_map[code]}_Echelle_{code.upper()}.py")

    # ======================================================
    # VUE 6 : EXPORT
    # ======================================================
    elif onglet_actif == "📤 Export":
        st.header("📤 Export")
        if st.button("Générer PDF", type="primary"): st.switch_page("pages/08_Export_Rapport.py")