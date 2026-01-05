import streamlit as st
import pandas as pd
import time
import os
import json
import altair as alt
from datetime import datetime

# Imports Configuration & DB
from protocole_config import PROTOCOLE_BARLOW, QUESTIONS_HEBDO
from connect_db import (
    charger_progression, charger_etat_devoirs, charger_suivi_global,
    charger_outils_autorises, sauvegarder_progression,
    sauvegarder_etat_devoirs, sauvegarder_suivi_global,
    sauvegarder_reponse_hebdo, supprimer_reponse, load_data
)

# Cache local pour l'historique
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
    
    # 1. CHARGEMENT DES DONNÉES
    outils_autorises = charger_outils_autorises(patient_id)
    progression = charger_progression(patient_id)
    devoirs = charger_etat_devoirs(patient_id)
    valides, notes_therapeute = charger_suivi_global(patient_id)
    df_history = charger_historique_local(patient_id)
    
    st.title(f"👋 Espace de {patient_id}")

    # 2. NAVIGATION PRINCIPALE
    onglets = st.tabs([
        "🏠 Tableau de Bord", 
        "🗺️ Protocole", 
        "📅 Agendas", 
        "🛠️ Outils & Exos", 
        "📊 Échelles", 
        "📤 Export"
    ])

    # ======================================================
    # ONGLET 1 : TABLEAU DE BORD
    # ======================================================
    with onglets[0]:
        st.markdown("### 📌 Ma situation aujourd'hui")
        c1, c2, c3 = st.columns(3)
        nb_valides = len(valides)
        with c1: 
            st.metric("Modules Terminés", f"{nb_valides} / {len(PROTOCOLE_BARLOW)}")
            st.progress(nb_valides / len(PROTOCOLE_BARLOW))
        with c2:
            st.metric("Outils Débloqués", f"{len(outils_autorises)}")
        with c3:
            st.info("💡 **Conseil du jour** : Pensez à votre bilan hebdo.")

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
    # ONGLET 2 : PROTOCOLE (AVEC TA VUE PRÉFÉRÉE RESTAURÉE)
    # ======================================================
    with onglets[1]:
        st.header("🗺️ Mon Parcours TCC")
        
        sous_onglets = ["📍 Progression", "🚀 Lanceur Rapide", "📝 Bilan Hebdo", "📜 Historique"]
        
        idx_defaut = 0
        if st.session_state.get("retour_outils", False):
            idx_defaut = 1
            st.session_state["retour_outils"] = False
            
        choix_sous_onglet = st.radio("Navigation Protocole", sous_onglets, index=idx_defaut, horizontal=True, label_visibility="collapsed")
        st.divider()

        # -------------------------------------------------
        # A. VUE PROGRESSION (TON CODE RESTAURÉ)
        # -------------------------------------------------
        if choix_sous_onglet == "📍 Progression":
            st.markdown("### 📍 Mon cheminement")
    
            for code_mod, data in PROTOCOLE_BARLOW.items():
                
                # Vérification si le module est débloqué
                if code_mod in progression:
                    
                    # On affiche l'icône de validation si fait
                    icon_valid = "✅" if code_mod in valides else ""
                    
                    with st.expander(f"{icon_valid} {data['titre']}", expanded=False):
                        t_seance, t_doc = st.tabs(["📖 Résumé Séance", "📂 Documents"])
                        
                        # --- Onglet Résumé ---
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
                                # On récupère les devoirs exclus pour ce module
                                exclus = devoirs.get(code_mod, [])
                                a_faire = False
                                
                                if data['taches_domicile']:
                                    for j, dev in enumerate(data['taches_domicile']):
                                        # Si l'index n'est pas dans les exclus, on l'affiche
                                        if j not in exclus:
                                            a_faire = True
                                            st.markdown(f"👉 **{dev['titre']}**")
                                            if dev.get('pdf') and os.path.exists(dev['pdf']):
                                                with open(dev['pdf'], "rb") as f:
                                                    st.download_button("📥 Support", f, file_name=os.path.basename(dev['pdf']), key=f"d_home_{code_mod}_{j}")
                                
                                if not a_faire: 
                                    st.success("🎉 Rien de spécial.")
                                else:
                                    st.write("")
                                    with st.expander("📸 Envoyer une photo"):
                                        st.camera_input("Photo", key=f"cam_{code_mod}")

                        # --- Onglet Documents ---
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

        # -------------------------------------------------
        # B. LANCEUR RAPIDE
        # -------------------------------------------------
        elif choix_sous_onglet == "🚀 Lanceur Rapide":
            st.subheader("Outils liés à ma progression")
            liste_exos_dispos = []
            for m in progression:
                if m in PROTOCOLE_BARLOW and "exercices" in PROTOCOLE_BARLOW[m]:
                    for exo in PROTOCOLE_BARLOW[m]["exercices"]:
                        liste_exos_dispos.append({"mod_code": m, "exo_data": exo})
            
            if not liste_exos_dispos:
                st.warning("Aucun exercice disponible.")
            else:
                for k, item in enumerate(liste_exos_dispos):
                    exo = item["exo_data"]
                    if st.button(f"👉 {item['mod_code']} - {exo['titre']}", key=f"btn_rapide_{k}", use_container_width=True):
                        st.session_state["exercice_actif"] = item
                        st.switch_page("pages/21_Barlow_Exercice.py")

        # -------------------------------------------------
        # C. BILAN HEBDO
        # -------------------------------------------------
        elif choix_sous_onglet == "📝 Bilan Hebdo":
            st.subheader("Bilan Hebdomadaire")
            choix_q = st.radio("Questionnaire :", list(QUESTIONS_HEBDO.keys()), horizontal=True)
            if choix_q:
                cfg = QUESTIONS_HEBDO[choix_q]
                with st.container(border=True):
                    st.markdown(f"**{cfg['titre']}**")
                    st.caption(cfg['description'])
                    with st.form(f"form_bilan_{choix_q}"):
                        rep = {}
                        score = 0
                        if cfg.get("ask_emotion"): rep["Emotion"] = st.text_input("Emotion :")
                        if cfg['type'] == "scale_0_8":
                            for q in cfg['questions']:
                                val = st.slider(q, 0, 8, 0)
                                rep[q] = val
                                score += val
                        elif cfg['type'] == "qcm_oasis":
                             for item in cfg['questions']:
                                lbl = item['label']
                                res = st.radio(lbl, item['options'])
                                try: score += int(res.split("=")[0])
                                except: pass
                                rep[lbl] = res

                        if st.form_submit_button("Enregistrer"):
                            lbl = choix_q
                            if "Emotion" in rep: lbl += f" ({rep['Emotion']})"
                            sauvegarder_reponse_hebdo(patient_id, lbl, str(score), rep)
                            st.success("Sauvegardé !")
                            charger_historique_local.clear()
                            time.sleep(1)
                            st.rerun()

        # -------------------------------------------------
        # D. HISTORIQUE
        # -------------------------------------------------
        elif choix_sous_onglet == "📜 Historique":
            st.subheader("Historique")
            if not df_history.empty:
                df_charts = df_history[~df_history["Questionnaire"].str.contains("Exercice", na=False)]
                if not df_charts.empty:
                    st.markdown("#### 📈 Évolution")
                    chart = alt.Chart(df_charts).mark_line(point=True).encode(x='Date', y='Score_Global', color='Type').interactive()
                    st.altair_chart(chart, use_container_width=True)
                
                st.markdown("#### 🛠️ Journal")
                for idx, row in df_history.sort_values("Date", ascending=False).iterrows():
                    with st.expander(f"{row['Date'].strftime('%d/%m')} - {row['Questionnaire']}"):
                        c_del, c_cont = st.columns([1, 5])
                        with c_del:
                            if st.button("🗑️", key=f"del_h_proto_{idx}"):
                                supprimer_reponse(patient_id, row["Date"], row["Questionnaire"])
                                charger_historique_local.clear()
                                st.rerun()
                        with c_cont:
                            try: st.json(json.loads(row["Details_Json"]))
                            except: st.write(row["Details_Json"])
            else: st.info("Historique vide.")

    # ======================================================
    # ONGLET 3 : LES 4 AGENDAS
    # ======================================================
    with onglets[2]:
        st.header("📅 Mes Agendas de suivi")
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
    # ONGLET 4 : BOITE À OUTILS
    # ======================================================
    with onglets[3]:
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
    # ONGLET 5 : ÉCHELLES
    # ======================================================
    with onglets[4]:
        st.header("📊 Mesures")
        liste_ech = [("phq9", "PHQ-9"), ("gad7", "GAD-7"), ("who5", "WHO-5"), ("isi", "ISI"), ("peg", "PEG"), ("wsas", "WSAS")]
        cols = st.columns(3)
        for i, (code, titre) in enumerate(liste_ech):
            if code in outils_autorises:
                with cols[i%3]:
                    page_map = {"phq9": "15", "gad7": "16", "isi": "17", "peg": "18", "wsas": "19", "who5": "20"}
                    if st.button(titre, key=f"btn_e_{code}", use_container_width=True): 
                        st.switch_page(f"pages/{page_map[code]}_Echelle_{code.upper()}.py")

    # ======================================================
    # ONGLET 6 : EXPORT
    # ======================================================
    with onglets[5]:
        st.header("📤 Export")
        if st.button("Générer PDF", type="primary"): st.switch_page("pages/08_Export_Rapport.py")