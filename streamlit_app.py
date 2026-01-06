import streamlit as st
import time
from datetime import datetime
import pandas as pd
import json
import os
import random
import string

# Imports DB
from connect_db import (
    verifier_therapeute, verifier_code_patient, recuperer_mes_patients,
    charger_outils_autorises, sauvegarder_outils_autorises, 
    charger_progression, charger_etat_devoirs, charger_suivi_global,
    charger_donnees_specifiques, sauvegarder_progression, 
    load_data, generer_code_securise, sauvegarder_etat_devoirs, sauvegarder_suivi_global
)

# Imports Visualisation & Config
from visualisations import (
    afficher_activites, afficher_sommeil, afficher_conso, afficher_compulsions,
    afficher_phq9, afficher_gad7, afficher_isi, afficher_peg, afficher_who5, afficher_wsas
)
from protocole_config import PROTOCOLE_BARLOW

# IMPORT DE LA VUE PATIENT
from vue_patient import afficher_vue_patient

# CONFIGURATION PAGE
st.set_page_config(page_title="Compagnon TCC", page_icon="🧠", layout="wide")
st.markdown("<style>[data-testid='stSidebarNav'] {display: none;}</style>", unsafe_allow_html=True)

# GESTION SESSION
if "authentifie" not in st.session_state: st.session_state.authentifie = False
if "user_type" not in st.session_state: st.session_state.user_type = None 
if "user_id" not in st.session_state: st.session_state.user_id = "" 
if "patient_selectionne" not in st.session_state: st.session_state.patient_selectionne = None

# Variable pour stocker l'identité du thérapeute quand il "espionne" un patient
if "original_therapist_id" not in st.session_state: st.session_state.original_therapist_id = None

# =========================================================
# 1. ÉCRAN DE CONNEXION
# =========================================================
if not st.session_state.authentifie:
    st.title("🧠 Compagnon TCC")
    t_pat, t_pro = st.tabs(["👤 Accès Patient", "🩺 Accès Thérapeute"])
    
    with t_pat:
            with st.form("login_p"):
                code_input = st.text_input("Code Patient :", type="password")
                if st.form_submit_button("Entrer"):
                    code_clean = code_input.strip()
                    if verifier_code_patient(code_clean):
                        real_id = code_clean 
                        try:
                            data_codes = load_data("Codes_Patients")
                            if data_codes:
                                df_codes = pd.DataFrame(data_codes)
                                match = df_codes[df_codes["Code"].astype(str).str.strip() == code_clean]
                                if not match.empty:
                                    real_id = match.iloc[0]["Identifiant"]
                        except: pass

                        st.session_state.authentifie = True
                        st.session_state.user_type = "patient"
                        st.session_state.user_id = real_id
                
    with t_pro:
        with st.form("login_t"):
            u = st.text_input("Identifiant")
            p = st.text_input("Mot de passe", type="password")
            if st.form_submit_button("Connexion Pro"):
                tid = verifier_therapeute(u, p)
                if tid:
                    st.session_state.authentifie = True
                    st.session_state.user_type = "therapeute"
                    st.session_state.user_id = tid
                    st.session_state.username_pro = u
                    st.rerun()
                else: st.error("Erreur d'identification")
    st.stop()

