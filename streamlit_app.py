import streamlit as st
import time
from datetime import datetime
import pandas as pd
import json
import os

# Imports DB
from connect_db import (
    verifier_therapeute, verifier_code_patient, recuperer_mes_patients,
    charger_outils_autorises, sauvegarder_outils_autorises, 
    charger_progression, charger_etat_devoirs, charger_suivi_global,
    charger_donnees_specifiques, sauvegarder_progression, 
    load_data, generer_code_securise
)

# Imports Visualisation & Config
from visualisations import (
    afficher_activites, afficher_sommeil, afficher_conso, afficher_compulsions,
    afficher_phq9, afficher_gad7, afficher_isi, afficher_peg, afficher_who5, afficher_wsas
)
from protocole_config import PROTOCOLE_BARLOW

# IMPORT DE LA VUE PATIENT CRÉÉE JUSTE AVANT
from vue_patient import afficher_vue_patient

# CONFIGURATION PAGE
st.set_page_config(page_title="Compagnon TCC", page_icon="🧠", layout="wide")
st.markdown("<style>[data-testid='stSidebarNav'] {display: none;}</style>", unsafe_allow_html=True)

# GESTION SESSION
if "authentifie" not in st.session_state: st.session_state.authentifie = False
if "user_type" not in st.session_state: st.session_state.user_type = None 
if "user_id" not in st.session_state: st.session_state.user_id = "" 

# =========================================================
# 1. ÉCRAN DE CONNEXION
# =========================================================
if not st.session_state.authentifie:
    st.title("🧠 Compagnon TCC")
    t_pat, t_pro = st.tabs(["👤 Accès Patient", "🩺 Accès Thérapeute"])
    
    with t_pat:
        with st.form("login_p"):
            code = st.text_input("Code Patient :", type="password")
            if st.form_submit_button("Entrer"):
                if verifier_code_patient(code):
                    st.session_state.authentifie = True
                    st.session_state.user_type = "patient"
                    st.session_state.user_id = code 
                    st.rerun()
                else: st.error("Code inconnu")
                
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
                    st.rerun()
                else: st.error("Erreur d'identification")
    st.stop()

# =========================================================
# 2. LOGIQUE PATIENT (Vue Centralisée)
# =========================================================
if st.session_state.user_type == "patient":
    afficher_vue_patient(st.session_state.user_id)
    
    with st.sidebar:
        st.write(f"Connecté : {st.session_state.user_id}")
        if st.button("Se déconnecter"):
            st.session_state.authentifie = False
            st.rerun()

