import streamlit as st
import time # Pour les petites pauses d'animation

st.set_page_config(page_title="Mon Compagnon TCC", page_icon="🧠", layout="wide")

# --- GESTION DE SESSION ---
if "authentifie" not in st.session_state:
    st.session_state.authentifie = False
if "patient_id" not in st.session_state:
    st.session_state.patient_id = ""

# =========================================================
# ÉCRAN DE CONNEXION / INSCRIPTION (Si pas connecté)
# =========================================================
if not st.session_state.authentifie:
    st.title("🔒 Espace Patient Sécurisé")
    st.info("""
    ℹ️ **Note de confidentialité :** Cette application est un outil d'accompagnement. 
    Pour garantir votre anonymat, **n'utilisez pas votre nom de famille complet**. 
    Utilisez un prénom ou un pseudonyme convenu avec votre thérapeute.
    Vos données sont strictement réservées à l'usage thérapeutique.
    """)
    st.info("Bienvenue. Connectez-vous ou créez votre espace personnel pour commencer.")

    # On crée deux onglets pour séparer les actions
    tab_login, tab_signup = st.tabs(["🔑 Se connecter", "📝 Créer un compte"])

    # --- ONGLET 1 : CONNEXION ---
    with tab_login:
        with st.form("login_form"):
            user_login = st.text_input("Votre Identifiant")
            pass_login = st.text_input("Votre Mot de passe", type="password")
            submit_login = st.form_submit_button("Me connecter")
        
        if submit_login:
            from connect_db import charger_utilisateurs
            users_db = charger_utilisateurs() # Récupère la liste depuis Google Sheets
            
            # Vérification (Est-ce que le couple User/Pass existe ?)
            compte_trouve = False
            for u in users_db:
                # On compare ce qui est écrit avec ce qui est dans le fichier Excel
                # (On utilise str() pour être sûr de comparer du texte)
                if str(u["Identifiant"]) == user_login and str(u["MotDePasse"]) == pass_login:
                    compte_trouve = True
                    break
            
            if compte_trouve:
                st.success("Connexion réussie !")
                st.session_state.authentifie = True
                st.session_state.patient_id = user_login
                time.sleep(1) # Petite pause pour voir le message
                st.rerun()    # On recharge la page pour entrer
            else:
                st.error("Identifiant ou mot de passe incorrect.")

    # --- ONGLET 2 : INSCRIPTION ---
    with tab_signup:
        st.write("C'est votre première fois ? Créez un identifiant unique.")
        with st.form("signup_form"):
            new_user = st.text_input("Choisissez un Identifiant")
            new_pass = st.text_input("Choisissez un Mot de passe", type="password")
            submit_signup = st.form_submit_button("Créer mon compte")
        
        if submit_signup:
            if new_user and new_pass:
                from connect_db import charger_utilisateurs, creer_compte
                
                # 1. On vérifie si le pseudo est déjà pris
                users_db = charger_utilisateurs()
                pseudo_pris = False
                for u in users_db:
                    if str(u["Identifiant"]) == new_user:
                        pseudo_pris = True
                        break
                
                if pseudo_pris:
                    st.warning("Cet identifiant existe déjà. Choisissez-en un autre.")
                else:
                    # 2. On crée le compte
                    if creer_compte(new_user, new_pass):
                        st.success("Compte créé avec succès ! Allez dans l'onglet 'Se connecter'.")
                        st.balloons()
            else:
                st.warning("Veuillez remplir tous les champs.")

    # On arrête le script ici tant qu'on n'est pas connecté
    st.stop()


# =========================================================
# APPLICATION PRINCIPALE (Visible seulement après connexion)
# =========================================================

st.title(f"🧠 Bienvenue, {st.session_state.patient_id}")
st.subheader("Tableau de bord personnel")
st.divider()

# --- LIGNE 1 ---
col1, col2 = st.columns(2)
with col1:
    st.info("### 🧩 Restructuration")
    st.write("Beck & Pensées alternatives")
    st.page_link("pages/01_Colonnes_Beck.py", label="Lancer", icon="➡️")
with col2:
    st.info("### 📊 Échelles (BDI)")
    st.write("Auto-évaluation de l'humeur")
    st.page_link("pages/02_Echelles_BDI.py", label="Tester", icon="➡️")

st.divider()

# --- LIGNE 2 ---
col3, col4 = st.columns(2)
with col3:
    st.warning("### 📝 Registre Activités")
    st.write("Quotidien & Plaisir")
    st.page_link("pages/05_Registre_Activites.py", label="Ouvrir", icon="➡️")
with col4:
    st.error("### 💡 Résolution Problèmes")
    st.write("Trouver des solutions")
    st.page_link("pages/06_Resolution_Probleme.py", label="Lancer", icon="➡️")

st.divider()

# --- LIGNE 3 ---
c5, c6 = st.columns(2)
with c5:
    st.success("### 🧘 Relaxation")
    st.write("Respiration & Détente")
    st.page_link("pages/07_Relaxation.py", label="Se détendre", icon="➡️")
with c6:
    st.success("### 📜 Historique")
    st.write("Voir mes progrès")
    st.page_link("pages/04_Historique.py", label="Consulter", icon="📅")

st.divider()

with st.expander("📚 Bibliothèque de Fiches & Ressources"):
    st.write("Accédez aux documents de référence.")
    st.page_link("pages/03_Ressources.py", label="Ouvrir la bibliothèque", icon="📚")

# --- SIDEBAR ---
with st.sidebar:
    st.write(f"Utilisateur : **{st.session_state.patient_id}**")
    if st.button("Se déconnecter"):
        st.session_state.authentifie = False
        st.session_state.patient_id = ""
        st.rerun()
    st.divider()
    st.title("Navigation")
    st.page_link("streamlit_app.py", label="🏠 Accueil")
    st.page_link("pages/01_Colonnes_Beck.py", label="🧩 Beck")
    st.page_link("pages/02_Echelles_BDI.py", label="📊 BDI")
    st.page_link("pages/05_Registre_Activites.py", label="📝 Activités")
    st.page_link("pages/06_Resolution_Probleme.py", label="💡 Problèmes")
    st.page_link("pages/07_Relaxation.py", label="🧘 Relaxation")
    st.page_link("pages/04_Historique.py", label="📜 Historique")