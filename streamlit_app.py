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
    
    # Disclaimer confidentialité
    st.info("""
    ℹ️ **Note de confidentialité :** Cette application est un outil d'accompagnement. 
    Pour garantir votre anonymat, **n'utilisez pas votre nom de famille complet**. 
    Utilisez un prénom ou un pseudonyme convenu avec votre thérapeute.
    Vos données sont strictement réservées à l'usage thérapeutique.
    """)
    
    st.write("Bienvenue. Connectez-vous ou créez votre espace personnel pour commencer.")

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
            
            # Vérification
            compte_trouve = False
            for u in users_db:
                if str(u["Identifiant"]) == user_login and str(u["MotDePasse"]) == pass_login:
                    compte_trouve = True
                    break
            
            if compte_trouve:
                st.success("Connexion réussie !")
                st.session_state.authentifie = True
                st.session_state.patient_id = user_login
                time.sleep(1)
                st.rerun()
            else:
                st.error("Identifiant ou mot de passe incorrect.")
                
        # --- BOUTON MOT DE PASSE OUBLIÉ ---
        st.write("---")
        with st.expander("S.O.S - Mot de passe oublié ?"):
            st.write("Pour des raisons de sécurité, la réinitialisation se fait via votre thérapeute.")
            # Remplacez par VOTRE email professionnel ici
            email_therapeute = "email_pro_exemple@gmail.com" 
            sujet = "Demande réinitialisation mot de passe TCC"
            corps = "Bonjour, j'ai oublié mon mot de passe. Mon identifiant est : ..."
            lien_mail = f"mailto:{email_therapeute}?subject={sujet}&body={corps}"
            
            st.markdown(f"""<a href="{lien_mail}" target="_blank"><button style="background-color:#f0f2f6;border:1px solid #d0d7de;padding:10px;border-radius:5px;cursor:pointer;color:#31333F;">📧 Envoyer une demande</button></a>""", unsafe_allow_html=True)

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
                # Vérif doublon
                users_db = charger_utilisateurs()
                pseudo_pris = False
                for u in users_db:
                    if str(u["Identifiant"]) == new_user:
                        pseudo_pris = True
                        break
                
                if pseudo_pris:
                    st.warning("Cet identifiant existe déjà. Choisissez-en un autre.")
                else:
                    if creer_compte(new_user, new_pass):
                        st.success("Compte créé avec succès ! Allez dans l'onglet 'Se connecter'.")
                        st.balloons()
            else:
                st.warning("Veuillez remplir tous les champs.")

    st.stop()


# =========================================================
# APPLICATION PRINCIPALE (Visible seulement après connexion)
# =========================================================

st.title(f"🧠 Bienvenue, {st.session_state.patient_id}")
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
    st.info("### ⚖️ Balance")
    st.write("Pour & Contre")
    st.page_link("pages/11_Balance_Decisionnelle.py", label="Peser", icon="➡️")

st.divider()

# --- LIGNE 2 : ACTION & PROBLÈMES ---
c4, c5, c6 = st.columns(3)

with c4:
    st.warning("### 📝 Activités")
    st.write("Registre Plaisir/Maîtrise")
    st.page_link("pages/05_Registre_Activites.py", label="Ouvrir", icon="➡️")

with c5:
    st.error("### 💡 Résolution Pb")
    st.write("Trouver des solutions")
    st.page_link("pages/06_Resolution_Probleme.py", label="Lancer", icon="➡️")

with c6:
    st.error("### 🧗 Exposition")
    st.write("Affronter ses peurs")
    st.page_link("pages/09_Exposition.py", label="Planifier", icon="➡️")

st.divider()

# --- LIGNE 3 : PHYSIOLOGIE & BIEN-ÊTRE ---
c7, c8, c9 = st.columns(3)

with c7:
    st.primary("### 🌙 Sommeil")
    st.write("Agenda du sommeil")
    st.page_link("pages/10_Agenda_Sommeil.py", label="Noter", icon="➡️")

with c8:
    st.success("### 🧘 Relaxation")
    st.write("Respiration & Détente")
    st.page_link("pages/07_Relaxation.py", label="Lancer", icon="➡️")

with c9:
    # Si vous avez gardé l'agenda conso (addictions), c'est ici, sinon on laisse vide ou on met historique
    st.warning("### 🍷 Agenda Conso") 
    st.write("Envies & Substances")
    # Vérifiez que le fichier 13_Agenda_Consos.py existe bien, sinon supprimez ce bloc
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
    st.page_link("pages/01_Colonnes_Beck.py", label="🧩 Beck")
    st.page_link("pages/02_Echelles_BDI.py", label="📊 BDI")
    st.page_link("pages/11_Balance_Decisionnelle.py", label="⚖️ Balance")
    st.page_link("pages/06_Resolution_Probleme.py", label="💡 Problèmes")
    st.page_link("pages/05_Registre_Activites.py", label="📝 Activités")
    st.page_link("pages/09_Exposition.py", label="🧗 Exposition")
    st.page_link("pages/10_Agenda_Sommeil.py", label="🌙 Sommeil")
    st.page_link("pages/13_Agenda_Consos.py", label="🍷 Consos")
    st.page_link("pages/07_Relaxation.py", label="🧘 Relaxation")
    st.page_link("pages/03_Ressources.py", label="📚 Ressources")
    st.page_link("pages/04_Historique.py", label="📜 Historique")
    st.page_link("pages/08_Export_Rapport.py", label="📩 Export PDF")