# =========================================================
# 2. LOGIQUE PATIENT
# =========================================================
if st.session_state.user_type == "patient":
    # Si c'est un thérapeute qui regarde, on met un bandeau d'avertissement
    if st.session_state.original_therapist_id:
        st.warning(f"👀 Mode Aperçu : Vous voyez l'interface de {st.session_state.user_id}")

    afficher_vue_patient(st.session_state.user_id)
    
    with st.sidebar:
        display_id = st.session_state.user_id 
        try:
            infos = load_data("Codes_Patients")
            if infos:
                df_infos = pd.DataFrame(infos)
                # Recherche insensible à la casse et espaces
                code_actuel = str(st.session_state.user_id).strip().upper()
                match = df_infos[df_infos["Identifiant"].astype(str).str.strip().str.upper() == code_actuel]
                if not match.empty:
                    col_id = "Identifiant" if "Identifiant" in df_infos.columns else "Commentaire"
                    display_id = match.iloc[0][col_id]
        except: pass
        
        outils_autorises = charger_outils_autorises(st.session_state.user_id)

        st.write(f"👤 ID: **{display_id}**")
        
        # --- LOGIQUE DE RETOUR THÉRAPEUTE ---
        if st.session_state.original_therapist_id:
            st.divider()
            if st.button("⬅️ Retour Espace Pro", type="primary"):
                # On restaure l'identité du thérapeute
                st.session_state.user_type = "therapeute"
                st.session_state.user_id = st.session_state.original_therapist_id
                st.session_state.original_therapist_id = None # On vide la mémoire
                st.rerun()
        else:
            # Déconnexion classique pour un vrai patient
            if st.button("Se déconnecter", key="logout_pat_sidebar"):
                st.session_state.authentifie = False
                st.rerun()
        
        st.divider()
        
        st.title("Navigation")
        st.page_link("streamlit_app.py", label="🏠 Accueil")
        st.divider()
        
        st.caption("📅 Agendas")
        if "sommeil" in outils_autorises: st.page_link("pages/10_Agenda_Sommeil.py", label="🌙 Sommeil")
        if "activites" in outils_autorises: st.page_link("pages/05_Registre_Activites.py", label="📝 Activités")
        if "conso" in outils_autorises: st.page_link("pages/13_Agenda_Consos.py", label="🍷 Consos")
        if "compulsions" in outils_autorises: st.page_link("pages/14_Agenda_Compulsions.py", label="🛑 Compulsions")
        
        st.caption("🛠️ Outils")
        if "beck" in outils_autorises: st.page_link("pages/01_Colonnes_Beck.py", label="🧩 Beck")
        if "sorc" in outils_autorises: st.page_link("pages/12_Analyse_SORC.py", label="🔍 SORC")
        if "problemes" in outils_autorises: st.page_link("pages/06_Resolution_Probleme.py", label="💡 Problèmes")
        if "balance" in outils_autorises: st.page_link("pages/11_Balance_Decisionnelle.py", label="⚖️ Balance")
        if "expo" in outils_autorises: st.page_link("pages/09_Exposition.py", label="🧗 Exposition")
        if "relax" in outils_autorises: st.page_link("pages/07_Relaxation.py", label="🧘 Relaxation")
        
        st.caption("📊 Échelles")
        if "phq9" in outils_autorises: st.page_link("pages/15_Echelle_PHQ9.py", label="📊 PHQ-9")
        if "gad7" in outils_autorises: st.page_link("pages/16_Echelle_GAD7.py", label="📊 GAD-7")
        if "who5" in outils_autorises: st.page_link("pages/20_Echelle_WHO5.py", label="📊 WHO-5")
        if "isi" in outils_autorises: st.page_link("pages/17_Echelle_ISI.py", label="📊 ISI")
        if "peg" in outils_autorises: st.page_link("pages/18_Echelle_PEG.py", label="📊 PEG")
        if "wsas" in outils_autorises: st.page_link("pages/19_Echelle_WSAS.py", label="📊 WSAS")
        
        st.caption("📜 Bilan")
        st.page_link("pages/04_Historique.py", label="Historique")
        st.page_link("pages/08_Export_Rapport.py", label="Export PDF")

