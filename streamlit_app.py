import streamlit as st
import pandas as pd
import time
import secrets
import string
from datetime import datetime

st.set_page_config(page_title="Compagnon TCC", page_icon="🧠", layout="wide")

# =========================================================
# 0. SÉCURITÉ & UTILITAIRES
# =========================================================

def generer_code_securise(prefix="PAT", length=6):
    """Génère un code aléatoire sécurisé (ex: PAT-X9J2M)"""
    # On évite I, 1, O, 0 pour éviter les confusions de lecture
    chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789" 
    suffix = ''.join(secrets.choice(chars) for _ in range(length))
    return f"{prefix}-{suffix}"

# --- INITIALISATION DE LA SESSION ---
if "authentifie" not in st.session_state:
    st.session_state.authentifie = False
if "user_type" not in st.session_state:
    st.session_state.user_type = None # "patient" ou "therapeute"
if "user_id" not in st.session_state:
    st.session_state.user_id = "" 

# =========================================================
# 1. FONCTIONS DE BASE DE DONNÉES
# =========================================================

@st.cache_data(ttl=60)
def verifier_therapeute(identifiant, mot_de_passe):
    """Vérifie les accès dans l'onglet 'Therapeutes'"""
    try:
        from connect_db import load_data
        data = load_data("Therapeutes")
        if data:
            df = pd.DataFrame(data)
            
            # --- BLINDAGE : Nettoyage des espaces et conversion en texte ---
            # On s'assure que les colonnes sont bien lues comme du texte
            df["Identifiant"] = df["Identifiant"].astype(str).str.strip()
            df["MotDePasse"] = df["MotDePasse"].astype(str).str.strip()
            
            user_clean = str(identifiant).strip()
            pwd_clean = str(mot_de_passe).strip()

            # Recherche de la ligne correspondante
            user_row = df[(df["Identifiant"] == user_clean) & (df["MotDePasse"] == pwd_clean)]
            
            if not user_row.empty:
                # On retourne la colonne 'ID' (ex: TH-01)
                return user_row.iloc[0]["ID"] 
    except Exception as e:
        st.error(f"Erreur connexion Thérapeute : {e}")
    return None

@st.cache_data(ttl=60)
def verifier_code_patient(code):
    """Vérifie si le code existe dans 'Codes_Patients'"""
    try:
        from connect_db import load_data
        data = load_data("Codes_Patients")
        if data:
            df = pd.DataFrame(data)
            if "Code" in df.columns:
                # Vérification insensible à la casse (majuscule/minuscule)
                if code.upper() in df["Code"].astype(str).str.upper().values:
                    return True
    except Exception as e:
        st.error(f"Erreur connexion Patient : {e}")
    return False

def recuperer_mes_patients(therapeute_id):
    """Récupère la liste des patients liés à ce thérapeute"""
    try:
        from connect_db import load_data
        data = load_data("Codes_Patients")
        if data:
            df = pd.DataFrame(data)
            # On filtre pour ne garder que ceux créés par CE thérapeute
            return df[df["Therapeute_ID"] == therapeute_id]
    except: pass
    return pd.DataFrame()

# =========================================================
# 2. ÉCRAN DE CONNEXION (NON CONNECTÉ)
# =========================================================

if not st.session_state.authentifie:
    st.title("🧠 Compagnon TCC")
    st.write("Bienvenue dans votre espace de travail thérapeutique.")

    # ONGLETS POUR LA DOUBLE ENTRÉE
    tab_patient, tab_pro = st.tabs(["👤 Accès Patient", "🩺 Accès Thérapeute"])
    
    # --- A. CONNEXION PATIENT ---
    with tab_patient:
        st.info("🔒 Entrez votre code unique fourni par votre thérapeute.")
        with st.form("login_patient"):
            code_input = st.text_input("Code Patient (ex: TCC-X9J...)", type="password")
            btn_pat = st.form_submit_button("Accéder à mon journal")
            
            if btn_pat:
                clean_code = code_input.strip().upper()
                # Vérification
                if verifier_code_patient(clean_code):
                    st.session_state.authentifie = True
                    st.session_state.user_type = "patient"
                    st.session_state.user_id = clean_code
                    st.success("Connexion réussie !")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("❌ Code non reconnu.")

    # --- B. CONNEXION THÉRAPEUTE ---
    with tab_pro:
        st.warning("Espace réservé aux professionnels.")
        with st.form("login_therapeute"):
            user_input = st.text_input("Identifiant")
            pwd_input = st.text_input("Mot de passe", type="password")
            btn_pro = st.form_submit_button("Connexion Pro")
            
            if btn_pro:
                th_id = verifier_therapeute(user_input, pwd_input)
                if th_id:
                    st.session_state.authentifie = True
                    st.session_state.user_type = "therapeute"
                    st.session_state.user_id = th_id
                    st.success(f"Bonjour {th_id}")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("❌ Identifiants incorrects.")