# =========================================================
# 3. LOGIQUE THÉRAPEUTE (Code Restauré)
# =========================================================
elif st.session_state.user_type == "therapeute":
    st.title("🩺 Espace Thérapeute")
    
    c1, c2 = st.columns([3, 1])
    with c1: st.write(f"Praticien : **{st.session_state.user_id}**")
    with c2: 
        if st.button("Déconnexion"):
            st.session_state.authentifie = False
            st.rerun()
    st.divider()

    # --- LISTE PATIENTS (CACHE) ---
    if "liste_patients_cache" not in st.session_state:
        df_pats = recuperer_mes_patients(st.session_state.user_id)
        if not df_pats.empty:
            st.session_state.liste_patients_cache = df_pats["Identifiant"].unique().tolist()
        else: st.session_state.liste_patients_cache = []

    # 1. CRÉATION PATIENT
    with st.expander("➕ Nouveau Patient"):
        c_gen1, c_gen2 = st.columns([1, 2])
        with c_gen1: 
            nb_pats = len(st.session_state.liste_patients_cache)
            prochain_id = f"PAT-{nb_pats+1:03d}"
            id_dossier = st.text_input("Dossier", value=prochain_id)
        with c_gen2:
            st.write(" ")
            if st.button("Générer accès"):
                ac_code = generer_code_securise("TCC")
                from connect_db import save_data # Import local si besoin
                save_data("Codes_Patients", [ac_code, st.session_state.user_id, id_dossier, str(datetime.now().date())])
                st.success(f"Créé : {id_dossier} -> Code : {ac_code}")
                # Reset cache
                if "liste_patients_cache" in st.session_state: del st.session_state.liste_patients_cache
                recuperer_mes_patients.clear()
                time.sleep(1)
                st.rerun()

    # 2. SÉLECTION PATIENT
    st.subheader("📂 Dossiers Patients")
    
    if st.session_state.liste_patients_cache:
        patient_sel = st.selectbox("Sélectionner un dossier :", st.session_state.liste_patients_cache)

        if patient_sel:
            st.markdown(f"### 👤 {patient_sel}")
            
            # --- GESTION DES OUTILS ---
            outils_autorises = charger_outils_autorises(patient_sel)
            
            # Définition locale de la Map
            MAP_OUTILS = {
                "🌙 Agenda Sommeil": "sommeil", "📝 Registre Activités": "activites",
                "🍷 Agenda Consos": "conso", "🛑 Agenda Compulsions": "compulsions",
                "🧩 Colonnes de Beck": "beck", "🔍 Analyse SORC": "sorc",
                "💡 Résolution Problème": "problemes", "⚖️ Balance Décisionnelle": "balance",
                "🧗 Exposition": "expo", "🧘 Relaxation": "relax",
                "📊 PHQ-9": "phq9", "📊 GAD-7": "gad7", "📊 ISI": "isi",
                "📊 PEG": "peg", "📊 WHO-5": "who5", "📊 WSAS": "wsas"
            }

            with st.expander("🔒 Débloquer des outils pour le patient"):
                INV_MAP = {v: k for k, v in MAP_OUTILS.items()}
                default_options = [INV_MAP[k] for k in outils_autorises if k in INV_MAP]
                
                choix_ouverts = st.multiselect("Outils accessibles :", options=list(MAP_OUTILS.keys()), default=default_options)
                
                if st.button("💾 Mettre à jour les accès"):
                    nouvelle_liste_cles = [MAP_OUTILS[nom] for nom in choix_ouverts]
                    sauvegarder_outils_autorises(patient_sel, nouvelle_liste_cles)
                    st.success("Accès mis à jour !")
                    time.sleep(0.5)
                    st.rerun()

            st.divider()

