import streamlit as st

st.set_page_config(page_title="Mon Compagnon TCC", page_icon="🧠", layout="wide")

# --- AUTHENTIFICATION ---
if "authentifie" not in st.session_state:
    st.session_state.authentifie = False
if "patient_id" not in st.session_state:
    st.session_state.patient_id = ""

def verifier_connexion():
    if st.session_state.password_input == "TCC2025" and st.session_state.user_input.strip() != "":
        st.session_state.authentifie = True
        st.session_state.patient_id = st.session_state.user_input
    elif st.session_state.password_input != "TCC2025":
        st.error("Mot de passe incorrect")
    else:
        st.warning("Veuillez entrer votre Prénom.")

if not st.session_state.authentifie:
    st.title("🔒 Espace Patient Sécurisé")
    st.info("""
    ℹ️ **Note de confidentialité :** Cette application est un outil d'accompagnement. 
    Pour garantir votre anonymat, **n'utilisez pas votre nom de famille complet**. 
    Utilisez un prénom ou un pseudonyme convenu avec votre thérapeute.
    """)
    
    # Onglets Connexion / Inscription
    tab_login, tab_signup = st.tabs(["🔑 Se connecter", "📝 Créer un compte"])

    with tab_login:
        with st.form("login_form"):
            user_login = st.text_input("Votre Identifiant")
            pass_login = st.text_input("Votre Mot de passe", type="password")
            submit_login = st.form_submit_button("Me connecter")
        
        if submit_login:
            from connect_db import charger_utilisateurs
            users_db = charger_utilisateurs()
            compte_trouve = False
            for u in users_db:
                if str(u["Identifiant"]) == user_login and str(u["MotDePasse"]) == pass_login:
                    compte_trouve = True
                    break
            if compte_trouve:
                st.success("Connexion réussie !")
                st.session_state.authentifie = True
                st.session_state.patient_id = user_login
                st.rerun()
            else:
                st.error("Identifiant ou mot de passe incorrect.")

    with tab_signup:
        st.write("Première fois ? Créez un compte.")
        with st.form("signup_form"):
            new_user = st.text_input("Choisissez un Identifiant")
            new_pass = st.text_input("Choisissez un Mot de passe", type="password")
            submit_signup = st.form_submit_button("Créer mon compte")
        
        if submit_signup:
            if new_user and new_pass:
                from connect_db import charger_utilisateurs, creer_compte
                users_db = charger_utilisateurs()
                pseudo_pris = False
                for u in users_db:
                    if str(u["Identifiant"]) == new_user:
                        pseudo_pris = True
                        break
                if pseudo_pris:
                    st.warning("Cet identifiant existe déjà.")
                else:
                    if creer_compte(new_user, new_pass):
                        st.success("Compte créé ! Allez dans l'onglet 'Se connecter'.")
                        st.balloons()
            else:
                st.warning("Remplissez tous les champs.")
    st.stop()

# --- ACCUEIL (TABLEAU DE BORD COMPLET) ---
st.title(f"🧠 Bonjour {st.session_state.patient_id}")
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
    st.info("### ⚖️ Balance décisonnelle")
    st.write("Pour & Contre")
    st.page_link("pages/11_Balance_Decisionnelle.py", label="Peser", icon="➡️")

st.divider()

# --- LIGNE 2 : ACTION & PROBLÈMES ---
c4, c5, c6 = st.columns(3)

with c4:
    st.success("### 🧘 Relaxation")
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
    st.info("### 🌙 Agenda du sommeil")
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
    st.page_link("pages/11_Balance_Decisionnelle.py", label="⚖️ Balance décisionnelle")
    st.page_link("pages/06_Resolution_Probleme.py", label="💡 Résolution de problèmes")
    st.page_link("pages/05_Registre_Activites.py", label="📝 Agenda des activités")
    st.page_link("pages/10_Agenda_Sommeil.py", label="🌙 Agenda du sommeil")
    st.page_link("pages/13_Agenda_Consos.py", label="🍷 Agenda de consommation")
    st.page_link("pages/02_Echelles_BDI.py", label="📊 BDI")
    st.page_link("pages/07_Relaxation.py", label="🧘 Relaxation")
    st.page_link("pages/09_Exposition.py", label="🧗 Exposition")
    st.page_link("pages/03_Ressources.py", label="📚 Ressources")
    st.page_link("pages/04_Historique.py", label="📜 Historique")
    st.page_link("pages/08_Export_Rapport.py", label="📩 Export PDF")
 