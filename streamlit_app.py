import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="TCC Companion", page_icon="🧠")

st.title("🧠 Compagnon TCC")
st.write("Bienvenue dans votre espace de travail thérapeutique.")

# =========================================================
# GESTION DE L'AUTHENTIFICATION (LISTE BLANCHE)
# =========================================================

# 1. Initialisation des variables de session
if "authentifie" not in st.session_state:
    st.session_state.authentifie = False
if "patient_id" not in st.session_state:
    st.session_state.patient_id = ""

# 2. Fonction pour récupérer les codes autorisés (Mise en cache pour la rapidité)
@st.cache_data(ttl=600) # Le cache se rafraîchit toutes les 10 min
def get_valid_codes():
    try:
        from connect_db import load_data
        data = load_data("Codes_Patients") # On lit l'onglet 'Codes_Patients'
        if data:
            df = pd.DataFrame(data)
            # On récupère la colonne 'Code' et on convertit tout en majuscules pour éviter les erreurs
            if "Code" in df.columns:
                return df["Code"].astype(str).str.upper().str.strip().tolist()
            elif "code" in df.columns: # Si écrit en minuscule dans Excel
                return df["code"].astype(str).str.upper().str.strip().tolist()
    except Exception as e:
        st.error(f"Erreur de connexion à la base de sécurité : {e}")
    return []

# 3. Interface de connexion
if not st.session_state.authentifie:
    
    st.info("🔒 Accès sécurisé : Veuillez entrer le code fourni par votre thérapeute.")
    
    with st.form("login_form"):
        code_input = st.text_input("Code d'accès", placeholder="Ex: A123", type="password")
        submit_btn = st.form_submit_button("Se connecter")
        
        if submit_btn:
            # Nettoyage de l'entrée utilisateur
            code_clean = code_input.strip().upper()
            
            # Récupération de la liste blanche
            codes_autorises = get_valid_codes()
            
            # --- VÉRIFICATION ---
            if code_clean in codes_autorises:
                # SUCCÈS
                st.session_state.patient_id = code_clean
                st.session_state.authentifie = True
                st.success(f"Code reconnu. Bienvenue !")
                time.sleep(1)
                st.rerun()
            elif not codes_autorises:
                # CAS D'URGENCE : Si la liste est vide ou connexion impossible
                st.error("⚠️ Impossible de vérifier les codes (Erreur serveur ou liste vide).")
            else:
                # ÉCHEC
                st.error("❌ Code non reconnu ou invalide. Contactez votre thérapeute.")

# 3. Affichage du menu une fois connecté
else:
    st.success(f"✅ Connecté (Code : {st.session_state.patient_id})")
    
    # Bouton de déconnexion
    if st.button("Se déconnecter / Changer de code"):
        st.session_state.authentifie = False
        st.session_state.patient_id = ""
        st.rerun()
    
    st.divider()
    st.subheader("Vos outils disponibles :")
    
    # Liens vers les autres pages
    col1, col2 = st.columns(2)
    with col1:
        st.page_link("pages/10_Registre_Activites.py", label="📝 Registre des Activités", icon="📝")
        st.page_link("pages/11_Agenda_Consos.py", label="🍷 Agenda Consos", icon="🍷")
    with col2:
        st.page_link("pages/12_Colonnes_Beck.py", label="🧩 Colonnes de Beck", icon="🧩")
        st.page_link("pages/13_Resolution_Problemes.py", label="💡 Résolution Problèmes", icon="💡")

# --- ACCUEIL (TABLEAU DE BORD COMPLET) ---
st.title(f"🧠 Bonjour {st.session_state.patient_id}")
st.subheader("Tableau de bord personnel")
st.divider()

# --- LIGNE 1 : COGNITIF & ANALYSE ---
c1, c2, c3 = st.columns(3)

with c1:
    st.info("### 🧩 Restructuration cognitive")
    st.write("Colonnes de Beck")
    st.page_link("pages/01_Colonnes_Beck.py", label="Lancer", icon="➡️")

with c2:
    st.info("### 📊 Échelles (BDI)")
    st.write("Suivi de l'humeur")
    st.page_link("pages/02_Echelles_BDI.py", label="Tester", icon="➡️")

with c3:
    st.info("### ⚖️ Balance décisonnelle")
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
    st.error("### 💡 Résolution de problèmes")
    st.write("Trouver des solutions")
    st.page_link("pages/06_Resolution_Probleme.py", label="Lancer", icon="➡️")

with c6:
    st.error("### 🧗 Protocole d'exposition")
    st.write("Affronter ses peurs")
    st.page_link("pages/09_Exposition.py", label="Planifier", icon="➡️")

st.divider()

# --- LIGNE 3 : PHYSIOLOGIE & BIEN-ÊTRE ---
c7, c8, c9 = st.columns(3)

with c7:
    # --- CORRECTION ICI (st.info au lieu de st.primary) ---
    st.warning("### 🌙 Agenda du sommeil")
    st.write("Agenda du sommeil")
    st.page_link("pages/10_Agenda_Sommeil.py", label="Noter", icon="➡️")

with c8:
    st.warning("### 📝 Agenda des activités")
    st.write("Registre Plaisir/Maîtrise")
    st.page_link("pages/05_Registre_Activites.py", label="Ouvrir", icon="➡️")

with c9:
    st.warning("### 🍷 Agenda de consommation") 
    st.write("Envies & Substances")
    # Vérifiez que le fichier 13_Agenda_Consos.py existe bien
    st.page_link("pages/13_Agenda_Consos.py", label="Ouvrir", icon="➡️") 

st.divider()

# --- LIGNE 4 : SUIVI & RESSOURCES ---
c10, c11, c12 = st.columns(3)

with c10:
    st.success("### 📜 Historique")
    st.write("Mes progrès")
    st.page_link("pages/04_Historique.py", label="Consulter", icon="📅")

with c11:
    st.success("### 📩 Export PDF")
    st.write("Envoyer rapport")
    st.page_link("pages/08_Export_Rapport.py", label="Générer", icon="📤")

with c12:
    st.success("### 📚 Ressources")
    st.write("Fiches pratiques")
    st.page_link("pages/03_Ressources.py", label="Lire", icon="📚")


# --- SIDEBAR (MENU COMPLET) ---
with st.sidebar:
    st.write(f"👤 **{st.session_state.patient_id}**")
    if st.button("Se déconnecter"):
        st.session_state.authentifie = False
        st.rerun()
    st.divider()
    st.title("Navigation")
    st.page_link("streamlit_app.py", label="🏠 Accueil")
    st.page_link("pages/01_Colonnes_Beck.py", label="🧩 Tableau de Beck")
    st.page_link("pages/02_Echelles_BDI.py", label="📊 BDI")
    st.page_link("pages/11_Balance_Decisionnelle.py", label="⚖️ Balance décisionnelle")
    st.page_link("pages/07_Relaxation.py", label="🧘 Relaxation")
    st.page_link("pages/06_Resolution_Probleme.py", label="💡 Résolution de problèmes")
    st.page_link("pages/09_Exposition.py", label="🧗 Protocole d'exposition")
    st.page_link("pages/10_Agenda_Sommeil.py", label="🌙 Agenda du sommeil")
    st.page_link("pages/05_Registre_Activites.py", label="📝 Agenda des activités")
    st.page_link("pages/13_Agenda_Consos.py", label="🍷 Agenda de consommation")
    st.page_link("pages/03_Ressources.py", label="📚 Ressources")
    st.page_link("pages/04_Historique.py", label="📜 Historique")
    st.page_link("pages/08_Export_Rapport.py", label="📩 Export PDF")
