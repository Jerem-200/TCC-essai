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
    charger_message_therapeute, charger_taches_assignees,
    charger_journal_patient, sauvegarder_note_journal
)

from connect_drive import lister_fichiers_drive, telecharger_fichier_drive

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
    st.title(f"👋 Espace de {patient_id}")

    # 2. NAVIGATION PRINCIPALE (STABLE)
    # On définit les onglets
    liste_onglets = [
        "🏠 Tableau de Bord", 
        "🗺️ Protocole", 
        "📅 Agendas", 
        "🛠️ Outils & Exos", 
        "📊 Échelles", 
        "📚 Psychoéducation",
        "📤 Export"
    ]
    
    # Gestion du retour forcé (depuis un exercice par exemple)
    cible = st.session_state.get("target_tab", None)
    if cible and cible in liste_onglets:
        st.session_state["nav_patient_main"] = cible
        st.session_state["target_tab"] = None 

    # Initialisation de la session si besoin
    if "nav_patient_main" not in st.session_state:
        st.session_state["nav_patient_main"] = liste_onglets[0]

    # LE MENU RADIO (C'est lui qui contrôle la page active)
    # L'argument 'key' est CRUCIAL pour ne pas revenir à l'accueil
    onglet_actif = st.radio(
        "Menu Principal", 
        liste_onglets, 
        horizontal=True, 
        label_visibility="collapsed",
        key="nav_patient_main" 
    )
    st.divider()
    
    # ======================================================
    # VUE 1 : TABLEAU DE BORD (DESIGN AÉRÉ)
    # ======================================================
    if onglet_actif == "🏠 Tableau de Bord":
        
        # CHARGEMENT CIBLÉ (LAZY LOADING)
        with st.spinner("Chargement de l'accueil..."):
            msg_therapeute = charger_message_therapeute(patient_id)
            taches = charger_taches_assignees(patient_id)
            df_journal = charger_journal_patient(patient_id)

        # --- EN-TÊTE : BIENVENUE & MESSAGE ---
        # On utilise des colonnes pour ne pas prendre toute la largeur si le message est court
        c_header, c_date = st.columns([3, 1])
        with c_header:
            st.markdown(f"### 👋 Bonjour, **{patient_id}**")
        with c_date:
            st.caption(f"📅 {datetime.now().strftime('%d/%m/%Y')}")

        st.write("") # Espace vide pour aérer

        # LE MESSAGE DU THÉRAPEUTE (Style "Citation" ou "Notification")
        if msg_therapeute and msg_therapeute.strip():
            with st.container(border=True):
                c_icon, c_msg = st.columns([1, 15])
                with c_icon: st.markdown("💬")
                with c_msg:
                    st.markdown("**Message de votre thérapeute :**")
                    st.info(msg_therapeute, icon="👨‍⚕️")
        
        st.write("") # Espace vide
        st.divider()

        # --- SECTION ALERTES (GRID LAYOUT) ---
        # Au lieu d'une liste, on fait des "Cartes" sur 3 colonnes
        
        if taches:
            st.subheader("🔔 À faire cette semaine")
            
            MAP_REDIRECTION = {
                "sommeil": ("🌙 Sommeil", "pages/10_Agenda_Sommeil.py", "Remplir l'agenda"),
                "activites": ("📝 Activités", "pages/05_Registre_Activites.py", "Noter une activité"),
                "conso": ("🍷 Consos", "pages/13_Agenda_Consos.py", "Déclarer conso"),
                "compulsions": ("🛑 Compulsions", "pages/14_Agenda_Compulsions.py", "Noter un épisode"),
                "beck": ("🧩 Beck", "pages/01_Colonnes_Beck.py", "Nouvelle fiche"),
                "sorc": ("🔍 SORC", "pages/12_Analyse_SORC.py", "Analyser"),
                "problemes": ("💡 Problèmes", "pages/06_Resolution_Probleme.py", "Résoudre"),
                "balance": ("⚖️ Balance", "pages/11_Balance_Decisionnelle.py", "Décider"),
                "expo": ("🧗 Exposition", "pages/09_Exposition.py", "S'exercer"),
                "relax": ("🧘 Relaxation", "pages/07_Relaxation.py", "Écouter"),
                "phq9": ("📊 PHQ-9", "pages/15_Echelle_PHQ9.py", "S'évaluer"),
                "gad7": ("📊 GAD-7", "pages/16_Echelle_GAD7.py", "S'évaluer"),
                "who5": ("📊 WHO-5", "pages/20_Echelle_WHO5.py", "S'évaluer"),
                "isi": ("📊 ISI", "pages/17_Echelle_ISI.py", "S'évaluer"),
                "wsas": ("📊 WSAS", "pages/19_Echelle_WSAS.py", "S'évaluer")
            }

            # On crée une grille de 3 colonnes pour afficher les cartes
            cols = st.columns(3)
            
            for index, t in enumerate(taches):
                if t in MAP_REDIRECTION:
                    titre_outil, page, action_text = MAP_REDIRECTION[t]
                    
                    # On place chaque tâche dans une colonne (modulo 3)
                    with cols[index % 3]:
                        with st.container(border=True):
                            st.markdown(f"**{titre_outil}**")
                            st.caption("Priorité haute")
                            if st.button(f"👉 {action_text}", key=f"go_{t}", use_container_width=True):
                                st.switch_page(page)
        else:
            # Si rien à faire, on affiche une carte verte centrée
            c_vide, _ = st.columns([2,1])
            with c_vide:
                st.success("✅ Aucune tâche assignée. Profitez-en pour parcourir la psychoéducation !")

        st.write("")
        st.divider()

        # --- SECTION JOURNAL (FOCUS MODE) ---
        
        c_journal_gauche, c_journal_droite = st.columns([2, 1], gap="large")
        
        with c_journal_gauche:
            st.subheader("📒 Journal de bord")
            st.caption("Une pensée ? Une réussite ? Notez-le ici.")
            
            with st.container(border=True):
                with st.form("form_journal_perso", border=False):
                    date_note = st.date_input("Date", value=datetime.now(), label_visibility="collapsed")
                    contenu_note = st.text_area("Écrivez ici...", height=120, placeholder="Aujourd'hui, je me suis senti...")
                    
                    col_submit, _ = st.columns([1, 2])
                    with col_submit:
                        if st.form_submit_button("💾 Enregistrer la note", use_container_width=True, type="primary"):
                            if contenu_note.strip():
                                with st.spinner("Sauvegarde..."):
                                    sauvegarder_note_journal(patient_id, date_note, contenu_note)
                                st.success("Note ajoutée !")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.warning("Note vide.")

        with c_journal_droite:
            st.markdown("###### 🕰️ Dernières notes")
            if not df_journal.empty:
                # On affiche les 3 dernières notes max en style "Timeline" compacte
                for index, row in df_journal.head(3).iterrows():
                    d_aff = row['Date_Seance'].strftime("%d/%m") if hasattr(row['Date_Seance'], 'strftime') else str(row['Date_Seance'])[:5]
                    
                    with st.container(border=True):
                        st.markdown(f"**{d_aff}**")
                        # On coupe le texte s'il est trop long pour l'aperçu
                        apercu = row['Contenu'][:60] + "..." if len(row['Contenu']) > 60 else row['Contenu']
                        st.caption(apercu)
                        with st.popover("Lire"):
                            st.markdown(f"**Séance du {d_aff}**")
                            st.write(row['Contenu'])
            else:
                st.caption("Rien pour l'instant.")

    # ======================================================
    # VUE 2 : PROTOCOLE (SOUS-ONGLETS SLIDE)
    # ======================================================
    elif onglet_actif == "🗺️ Protocole":
        progression = charger_progression(patient_id)
        valides, notes_therapeute = charger_suivi_global(patient_id)
        devoirs = charger_etat_devoirs(patient_id)
        df_history = charger_historique_local(patient_id)
        st.header("🗺️ Mon Parcours TCC")
        
        # 1. CRÉATION DES 4 SOUS-ONGLETS (Type Slide)
        sub_tab_prog, sub_tab_outils, sub_tab_bilan, sub_tab_histo = st.tabs([
            "📍 Progression", 
            "🚀 Lanceur Rapide", 
            "📝 Bilan Hebdo", 
            "📜 Historique"
        ])

        # -------------------------------------------------
        # A. SOUS-ONGLET : PROGRESSION
        # -------------------------------------------------
        with sub_tab_prog:
            st.markdown("### 📍 Mon cheminement")
            if "last_active_module" not in st.session_state: 
                st.session_state.last_active_module = None

            for code_mod, data in PROTOCOLE_BARLOW.items():
                if code_mod in progression:
                    icon_valid = "✅" if code_mod in valides else ""
                    is_expanded = (code_mod == st.session_state.last_active_module)
                    
                    with st.expander(f"{icon_valid} {data['titre']}", expanded=is_expanded):
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
                                exclus = devoirs.get(code_mod, [])
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

        # -------------------------------------------------
        # B. SOUS-ONGLET : LANCEUR RAPIDE (Redirection Exos)
        # -------------------------------------------------
        with sub_tab_outils:
            st.subheader("🚀 Accès rapide aux outils")
            st.caption("Retrouvez ici tous les exercices débloqués, classés par module.")
            st.write("")

            exos_trouves = False
            for code_mod, data in PROTOCOLE_BARLOW.items():
                if code_mod in progression:
                    if "exercices" in data and data["exercices"]:
                        for i, exo in enumerate(data["exercices"]):
                            exos_trouves = True
                            c_txt, c_btn = st.columns([5, 1])
                            with c_txt:
                                st.markdown(f"🔹 **{exo['titre']}** <small style='color:grey'>({data['titre']})</small>", unsafe_allow_html=True)
                            with c_btn:
                                key_btn = f"btn_light_{code_mod}_{i}"
                                if st.button("Ouvrir", key=key_btn, use_container_width=True):
                                    st.session_state["exercice_actif"] = {"mod_code": code_mod, "exo_data": exo}
                                    st.switch_page("pages/21_Barlow_Exercice.py")
                            st.divider()

            if not exos_trouves:
                st.info("Aucun exercice disponible.")
                st.caption("Avancez dans les modules pour débloquer des outils.")

        # -------------------------------------------------
        # C. SOUS-ONGLET : BILAN HEBDO
        # -------------------------------------------------
        with sub_tab_bilan:
            st.subheader("Bilan Hebdomadaire")
            
            # Ajout d'une clé (key) pour stabiliser le selectbox
            choix_q = st.selectbox("Questionnaire :", list(QUESTIONS_HEBDO.keys()), key="sb_bilan_hebdo")
            
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
        # D. SOUS-ONGLET : HISTORIQUE
        # -------------------------------------------------
        with sub_tab_histo:
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
    # VUE 3 : AGENDAS
    # ======================================================
    elif onglet_actif == "📅 Agendas":
        outils_autorises = charger_outils_autorises(patient_id)
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
    # VUE 4 : OUTILS
    # ======================================================
    elif onglet_actif == "🛠️ Outils & Exos":
        outils_autorises = charger_outils_autorises(patient_id)
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
        outils_autorises = charger_outils_autorises(patient_id)
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
    # ONGLET 6 : PSYCHOÉDUCATION (HYBRIDE LOCAL + CLOUD)
    # ======================================================
    elif onglet_actif == "📚 Psychoéducation":
        st.header("📚 Ressources Psycho-éducatives")
        st.write("Consultez les fiches de référence ou accédez à la bibliothèque partagée.")

        # --- 1. FONCTION D'AFFICHAGE LOCAL (Pour les fichiers du code de base) ---
        def afficher_ressource_locale(titre_pdf, nom_fichier_pdf, liste_images=[]):
            if os.path.exists(nom_fichier_pdf):
                with open(nom_fichier_pdf, "rb") as f:
                    st.download_button(
                        label=f"📥 Télécharger '{titre_pdf}' (PDF)",
                        data=f,
                        file_name=os.path.basename(nom_fichier_pdf),
                        mime="application/pdf",
                        use_container_width=True
                    )
            else:
                st.warning(f"Fichier local introuvable : {nom_fichier_pdf}")
            
            for img in liste_images:
                if os.path.exists(img):
                    st.image(img, use_container_width=True)

        # --- 2. FONCTION D'AFFICHAGE CLOUD (Pour les fichiers ajoutés par le thérapeute) ---
        def afficher_fichier_cloud(file_info):
            f_name = file_info['name']
            f_id = file_info['id']
            f_mime = file_info.get('mimeType', 'application/pdf')
            with st.container(border=True):
                icon = "📄" if "pdf" in f_mime else "🖼️"
                st.write(f"**{icon} {f_name}**")
                content = telecharger_fichier_drive(f_id)
                if content:
                    st.download_button("Télécharger", content, file_name=f_name, mime=f_mime, key=f"dl_cloud_{f_id}")
                    if "image" in f_mime: st.image(content)

        # --- ONGLETS ---
        t_emotions, t_roue, t_distorsions, t_vrac = st.tabs([
            "Fonctions Émotions", 
            "Roue Émotions", 
            "Distorsions", 
            "📂 Bibliothèque Complète"
        ])

        # A. Contenu LOCAL (Code de base)
        with t_emotions:
            st.subheader("À quoi servent nos émotions ?")
            afficher_ressource_locale("Fiche Fonctions", "assets/Les fonctions des émotions.pdf", ["assets/fonctions.jpg"])

        with t_roue:
            st.subheader("La Roue de Plutchik")
            afficher_ressource_locale("Roue des sentiments", "assets/Roue des sentiments de Plutchik.pdf", ["assets/roue.jpg"])

        with t_distorsions:
            st.subheader("Les Distorsions Cognitives")
            afficher_ressource_locale("Liste Distorsions", "assets/Distorsions cognitives.pdf", ["assets/disto_1.jpg"])

        # B. Contenu CLOUD (Dynamique)
        with t_vrac:
            st.subheader("📂 Documents additionnels (Cloud)")
            # On va chercher les fichiers sur Google Cloud
            tous_fichiers_cloud = lister_fichiers_drive()
            
            if tous_fichiers_cloud:
                cols = st.columns(3)
                for i, f in enumerate(tous_fichiers_cloud):
                    with cols[i % 3]:
                        afficher_fichier_cloud(f)
            else:
                st.info("Aucun document supplémentaire n'a été ajouté par le thérapeute.")


    # ======================================================
    # VUE 6 : EXPORT
    # ======================================================
    elif onglet_actif == "📤 Export":
        st.header("📤 Export")
        if st.button("Générer PDF", type="primary"): st.switch_page("pages/08_Export_Rapport.py")