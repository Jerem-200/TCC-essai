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
    sauvegarder_reponse_hebdo, supprimer_reponse, load_data,
    charger_historique_complet_cache # Si tu l'as ajoutée dans connect_db, sinon définir ici
)

# Si charger_historique_complet_cache n'est pas dans connect_db, on le garde ici en local
@st.cache_data(ttl=300)
def charger_historique_local(uid):
    raw = load_data("Reponses_Hebdo")
    if raw:
        df = pd.DataFrame(raw)
        if "Patient" in df.columns:
            df = df[df["Patient"] == uid]
            if not df.empty:
                df["Date"] = pd.to_datetime(df["Date"])
                return df
    return pd.DataFrame()

def afficher_vue_patient(patient_id):
    
    # 1. CHARGEMENT DONNÉES
    outils_autorises = charger_outils_autorises(patient_id)
    progression = charger_progression(patient_id)
    devoirs = charger_etat_devoirs(patient_id)
    valides, notes_therapeute = charger_suivi_global(patient_id)
    
    st.title(f"👋 Espace de {patient_id}")

    # 2. CRÉATION DES ONGLETS (Navigation Principale)
    # C'est ici qu'on définit ta structure idéale
    onglets = st.tabs([
        "🏠 Tableau de Bord", 
        "🗺️ Protocole", 
        "📅 Agendas", 
        "🛠️ Outils & Exos", 
        "📊 Échelles", 
        "📝 Bilan Hebdo",
        "📜 Historique",
        "📤 Export"
    ])

    # ======================================================
    # ONGLET 1 : TABLEAU DE BORD (Accueil + Note Séance)
    # ======================================================
    with onglets[0]:
        st.markdown("### 📌 Ma situation aujourd'hui")
        
        # Indicateurs rapides
        c1, c2, c3 = st.columns(3)
        nb_valides = len(valides)
        with c1: 
            st.metric("Modules Terminés", f"{nb_valides} / {len(PROTOCOLE_BARLOW)}")
            st.progress(nb_valides / len(PROTOCOLE_BARLOW))
        with c2:
            st.metric("Outils Débloqués", f"{len(outils_autorises)}")
        with c3:
            st.info("💡 **Conseil du jour** : N'oubliez pas de remplir votre bilan hebdo.")

        st.divider()

        # NOUVELLE FONCTIONNALITÉ : NOTE DE SÉANCE
        st.subheader("📒 Mon Journal de Séance")
        st.caption("Un espace pour noter ce que vous retenez de vos échanges avec le psychologue.")
        
        with st.form("form_note_seance"):
            col_d, col_t = st.columns([1, 3])
            with col_d:
                date_note = st.date_input("Date de la séance", value=datetime.now())
            with col_t:
                contenu_note = st.text_area("Résumé & Points clés :", height=100, placeholder="Aujourd'hui, nous avons travaillé sur...")
            
            if st.form_submit_button("💾 Enregistrer ma note", type="primary"):
                payload = {"type": "note_personnelle", "contenu": contenu_note}
                sauvegarder_reponse_hebdo(patient_id, f"Note Séance - {date_note}", "Perso", payload)
                st.success("Note enregistrée dans l'historique !")
                time.sleep(1)
                st.rerun()

    # ======================================================
    # ONGLET 2 : PROTOCOLE (BARLOW) - COMPLET
    # ======================================================
    with onglets[1]:
        st.header("🗺️ Mon Parcours TCC")
        
        if "last_active_module" not in st.session_state:
            st.session_state.last_active_module = "module0"

        for code_mod, data in PROTOCOLE_BARLOW.items():
            is_done = code_mod in valides
            icon = "✅" if is_done else "🟦"
            expanded = (code_mod == st.session_state.last_active_module)
            
            # MODULE ACCESSIBLE
            if code_mod in progression:
                with st.expander(f"{icon} {data['titre']}", expanded=expanded):
                    
                    t_seance, t_docs = st.tabs(["⚡ Séance en cours", "📂 Documents"])
                    
                    with t_seance:
                        st.info(f"**Objectifs :** {data['objectifs']}")
                        
                        # --- FORMULAIRE DE TRAVAIL ---
                        with st.form(key=f"form_proto_{code_mod}"):
                            checklist_results = []
                            
                            # A. EXAMEN (Si présent)
                            if data['examen_devoirs']:
                                st.markdown("**1️⃣ Retour sur les tâches**")
                                for idx, task in enumerate(data['examen_devoirs']):
                                    chk = st.checkbox(task['titre'], key=f"chk_ex_{code_mod}_{idx}")
                                    checklist_results.append(chk)
                                st.write("---")

                            # B. ÉTAPES DE LA SÉANCE
                            st.markdown("**2️⃣ Contenu de la séance**")
                            for idx, etape in enumerate(data['etapes_seance']):
                                chk = st.checkbox(etape['titre'], key=f"chk_st_{code_mod}_{idx}", help=etape.get('details'))
                                checklist_results.append(chk)
                            st.write("---")
                            
                            # C. DEVOIRS (Si présents)
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

                            # D. NOTES DU THÉRAPEUTE (C'est ce qu'il manquait !)
                            st.markdown("**4️⃣ Notes & Commentaires**")
                            note_precedente = notes_therapeute.get(code_mod, "")
                            nouvelle_note = st.text_area("Observations :", value=note_precedente, height=100)

                            # BOUTON VALIDATION
                            if st.form_submit_button("💾 Sauvegarder l'avancement", type="primary"):
                                # 1. Sauvegarde Devoirs (ceux décochés sont exclus)
                                if data['taches_domicile']:
                                    exclus = [k for k, v in enumerate(liste_devoirs_temp) if not v]
                                    devoirs[code_mod] = exclus
                                    sauvegarder_etat_devoirs(patient_id, devoirs)
                                
                                # 2. Sauvegarde Note
                                notes_therapeute[code_mod] = nouvelle_note
                                
                                # 3. Validation Module (Si tout coché)
                                all_ok = all(checklist_results) if checklist_results else True
                                if all_ok and code_mod not in valides:
                                    valides.append(code_mod)
                                    st.toast("Module Validé !", icon="🎉")
                                elif not all_ok and code_mod in valides:
                                    valides.remove(code_mod)
                                    st.toast("Module remis en cours", icon="ℹ️")
                                
                                sauvegarder_suivi_global(patient_id, valides, notes_therapeute)
                                st.session_state.last_active_module = code_mod
                                time.sleep(0.5)
                                st.rerun()

                        # --- LANCEMENT EXERCICE SPÉCIFIQUE ---
                        if data.get('exercices'):
                            st.info("👇 **Outil pratique associé :**")
                            for exo in data['exercices']:
                                if st.button(f"🚀 Lancer : {exo['titre']}", key=f"btn_exo_{code_mod}"):
                                    st.session_state["exercice_actif"] = {"mod_code": code_mod, "exo_data": exo}
                                    st.switch_page("pages/21_Barlow_Exercice.py")
                    
                    with t_docs:
                        if data.get('pdfs_module'):
                            for p in data['pdfs_module']:
                                if os.path.exists(p):
                                    with open(p, "rb") as f:
                                        st.download_button(f"📥 {os.path.basename(p)}", f, file_name=os.path.basename(p), key=f"dl_{code_mod}")
                        else: st.caption("Aucun document.")
            
            # MODULE VERROUILLÉ
            else:
                with st.container():
                    st.write(f"🔒 **{data['titre']}** (Bientôt disponible)")
                    st.divider()

    # ======================================================
    # ONGLET 3 : LES 4 AGENDAS
    # ======================================================
    with onglets[2]:
        st.header("📅 Mes Agendas de suivi")
        st.caption("Cliquez pour ouvrir l'agenda.")
        
        col_a1, col_a2 = st.columns(2)
        
        # 1. SOMMEIL
        with col_a1:
            if "sommeil" in outils_autorises:
                with st.container(border=True):
                    st.subheader("🌙 Sommeil")
                    st.write("Suivi des nuits et de la qualité.")
                    if st.button("Ouvrir Agenda Sommeil", use_container_width=True): 
                        st.switch_page("pages/10_Agenda_Sommeil.py")
            else: st.info("🌙 Agenda Sommeil (Verrouillé)")

            # 2. CONSOMMATIONS
            if "conso" in outils_autorises:
                with st.container(border=True):
                    st.subheader("🍷 Consommations")
                    st.write("Suivi des prises de substances.")
                    if st.button("Ouvrir Agenda Consos", use_container_width=True): 
                        st.switch_page("pages/13_Agenda_Consos.py")
            else: st.info("🍷 Agenda Consos (Verrouillé)")

        with col_a2:
            # 3. ACTIVITÉS
            if "activites" in outils_autorises:
                with st.container(border=True):
                    st.subheader("📝 Activités")
                    st.write("Registre d'activités et humeur.")
                    if st.button("Ouvrir Registre Activités", use_container_width=True): 
                        st.switch_page("pages/05_Registre_Activites.py")
            else: st.info("📝 Registre Activités (Verrouillé)")
            
            # 4. COMPULSIONS
            if "compulsions" in outils_autorises:
                with st.container(border=True):
                    st.subheader("🛑 Compulsions")
                    st.write("Suivi des crises et compulsions.")
                    if st.button("Ouvrir Agenda Compulsions", use_container_width=True): 
                        st.switch_page("pages/14_Agenda_Compulsions.py")
            else: st.info("🛑 Agenda Compulsions (Verrouillé)")

    # ======================================================
    # ONGLET 4 : BOITE À OUTILS (EXERCICES)
    # ======================================================
    with onglets[3]:
        st.header("🛠️ Boîte à outils TCC")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            if "beck" in outils_autorises:
                st.info("**Colonnes de Beck**")
                if st.button("Lancer Beck", use_container_width=True): st.switch_page("pages/01_Colonnes_Beck.py")
            if "sorc" in outils_autorises:
                st.info("**Analyse SORC**")
                if st.button("Lancer SORC", use_container_width=True): st.switch_page("pages/12_Analyse_SORC.py")
        
        with c2:
            if "problemes" in outils_autorises:
                st.info("**Résolution Problème**")
                if st.button("Lancer Résolution", use_container_width=True): st.switch_page("pages/06_Resolution_Probleme.py")
            if "balance" in outils_autorises:
                st.info("**Balance Décisionnelle**")
                if st.button("Lancer Balance", use_container_width=True): st.switch_page("pages/11_Balance_Decisionnelle.py")
        
        with c3:
            if "expo" in outils_autorises:
                st.info("**Exposition**")
                if st.button("Lancer Exposition", use_container_width=True): st.switch_page("pages/09_Exposition.py")
            if "relax" in outils_autorises:
                st.info("**Relaxation**")
                if st.button("Lancer Relaxation", use_container_width=True): st.switch_page("pages/07_Relaxation.py")

    # ======================================================
    # ONGLET 5 : ÉCHELLES
    # ======================================================
    with onglets[4]:
        st.header("📊 Mesures Psychométriques")
        
        # Liste simplifiée pour générer les boutons
        liste_echelles = [
            ("phq9", "PHQ-9 (Dépression)", "pages/15_Echelle_PHQ9.py"),
            ("gad7", "GAD-7 (Anxiété)", "pages/16_Echelle_GAD7.py"),
            ("who5", "WHO-5 (Bien-être)", "pages/20_Echelle_WHO5.py"),
            ("isi", "ISI (Insomnie)", "pages/17_Echelle_ISI.py"),
            ("peg", "PEG (Douleur)", "pages/18_Echelle_PEG.py"),
            ("wsas", "WSAS (Handicap)", "pages/19_Echelle_WSAS.py")
        ]
        
        cols = st.columns(3)
        for i, (code, titre, page) in enumerate(liste_echelles):
            if code in outils_autorises:
                with cols[i % 3]:
                    with st.container(border=True):
                        st.markdown(f"**{titre}**")
                        if st.button("Remplir", key=f"btn_ech_{code}", use_container_width=True):
                            st.switch_page(page)

    # ======================================================
    # ONGLET 6 : BILAN HEBDO
    # ======================================================
    with onglets[5]:
        st.header("📝 Bilan Hebdomadaire")
        choix_q = st.selectbox("Sélectionnez le bilan :", list(QUESTIONS_HEBDO.keys()))
        
        if choix_q:
            cfg = QUESTIONS_HEBDO[choix_q]
            st.info(cfg['description'])
            with st.form("form_bilan_hebdo"):
                rep = {}
                score = 0
                if cfg.get("ask_emotion"):
                    rep["Emotion"] = st.text_input("Emotion dominante de la semaine :")
                
                if cfg['type'] == "scale_0_8":
                    for q in cfg['questions']:
                        val = st.slider(q, 0, 8, 0)
                        rep[q] = val
                        score += val
                
                if st.form_submit_button("Envoyer le bilan", type="primary"):
                    label = choix_q
                    if "Emotion" in rep: label += f" ({rep['Emotion']})"
                    sauvegarder_reponse_hebdo(patient_id, label, str(score), rep)
                    st.success("Bilan envoyé au thérapeute !")
                    charger_historique_local.clear()

    # ======================================================
    # ONGLET 7 : HISTORIQUE
    # ======================================================
    with onglets[6]:
        st.header("📜 Historique Complet")
        df_hist = charger_historique_local(patient_id)
        
        if not df_hist.empty:
            # Graphique
            df_chart = df_hist[~df_hist["Questionnaire"].str.contains("Note|Exercice", na=False)]
            if not df_chart.empty:
                st.markdown("##### 📈 Évolution")
                chart = alt.Chart(df_chart).mark_line(point=True).encode(
                    x='Date', y='Score_Global', color='Questionnaire'
                ).interactive()
                st.altair_chart(chart, use_container_width=True)
            
            # Liste
            st.markdown("##### 🗓️ Journal")
            for idx, row in df_hist.sort_values("Date", ascending=False).iterrows():
                label_titre = f"{row['Date'].strftime('%d/%m')} - {row['Questionnaire']}"
                with st.expander(label_titre):
                    col_del, col_cont = st.columns([1, 5])
                    with col_del:
                        if st.button("🗑️", key=f"del_h_{idx}"):
                            supprimer_reponse(patient_id, row["Date"], row["Questionnaire"])
                            charger_historique_local.clear()
                            st.rerun()
                    with col_cont:
                        try: st.json(json.loads(row["Details_Json"]))
                        except: st.write(row["Details_Json"])
        else:
            st.info("Aucun historique disponible.")

    # ======================================================
    # ONGLET 8 : EXPORT
    # ======================================================
    with onglets[7]:
        st.header("📤 Export des données")
        st.write("Téléchargez un rapport complet de vos progrès au format PDF.")
        if st.button("Générer mon rapport PDF", type="primary"):
            st.switch_page("pages/08_Export_Rapport.py")