# =========================================================
# 3. LOGIQUE THÉRAPEUTE
# =========================================================
elif st.session_state.user_type == "therapeute":
    
    c1, c2 = st.columns([6, 1])
    with c1: st.title("🩺 Espace Thérapeute")
    with c2: 
        if st.button("Déconnexion"):
            st.session_state.authentifie = False
            st.rerun()

    # --- CHARGEMENT LISTE PATIENTS ---
    if "liste_patients_cache" not in st.session_state:
        df_pats = recuperer_mes_patients(st.session_state.user_id)
        if not df_pats.empty:
            st.session_state.liste_patients_cache = df_pats["Identifiant"].unique().tolist()
        else: st.session_state.liste_patients_cache = []

    # --- STRUCTURE DES ONGLETS (AJOUT DE GESTION PATIENT) ---
    tab_dash, tab_gestion, tab_proto, tab_exos, tab_visu, tab_res = st.tabs([
        "🏠 Tableau de Bord", 
        "👤 Gestion Patients",
        "🗺️ Protocole & Accès", 
        "📝 Gestion Exercices",
        "📊 Visualisation",
        "📚 Ressources"
    ])

    # =================================================
    # ONGLET 1 : TABLEAU DE BORD (STATS & MEMO)
    # =================================================
    with tab_dash:
        st.header("🏠 Tableau de bord")
        
        # NOTE : J'ai retiré la création et la sélection d'ici pour les mettre dans "Gestion"
        # Mais on garde une KPI rapide
        k1, k2, k3 = st.columns(3)
        with k1: st.metric("Patients suivis", len(st.session_state.liste_patients_cache))
        with k2: st.metric("Séances cette semaine", "4") # Placeholder
        with k3: st.metric("Messages non lus", "0") # Placeholder
        
        st.divider()
        st.markdown("#### 📝 Mémo Personnel (To-Do)")
        if "therapeute_memo" not in st.session_state: st.session_state.therapeute_memo = ""
        nouvelle_note = st.text_area("À faire :", value=st.session_state.therapeute_memo, height=150, placeholder="Ex: Relancer PAT-003 pour son agenda sommeil...")
        st.session_state.therapeute_memo = nouvelle_note

    # =================================================
    # ONGLET 2 : GESTION PATIENTS (CRÉATION & INFOS)
    # =================================================
    with tab_gestion:
        col_select, col_create = st.columns([1, 1])
        
        # A. SÉLECTION ET INFORMATIONS DU PATIENT
        with col_select:
            st.subheader("📂 Consulter un dossier")
            
            if st.session_state.liste_patients_cache:
                # Sélection principale qui pilote toute l'app
                patient_precedent = st.session_state.patient_selectionne
                st.session_state.patient_selectionne = st.selectbox(
                    "Sélectionner le patient actif :", 
                    st.session_state.liste_patients_cache,
                    index=st.session_state.liste_patients_cache.index(patient_precedent) if patient_precedent in st.session_state.liste_patients_cache else 0
                )
                
                patient_sel = st.session_state.patient_selectionne
                
                # --- BLOC INFOS SENSIBLES (SÉCURISÉ) ---
                with st.container(border=True):
                    st.markdown(f"#### ℹ️ Infos : {patient_sel}")
                    
                    # 1. Récupération du Code Patient (Comme avant)
                    code_patient = "Introuvable"
                    try:
                        all_codes = load_data("Codes_Patients")
                        if all_codes:
                            df_c = pd.DataFrame(all_codes)
                            row = df_c[df_c["Identifiant"] == patient_sel]
                            if not row.empty:
                                code_patient = row.iloc[0]["Code"]
                    except: pass
                    
                    # 2. Logique d'affichage sécurisé
                    # On utilise une clé unique pour savoir si CE patient est déverrouillé
                    key_reveal = f"reveal_state_{patient_sel}"
                    if key_reveal not in st.session_state: st.session_state[key_reveal] = False

                    c_code, c_view = st.columns([1, 1])
                    
                    with c_code:
                        if not st.session_state[key_reveal]:
                            # CAS 1 : C'est masqué
                            st.info("🔒 Code patient masqué")
                            pwd_verif = st.text_input("Confirmez votre mot de passe pro :", type="password", key=f"input_pwd_{patient_sel}")
                            
                            if st.button("🔓 Révéler", key=f"btn_reveal_{patient_sel}"):
                                # On utilise l'identifiant de connexion (u) et pas l'ID interne (tid)
                                login_a_verifier = st.session_state.get("username_pro", st.session_state.user_id)
                                if verifier_therapeute(login_a_verifier, pwd_verif):
                                    st.session_state[key_reveal] = True
                                    st.rerun()
                                else:
                                    st.error("Mot de passe incorrect.")
                        else:
                            # CAS 2 : C'est révélé
                            st.text_input("🔑 Code d'accès (Mot de passe)", value=code_patient, disabled=True)
                            if st.button("🔒 Masquer", key=f"btn_hide_{patient_sel}"):
                                st.session_state[key_reveal] = False
                                st.rerun()
                    
                    with c_view:
                        # On aligne le bouton "Voir interface" vers le bas pour qu'il soit joli
                        st.write("") 
                        st.write("") 
                        if st.session_state[key_reveal]: st.write("") # Petit ajustement d'alignement si révélé
                        
                        if st.button("👁️ Voir l'interface de ce patient", type="primary"):
                            st.session_state.original_therapist_id = st.session_state.user_id
                            st.session_state.user_type = "patient"
                            st.session_state.user_id = patient_sel
                            st.rerun()

            else:
                st.info("Vous n'avez pas encore de patients.")

        # B. CRÉATION NOUVEAU PATIENT (DÉPLACÉ ICI)
        with col_create:
            st.subheader("➕ Créer un Nouveau Patient")
            with st.container(border=True):
                # Calcul de l'ID avec la méthode Globale (pour unicité)
                tous_les_codes = load_data("Codes_Patients")
                nb_total_absolu = len(tous_les_codes) if tous_les_codes else 0
                prochain_id = f"PAT-{nb_total_absolu + 1:03d}"
                
                st.info(f"Prochain ID suggéré : **{prochain_id}**")
                id_dossier = st.text_input("Identifiant Dossier", value=prochain_id)
                
                if st.button("Générer l'accès maintenant"):
                    ac_code = generer_code_securise("TCC")
                    from connect_db import save_data 
                    
                    # Sauvegarde Code
                    save_data("Codes_Patients", [ac_code, st.session_state.user_id, id_dossier, str(datetime.now().date())])
                    # Init Progression (Module 0 uniquement)
                    sauvegarder_progression(id_dossier, ["module0"])
                    
                    st.success(f"Patient créé ! Code : {ac_code}")
                    # Refresh cache
                    if "liste_patients_cache" in st.session_state: del st.session_state.liste_patients_cache
                    recuperer_mes_patients.clear()
                    time.sleep(1)
                    st.rerun()

    # =================================================
    # ONGLET 3 : PROTOCOLE (MODULES + OUTILS)
    # =================================================
    with tab_proto:
        patient_sel = st.session_state.patient_selectionne
        
        if not patient_sel:
            st.info("Veuillez sélectionner un patient dans l'onglet 'Gestion Patients'.")
        else:
            st.markdown(f"### Gestion du Protocole : **{patient_sel}**")

            # --- 2. PILOTAGE MODULES BARLOW ---
            cache_key = f"cache_data_{patient_sel}"
            if cache_key not in st.session_state:
                st.session_state[cache_key] = {
                    "progression": charger_progression(patient_sel),
                    "devoirs": charger_etat_devoirs(patient_sel),
                    "valides": charger_suivi_global(patient_sel)[0],
                    "notes": charger_suivi_global(patient_sel)[1]
                }
            
            data_session = st.session_state[cache_key]
            progression_patient = data_session["progression"]
            devoirs_exclus_memoire = data_session["devoirs"]
            modules_valides_db = data_session["valides"]
            notes_seance_db = data_session["notes"]
            
            if "last_active_module" not in st.session_state: st.session_state.last_active_module = "module0"

            st.markdown("#### 🗺️ Modules Barlow")
            nb_total = len(PROTOCOLE_BARLOW)
            nb_fait = len(modules_valides_db)
            st.progress(min(nb_fait / nb_total, 1.0), text=f"Avancement : {nb_fait}/{nb_total} modules terminés")

            for code_mod, data in PROTOCOLE_BARLOW.items():
                if code_mod in modules_valides_db: icon = "✅"
                elif code_mod in progression_patient: icon = "🟦"
                else: icon = "🔒"
                
                should_be_expanded = (code_mod == st.session_state.last_active_module)
                
                col_mod, col_btn = st.columns([0.85, 0.15])
                with col_mod:
                    with st.expander(f"{icon} {data['titre']}", expanded=should_be_expanded):
                        t_act, t_doc = st.tabs(["⚡ Séance", "📂 Docs"])
                        with t_act:
                            with st.form(key=f"form_{patient_sel}_{code_mod}"):
                                check_list = []
                                if data['examen_devoirs']:
                                    st.caption("Examen tâches")
                                    for idx, d in enumerate(data['examen_devoirs']):
                                        check_list.append(st.checkbox(d['titre'], key=f"ex_{patient_sel}_{code_mod}_{idx}"))
                                st.caption("Étapes Séance")
                                for idx_e, etape in enumerate(data['etapes_seance']):
                                    check_list.append(st.checkbox(etape['titre'], key=f"st_{patient_sel}_{code_mod}_{idx_e}", help=etape.get('details')))
                                dev_temp = []
                                if data['taches_domicile']:
                                    st.caption("Assignation Devoirs")
                                    excl = devoirs_exclus_memoire.get(code_mod, [])
                                    for j, dev in enumerate(data['taches_domicile']):
                                        dev_temp.append(st.checkbox(dev['titre'], value=(j not in excl), key=f"dv_{patient_sel}_{code_mod}_{j}"))
                                note = st.text_area("Note", value=notes_seance_db.get(code_mod, ""), height=80)
                                
                                if st.form_submit_button("💾 Enregistrer"):
                                    notes_seance_db[code_mod] = note
                                    st.session_state[cache_key]["notes"] = notes_seance_db
                                    
                                    if data['taches_domicile']:
                                        new_excl = [k for k, c in enumerate(dev_temp) if not c]
                                        devoirs_exclus_memoire[code_mod] = new_excl
                                        st.session_state[cache_key]["devoirs"] = devoirs_exclus_memoire
                                        sauvegarder_etat_devoirs(patient_sel, devoirs_exclus_memoire)

                                    if code_mod not in progression_patient:
                                        progression_patient.append(code_mod)
                                        sauvegarder_progression(patient_sel, progression_patient)
                                        st.session_state[cache_key]["progression"] = progression_patient

                                    all_ok = all(check_list) if check_list else True
                                    if all_ok: 
                                        if code_mod not in modules_valides_db: modules_valides_db.append(code_mod)
                                    else:
                                        if code_mod in modules_valides_db: modules_valides_db.remove(code_mod)
                                    
                                    st.session_state[cache_key]["valides"] = modules_valides_db
                                    sauvegarder_suivi_global(patient_sel, modules_valides_db, notes_seance_db)
                                    st.session_state.last_active_module = code_mod
                                    st.success("Sauvegardé")
                                    time.sleep(0.2)
                                    st.rerun()

                        with t_doc:
                             if data.get('pdfs_module'):
                                for p in data['pdfs_module']:
                                    if os.path.exists(p):
                                        with open(p, "rb") as f:
                                            st.download_button(f"📥 {os.path.basename(p)}", f, file_name=os.path.basename(p))

                with col_btn:
                    if code_mod in progression_patient:
                        if st.button("🔓", key=f"lk_{patient_sel}_{code_mod}", help="Bloquer"):
                            progression_patient.remove(code_mod)
                            sauvegarder_progression(patient_sel, progression_patient)
                            st.session_state[cache_key]["progression"] = progression_patient
                            st.rerun()
                    else:
                        if st.button("🔒", key=f"ulk_{patient_sel}_{code_mod}", type="primary", help="Débloquer"):
                            progression_patient.append(code_mod)
                            sauvegarder_progression(patient_sel, progression_patient)
                            st.session_state[cache_key]["progression"] = progression_patient
                            st.rerun()

    # =================================================
    # ONGLET 4 : GESTION EXERCICES
    # =================================================
    with tab_exos:
        patient_sel = st.session_state.patient_selectionne
        if not patient_sel:
            st.info("Veuillez sélectionner un patient d'abord.")
        else:
            st.header(f"📝 Communication & Exercices : {patient_sel}")

            # --- 1. DÉBLOCAGE DES OUTILS ---
            outils_autorises = charger_outils_autorises(patient_sel)
            MAP_OUTILS = {
                "🌙 Agenda Sommeil": "sommeil", "📝 Registre Activités": "activites",
                "🍷 Agenda Consos": "conso", "🛑 Agenda Compulsions": "compulsions",
                "🧩 Colonnes de Beck": "beck", "🔍 Analyse SORC": "sorc",
                "💡 Résolution Problème": "problemes", "⚖️ Balance Décisionnelle": "balance",
                "🧗 Exposition": "expo", "🧘 Relaxation": "relax",
                "📊 PHQ-9": "phq9", "📊 GAD-7": "gad7", "📊 ISI": "isi",
                "📊 PEG": "peg", "📊 WHO-5": "who5", "📊 WSAS": "wsas"
            }
            
            with st.expander("🛠️ Gérer les accès aux Outils & Échelles", expanded=False):
                INV_MAP = {v: k for k, v in MAP_OUTILS.items()}
                default_options = [INV_MAP[k] for k in outils_autorises if k in INV_MAP]
                choix_ouverts = st.multiselect("Outils accessibles pour ce patient :", options=list(MAP_OUTILS.keys()), default=default_options)
                if st.button("💾 Enregistrer les accès outils"):
                    nouvelle_liste_cles = [MAP_OUTILS[nom] for nom in choix_ouverts]
                    sauvegarder_outils_autorises(patient_sel, nouvelle_liste_cles)
                    st.success("Accès outils mis à jour !")
                    time.sleep(0.5)
                    st.rerun()

            st.divider()
            
            c_msg, c_assign = st.columns(2)
            
            with c_msg:
                st.subheader("Envoyer un message")
                st.caption("Le patient verra ce message sur son tableau de bord.")
                msg_content = st.text_area("Votre message :", height=150, placeholder="Bonjour, n'oubliez pas de remplir votre agenda sommeil cette semaine...")
                if st.button("📨 Envoyer le message"):
                    st.toast("Message envoyé (Simulation)", icon="📨")
            
            with c_assign:
                st.subheader("Exercices à faire")
                st.caption("Cochez les exercices prioritaires pour la semaine :")
                exos_dispos = ["Agenda Sommeil", "Colonne de Beck", "Exposition (Hiérarchie)", "Relaxation Audio 1"]
                with st.form("form_assign_exos"):
                    for exo in exos_dispos:
                        st.checkbox(exo)
                    if st.form_submit_button("Mettre à jour les tâches"):
                        st.success("Tâches mises à jour (Simulation)")

    # =================================================
    # ONGLET 5 : VISUALISATION
    # =================================================
    with tab_visu:
        patient_sel = st.session_state.patient_selectionne
        if not patient_sel:
            st.info("Veuillez sélectionner un patient.")
        else:
            st.header(f"📊 Données cliniques : {patient_sel}")
            outils_actuels = charger_outils_autorises(patient_sel)
            
            def T(titre, cle): return f"{titre} 🔒" if cle not in outils_actuels else titre

            options = [
                "Choisir...",
                T("📝 Activités & Humeur", "activites"), T("🌙 Sommeil", "sommeil"), 
                T("🍷 Consommations", "conso"), T("🛑 Compulsions", "compulsions"),
                T("📉 PHQ-9", "phq9"), T("😰 GAD-7", "gad7"), T("🌿 WHO-5", "who5"),
                T("😴 ISI", "isi"), T("🤕 PEG", "peg"), T("🧩 WSAS", "wsas"),
                T("💡 Problèmes", "problemes"), T("🧗 Exposition", "expo"), 
                T("⚖️ Balance", "balance"), T("🔍 SORC", "sorc")
            ]
            
            choix_vue = st.selectbox("Outil à analyser :", options)

            if "Activités" in choix_vue:
                df_act = charger_donnees_specifiques("Activites", patient_sel)
                df_hum = charger_donnees_specifiques("Humeur", patient_sel)
                afficher_activites(df_act, df_hum, patient_sel)
            elif "Sommeil" in choix_vue:
                afficher_sommeil(charger_donnees_specifiques("Sommeil", patient_sel), patient_sel)
            elif "PHQ-9" in choix_vue:
                afficher_phq9(charger_donnees_specifiques("PHQ9", patient_sel), patient_sel)
            elif "GAD-7" in choix_vue:
                afficher_gad7(charger_donnees_specifiques("GAD7", patient_sel), patient_sel)
            elif "ISI" in choix_vue:
                afficher_isi(charger_donnees_specifiques("ISI", patient_sel), patient_sel)
            elif "WHO-5" in choix_vue:
                afficher_who5(charger_donnees_specifiques("WHO5", patient_sel), patient_sel)
            elif "PEG" in choix_vue:
                afficher_peg(charger_donnees_specifiques("PEG", patient_sel), patient_sel)
            elif "WSAS" in choix_vue:
                afficher_wsas(charger_donnees_specifiques("WSAS", patient_sel), patient_sel)
            elif "Problèmes" in choix_vue:
                st.dataframe(charger_donnees_specifiques("Resolution_Probleme", patient_sel), use_container_width=True)
            elif "Expo" in choix_vue:
                st.dataframe(charger_donnees_specifiques("Exposition", patient_sel), use_container_width=True)
            elif "Balance" in choix_vue:
                st.dataframe(charger_donnees_specifiques("Balance_Decisionnelle", patient_sel), use_container_width=True)
            elif "SORC" in choix_vue:
                st.dataframe(charger_donnees_specifiques("SORC", patient_sel), use_container_width=True)

    # =================================================
    # ONGLET 6 : RESSOURCES
    # =================================================
    with tab_res:
        st.header("📚 Ressources Partagées (Cloud)")
        st.info("Les fichiers ajoutés ici sont visibles par TOUS les patients dans l'onglet 'Psychoéducation'.")
        
        from connect_drive import uploader_fichier_drive, lister_fichiers_drive, supprimer_fichier_drive
        
        col_up, col_list = st.columns([1, 2])
        
        with col_up:
            st.subheader("Téléverser")
            uploaded_file = st.file_uploader("Document (PDF/IMG)", type=['pdf', 'png', 'jpg', 'jpeg'])
            if uploaded_file is not None:
                if st.button(f"☁️ Envoyer"):
                    with st.spinner("Envoi..."):
                        if uploader_fichier_drive(uploaded_file, uploaded_file.name):
                            st.success("Envoyé !")
                            time.sleep(1)
                            st.rerun()
        
        with col_list:
            st.subheader("Bibliothèque actuelle")
            fichiers_drive = lister_fichiers_drive()
            if fichiers_drive:
                for f in fichiers_drive:
                    with st.container(border=True):
                        c1, c2 = st.columns([5, 1])
                        c1.text(f"📄 {f['name']}")
                        if c2.button("🗑️", key=f"del_{f['id']}"):
                            supprimer_fichier_drive(f['id'])
                            st.rerun()
            else:
                st.caption("Vide.")