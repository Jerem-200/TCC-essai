import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="TCC Companion", page_icon="🧠", layout="wide")

# =========================================================
# GESTION DE L'AUTHENTIFICATION (LISTE BLANCHE)
# =========================================================

if "authentifie" not in st.session_state:
    st.session_state.authentifie = False
if "patient_id" not in st.session_state:
    st.session_state.patient_id = ""

@st.cache_data(ttl=600)
def get_valid_codes():
    try:
        from connect_db import load_data
        data = load_data("Codes_Patients")
        if data:
            df = pd.DataFrame(data)
            if "Code" in df.columns:
                return df["Code"].astype(str).str.upper().str.strip().tolist()
            elif "code" in df.columns:
                return df["code"].astype(str).str.upper().str.strip().tolist()
    except Exception as e:
        # En dev, on peut afficher l'erreur, en prod on reste discret
        print(f"Erreur DB: {e}")
    return []

# --- CAS 1 : NON CONNECTÉ ---
if not st.session_state.authentifie:
    st.title("🧠 Compagnon TCC")
    st.write("Bienvenue dans votre espace de travail thérapeutique.")
    st.info("🔒 Accès sécurisé : Veuillez entrer le code fourni par votre thérapeute.")
    
    with st.form("login_form"):
        code_input = st.text_input("Code d'accès", placeholder="Ex: A123", type="password")
        submit_btn = st.form_submit_button("Se connecter")
        
        if submit_btn:
            code_clean = code_input.strip().upper()
            codes_autorises = get_valid_codes()
            
            # --- BACKDOOR POUR TESTER SANS BASE DE DONNÉES (Optionnel) ---
            # Enlevez cette ligne 'if' en production si vous voulez être strict
            if code_clean == "DEMO": codes_autorises = ["DEMO"]
            # -------------------------------------------------------------

            if code_clean in codes_autorises:
                st.session_state.patient_id = code_clean
                st.session_state.authentifie = True
                st.success(f"Code reconnu. Bienvenue !")
                time.sleep(1)
                st.rerun()
            elif not codes_autorises:
                st.error("⚠️ Erreur de connexion au serveur (Liste vide).")
            else:
                st.error("❌ Code non reconnu.")

# --- CAS 2 : CONNECTÉ (TABLEAU DE BORD) ---
else:
    # Tout le contenu du tableau de bord doit être INDENTÉ ici
    
    # En-tête avec bouton déconnexion
    c_titre, c_logout = st.columns([4, 1])
    with c_titre:
        st.title(f"🧠 Bonjour {st.session_state.patient_id}")
    with c_logout:
        if st.button("Se déconnecter"):
            st.session_state.authentifie = False
            st.session_state.patient_id = ""
            st.rerun()

    st.subheader("Tableau de bord personnel")
    st.divider()

    # --- LIGNE 1 : COGNITIF & ANALYSE ---
    c1, c2, c3 = st.columns(3)
    with c1:
        st.info("### 🧩 Restructuration")
        st.write("Colonnes de Beck")
        st.page_link("pages/01_Colonnes_Beck.py", label="Lancer", icon="➡️")
    with c2:
        st.info("### 📊 Échelles (BDI)")
        st.write("Suivi de l'humeur")
        st.page_link("pages/02_Echelles_BDI.py", label="Tester", icon="➡️")
    with c3:
        st.info("### ⚖️ Balance décisionnelle")
        st.write("Pour & Contre")
        st.page_link("pages/11_Balance_Decisionnelle.py", label="Peser", icon="➡️")

    st.divider()

    # --- LIGNE 2 : ACTION & PROBLÈMES ---
    c4, c5, c6 = st.columns(3)
    with c4:
        st.error("### 🧘 Relaxation")
        st.write("Respiration & Détente")
        st.page_link("pages/07_Relaxation.py", label="Lancer", icon="➡️")
    with c5:
        st.error("### 💡 Résolution de problème")
        st.write("Trouver des solutions")
        # Attention au nom exact du fichier (singulier ou pluriel ?)
        st.page_link("pages/06_Resolution_Probleme.py", label="Lancer", icon="➡️")
    with c6:
        st.error("### 🧗 Exposition")
        st.write("Affronter ses peurs")
        st.page_link("pages/09_Exposition.py", label="Planifier", icon="➡️")

    st.divider()

    # --- LIGNE 3 : PHYSIOLOGIE & BIEN-ÊTRE ---
    c7, c8, c9 = st.columns(3)
    with c7:
        st.warning("### 🌙 Agenda du sommeil")
        st.write("Agenda du sommeil")
        st.page_link("pages/10_Agenda_Sommeil.py", label="Noter", icon="➡️")
    with c8:
        st.warning("### 📝 Agenda des activités")
        st.write("Plaisir & Maîtrise")
        # J'ai mis 05 ici car c'est ce que vous aviez dans la grille
        st.page_link("pages/05_Registre_Activites.py", label="Ouvrir", icon="➡️")
    with c9:
        st.warning("### 🍷 Agenda de consommation") 
        st.write("Envies & Substances")
        # J'ai mis 13 ici, vérifiez si c'est 11 ou 13 dans votre dossier
        st.page_link("pages/13_Agenda_Consos.py", label="Ouvrir", icon="➡️") 

    st.divider()

    # --- LIGNE 4 : SUIVI & RESSOURCES ---
    c10, c11, c12 = st.columns(3)
    with c10:
        st.success("### 📜 Historique")
        st.write("Mes progrès")
        st.page_link("pages/04_Historique.py", label="Consulter", icon="📅")
    with c11:
        st.success("### 📩 Export")
        st.write("Envoyer rapport")
        st.page_link("pages/08_Export_Rapport.py", label="Générer", icon="📤")
    with c12:
        st.success("### 📚 Ressources")
        st.write("Fiches pratiques")
        st.page_link("pages/03_Ressources.py", label="Lire", icon="📚")

    # --- SIDEBAR (MENU LATÉRAL) ---
    with st.sidebar:
        st.write(f"👤 ID: **{st.session_state.patient_id}**")
        st.divider()
        st.title("Navigation")
        st.page_link("streamlit_app.py", label="🏠 Accueil")
        # Vérifiez que ces liens correspondent bien à vos fichiers existants
        st.page_link("pages/01_Colonnes_Beck.py", label="🧩 Tableau de Beck")
        st.page_link("pages/02_Echelles_BDI.py", label="📊 BDI")
        st.page_link("pages/05_Registre_Activites.py", label="📝 Agenda des activités")
        st.page_link("pages/06_Resolution_Probleme.py", label="💡 Résolution Problèmes")
        st.page_link("pages/07_Relaxation.py", label="🧘 Relaxation")
        st.page_link("pages/09_Exposition.py", label="🧗 Exposition")
        st.page_link("pages/10_Agenda_Sommeil.py", label="🌙 Sommeil")
        st.page_link("pages/11_Balance_Decisionnelle.py", label="⚖️ Balance")
        st.page_link("pages/13_Agenda_Consos.py", label="🍷 Consommation")
        st.page_link("pages/03_Ressources.py", label="📚 Ressources")