# --- PILOTAGE PROTOCOLE (CORRIGÉ) ---
            with st.expander("🗺️ Pilotage du Protocole (Barlow)", expanded=True):
                progression = charger_progression(patient_sel)
                devoirs = charger_etat_devoirs(patient_sel)
                valides, notes = charger_suivi_global(patient_sel)

                # Barre progression
                st.progress(len(valides) / len(PROTOCOLE_BARLOW))

                for code_mod, data in PROTOCOLE_BARLOW.items():
                    # 1. DÉFINITION DE L'ICÔNE DU TITRE (GAUCHE)
                    if code_mod in valides:
                        icon = "✅"  # Fait
                    elif code_mod in progression:
                        icon = "🟦"  # En cours
                    else:
                        icon = "🔒"  # Bloqué
                    
                    # Colonnes : Titre à gauche (90%), Bouton à droite (10%)
                    c_titre, c_lock = st.columns([0.9, 0.1])
                    
                    with c_titre:
                        with st.expander(f"{icon} {data['titre']}"):
                            st.caption(f"📝 Note enregistrée : {notes.get(code_mod, 'Aucune note')}")
                            if data.get('pdfs_module'):
                                for p in data['pdfs_module']:
                                    if os.path.exists(p):
                                        with open(p, "rb") as f:
                                            st.download_button(f"📥 {os.path.basename(p)}", f, file_name=os.path.basename(p), key=f"dl_th_{patient_sel}_{code_mod}_{os.path.basename(p)}")
                    
                    # 2. LOGIQUE DU BOUTON (DROITE) - MODE "INTERRUPTEUR"
                    with c_lock:
                        if code_mod in progression:
                            # CAS : Le module est ACCESSIBLE
                            # On affiche un cadenas OUVERT 🔓 pour montrer l'état actuel.
                            # Cliquer dessus va le BLOQUER.
                            if st.button("🔓", key=f"btn_state_open_{patient_sel}_{code_mod}", help="Actuellement OUVERT. Cliquer pour BLOQUER."):
                                progression.remove(code_mod)
                                sauvegarder_progression(patient_sel, progression)
                                st.rerun()
                        else:
                            # CAS : Le module est BLOQUÉ
                            # On affiche un cadenas FERMÉ 🔒 (en rouge/primaire) pour montrer l'état.
                            # Cliquer dessus va le DÉBLOQUER.
                            if st.button("🔒", key=f"btn_state_lock_{patient_sel}_{code_mod}", type="primary", help="Actuellement VERROUILLÉ. Cliquer pour DÉBLOQUER."):
                                progression.append(code_mod)
                                sauvegarder_progression(patient_sel, progression)
                                st.rerun()

            st.divider()

            # --- VISUALISATION ---
            st.subheader("📊 Visualisation des Données")
            
            def T(titre, cle):
                return f"{titre} 🔒" if cle not in outils_autorises else titre

            liste_choix = [
                "Choisir...",
                T("📝 Activités & Humeur", "activites"), T("🌙 Sommeil", "sommeil"), 
                T("🍷 Consommations", "conso"), T("🛑 Compulsions", "compulsions"),
                T("📉 PHQ-9", "phq9"), T("😰 GAD-7", "gad7"), T("🌿 WHO-5", "who5"),
                T("😴 ISI", "isi"), T("🤕 PEG", "peg"), T("🧩 WSAS", "wsas")
            ]
            
            choix_vue = st.selectbox("Outil à analyser :", liste_choix)

            if "Activités" in choix_vue:
                df_act = charger_donnees_specifiques("Activites", patient_sel)
                df_hum = charger_donnees_specifiques("Humeur", patient_sel)
                afficher_activites(df_act, df_hum, patient_sel)
            
            elif "Sommeil" in choix_vue:
                df = charger_donnees_specifiques("Sommeil", patient_sel)
                afficher_sommeil(df, patient_sel)

            elif "PHQ-9" in choix_vue:
                df = charger_donnees_specifiques("PHQ9", patient_sel)
                afficher_phq9(df, patient_sel)
            
            elif "GAD-7" in choix_vue:
                df = charger_donnees_specifiques("GAD7", patient_sel)
                afficher_gad7(df, patient_sel)

            elif "ISI" in choix_vue:
                df = charger_donnees_specifiques("ISI", patient_sel)
                afficher_isi(df, patient_sel)

            elif "PEG" in choix_vue:
                df = charger_donnees_specifiques("PEG", patient_sel)
                afficher_peg(df, patient_sel)

            elif "WHO-5" in choix_vue:
                df = charger_donnees_specifiques("WHO5", patient_sel)
                afficher_who5(df, patient_sel)

            elif "WSAS" in choix_vue:
                df = charger_donnees_specifiques("WSAS", patient_sel)
                afficher_wsas(df, patient_sel)

            elif "Problèmes" in choix_vue:
                df = charger_donnees_specifiques("Resolution_Probleme", patient_sel)
                if not df.empty: st.dataframe(df, use_container_width=True)
                else: st.info("Aucune donnée.")

            elif "Expo" in choix_vue:
                df = charger_donnees_specifiques("Exposition", patient_sel)
                if not df.empty: st.dataframe(df, use_container_width=True)
                else: st.info("Aucune donnée.")

            elif "Balance" in choix_vue:
                df = charger_donnees_specifiques("Balance_Decisionnelle", patient_sel)
                if not df.empty: st.dataframe(df, use_container_width=True)
                else: st.info("Aucune donnée.")

            elif "SORC" in choix_vue:
                df = charger_donnees_specifiques("SORC", patient_sel)
                if not df.empty: st.dataframe(df, use_container_width=True)
                else: st.info("Aucune donnée.")
    
    else:
        st.warning("Aucun patient trouvé.")