# =========================================================
# 3. TABLEAUX DE BORD (CONNECTÉ)
# =========================================================
else:
# -----------------------------------------------------
    # SCÉNARIO A : TABLEAU DE BORD THÉRAPEUTE
    # -----------------------------------------------------
    if st.session_state.user_type == "therapeute":
        st.title("🩺 Espace Thérapeute")
        c_user, c_deco = st.columns([3, 1])
        with c_user:
            st.write(f"Connecté : **{st.session_state.user_id}**")
        with c_deco:
            if st.button("Se déconnecter", key="logout_th"):
                st.session_state.authentifie = False
                st.rerun()
            
        st.divider()
        
        # --- 1. PROVISIONING (AUTOMATISÉ) ---
        st.subheader("➕ Nouveau Patient")
        
        # --- CALCUL DU PROCHAIN ID ---
        # 1. On récupère les patients existants de ce thérapeute
        df_pats = recuperer_mes_patients(st.session_state.user_id)
        
        # 2. On cherche le premier "PAT-XXX" libre
        prochain_id = "PAT-001"
        if not df_pats.empty:
            # On récupère la liste des commentaires (qui contiennent les IDs : "PAT-001", "PAT-002"...)
            ids_existants = df_pats["Commentaire"].tolist()
            
            # On boucle de 1 à 1000 pour trouver le premier trou
            for i in range(1, 1000):
                test_id = f"PAT-{i:03d}" # Formate en 001, 002, 010...
                if test_id not in ids_existants:
                    prochain_id = test_id
                    break
        # -----------------------------

        st.info(f"Création automatique du patient : **{prochain_id}**")
        
        with st.form("create_patient"):
            c1, c2 = st.columns(2)
            with c1:
                # Champ bloqué (disabled=True) avec la valeur calculée
                id_dossier = st.text_input("Identifiant (Auto)", value=prochain_id, disabled=True)
            with c2:
                # On ne stocke pas le nom, c'est juste pour le cerveau du thérapeute à l'instant T
                # Le code ci-dessous n'enregistrera PAS ce champ dans le Cloud pour respecter votre règle
                note_perso = st.text_input("Note (Optionnelle, non sauvegardée)", placeholder="ex: Mme Dupont")
            
            submitted = st.form_submit_button("Générer l'accès")
            
            if submitted:
                # Génération du code technique
                access_code = generer_code_securise(prefix="TCC")
                
                # Sauvegarde : On ne sauvegarde QUE l'ID Dossier (PAT-XXX) dans le commentaire
                try:
                    from connect_db import save_data
                    save_data("Codes_Patients", [
                        access_code, 
                        st.session_state.user_id, 
                        id_dossier, # C'est PAT-001
                        str(datetime.now().date())
                    ])
                    
                    st.success(f"✅ Patient {id_dossier} activé !")
                    
                    # AFFICHAGE DU COUPON
                    st.markdown("---")
                    st.markdown(f"### 📂 Dossier : **{id_dossier}**")
                    if note_perso:
                        st.caption(f"Pour : {note_perso}")
                    st.markdown("Donnez ce code unique au patient :")
                    st.code(access_code, language="text")
                    st.warning("Notez la correspondance (PAT-XXX = Mme Dupont) dans votre dossier papier.")
                    st.markdown("---")
                    
                    # Petit délai pour laisser lire avant de rafraîchir la liste
                    time.sleep(2)
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Erreur : {e}")

        st.divider()

        # --- 2. SUPERVISION ---
        st.subheader("🔎 Visualiser les données")
        
        # On rafraîchit la liste
        df_pats = recuperer_mes_patients(st.session_state.user_id)
        
        if not df_pats.empty:
            # Map : PAT-001 -> TCC-XYZ
            map_patients = dict(zip(df_pats["Commentaire"], df_pats["Code"]))
            
            choix_patient = st.selectbox(
                "Sélectionnez un dossier à consulter :", 
                options=sorted(df_pats["Commentaire"].unique()), # Trié par ordre alphabétique (PAT-001, 002...)
                index=None
            )
            
            if choix_patient:
                code_technique = map_patients[choix_patient]
                st.info(f"Visualisation du dossier : **{choix_patient}**")
                
                # Exemple Sommeil
                try:
                    from connect_db import load_data
                    data_sommeil = load_data("Sommeil")
                    if data_sommeil:
                        df_sommeil = pd.DataFrame(data_sommeil)
                        # Filtre sur le code technique
                        if "Patient" in df_sommeil.columns:
                            df_patient_sommeil = df_sommeil[df_sommeil["Patient"] == code_technique]
                            
                            if not df_patient_sommeil.empty:
                                st.write(f"🌙 Données de Sommeil ({len(df_patient_sommeil)} nuits)")
                                st.dataframe(
                                    df_patient_sommeil.drop(columns=["Patient"]), 
                                    use_container_width=True,
                                    hide_index=True
                                )
                            else:
                                st.warning("Pas de données de sommeil.")
                except: pass
        else:
            st.info("Aucun patient.")
            

    # -----------------------------------------------------
    # SCÉNARIO B : TABLEAU DE BORD PATIENT
    # -----------------------------------------------------
    elif st.session_state.user_type == "patient":
        
        c_titre, c_logout = st.columns([4, 1])
        with c_titre:
            st.title(f"🧠 Bonjour")
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