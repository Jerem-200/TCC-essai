import streamlit as st
import pandas as pd
import time
import secrets
import string
from datetime import datetime

st.set_page_config(page_title="TCC Companion", page_icon="🧠", layout="centered")

# =========================================================
# 0. SECURITY & UTILS
# =========================================================

def generate_secure_code(prefix="PAT", length=6):
    """Generates a random, secure code (e.g., PAT-X9J2M)"""
    chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789" # No I, 1, O, 0 to avoid confusion
    suffix = ''.join(secrets.choice(chars) for _ in range(length))
    return f"{prefix}-{suffix}"

# --- SESSION INITIALIZATION ---
if "authentifie" not in st.session_state:
    st.session_state.authentifie = False
if "user_type" not in st.session_state:
    st.session_state.user_type = None # "patient" or "therapeute"
if "user_id" not in st.session_state:
    st.session_state.user_id = "" 

# =========================================================
# 1. DATABASE FUNCTIONS
# =========================================================

@st.cache_data(ttl=60)
def verify_therapist(username, password):
    """Checks credentials against the 'Therapeutes' sheet"""
    try:
        from connect_db import load_data
        data = load_data("Therapeutes")
        if data:
            df = pd.DataFrame(data)
            # Find row matching username AND password
            user_row = df[(df["Identifiant"] == username) & (df["MotDePasse"] == password)]
            if not user_row.empty:
                return user_row.iloc[0]["ID"] # Returns 'TH-01'
    except Exception as e:
        print(f"Login Error: {e}")
    return None

@st.cache_data(ttl=60)
def verify_patient_code(code):
    """Checks if patient code exists in 'Codes_Patients'"""
    try:
        from connect_db import load_data
        data = load_data("Codes_Patients")
        if data:
            df = pd.DataFrame(data)
            if "Code" in df.columns:
                # Check if code exists
                if code.upper() in df["Code"].astype(str).str.upper().values:
                    return True
    except Exception as e:
        print(f"Patient Login Error: {e}")
    return False

def get_my_patients(therapist_id):
    """Fetches patients linked to this therapist"""
    try:
        from connect_db import load_data
        data = load_data("Codes_Patients")
        if data:
            df = pd.DataFrame(data)
            return df[df["Therapeute_ID"] == therapist_id]
    except: pass
    return pd.DataFrame()

# =========================================================
# 2. LOGIN SCREEN (NOT AUTHENTICATED)
# =========================================================

if not st.session_state.authentifie:
    st.title("🧠 Compagnon TCC")
    st.write("Bienvenue dans votre espace de travail thérapeutique.")

    # TABS FOR DOUBLE ENTRY
    tab_patient, tab_pro = st.tabs(["👤 Accès Patient", "🩺 Accès Thérapeute"])
    
    # --- A. PATIENT LOGIN ---
    with tab_patient:
        st.info("🔒 Entrez votre code unique fourni par votre thérapeute.")
        with st.form("login_patient"):
            code_input = st.text_input("Code Patient (ex: TCC-X9J...)", type="password")
            btn_pat = st.form_submit_button("Accéder à mon journal")
            
            if btn_pat:
                clean_code = code_input.strip().upper()
                # Verification
                if verify_patient_code(clean_code):
                    st.session_state.authentifie = True
                    st.session_state.user_type = "patient"
                    st.session_state.user_id = clean_code
                    st.success("Connexion réussie !")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("❌ Code non reconnu.")

    # --- B. THERAPIST LOGIN ---
    with tab_pro:
        st.warning("Espace réservé aux professionnels.")
        with st.form("login_therapeute"):
            user_input = st.text_input("Identifiant")
            pwd_input = st.text_input("Mot de passe", type="password")
            btn_pro = st.form_submit_button("Connexion Pro")
            
            if btn_pro:
                th_id = verify_therapist(user_input, pwd_input)
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
# 3. DASHBOARDS (AUTHENTICATED)
# =========================================================
else:
    # -----------------------------------------------------
    # SCENARIO A: THERAPIST DASHBOARD
    # -----------------------------------------------------
    if st.session_state.user_type == "therapeute":
        st.title("🩺 Espace Thérapeute")
        st.write(f"Connecté en tant que : **{st.session_state.user_id}**")
        
        if st.button("Se déconnecter", key="logout_th"):
            st.session_state.authentifie = False
            st.rerun()
            
        st.divider()
        
        # --- 1. GENERATE NEW PATIENT ---
        st.subheader("➕ Générer un accès patient")
        st.caption("Créez un code unique sécurisé pour un nouveau patient.")
        
        with st.form("create_patient"):
            comment = st.text_input("Note interne (ex: M. Dupont - Anxiété)", placeholder="Nom ou initiales pour vous souvenir")
            submitted = st.form_submit_button("Générer le code")
            
            if submitted:
                # 1. Generate Secure Code
                new_code = generate_secure_code(prefix="TCC")
                
                # 2. Save to Cloud
                try:
                    from connect_db import save_data
                    # Columns: Code | Therapeute_ID | Commentaire | Date_Creation
                    save_data("Codes_Patients", [
                        new_code, 
                        st.session_state.user_id, 
                        comment, 
                        str(datetime.now().date())
                    ])
                    st.success("✅ Patient créé !")
                    st.info(f"🔑 Code à transmettre : **{new_code}**")
                    st.warning("Notez ce code maintenant, il permet au patient d'accéder à l'app.")
                    
                except Exception as e:
                    st.error(f"Erreur de sauvegarde : {e}")

        st.divider()
        
        # --- 2. LIST MY PATIENTS ---
        st.subheader("📂 Mes Patients actifs")
        df_pats = get_my_patients(st.session_state.user_id)
        
        if not df_pats.empty:
            st.dataframe(
                df_pats[["Code", "Commentaire", "Date_Creation"]], 
                use_container_width=True, 
                hide_index=True
            )
        else:
            st.info("Aucun patient enregistré pour le moment.")
            

    # -----------------------------------------------------
    # SCENARIO B: PATIENT DASHBOARD (Your existing logic)
    # -----------------------------------------------------
    elif st.session_state.user_type == "patient":
        
        # Header & Logout
        c_titre, c_logout = st.columns([4, 1])
        with c_titre:
            st.title(f"🧠 Bonjour")
        with c_logout:
            if st.button("Se déconnecter", key="logout_pat"):
                st.session_state.authentifie = False
                st.rerun()

        st.subheader("Tableau de bord personnel")
        st.divider()

        # 
        # (Note: Streamlit renders UI, inserting image here is metaphorical for the layout below)

        # --- ROW 1 : COGNITION ---
        c1, c2, c3 = st.columns(3)
        with c1:
            st.info("### 🧩 Restructuration")
            st.write("Colonnes de Beck")
            st.page_link("pages/01_Colonnes_Beck.py", label="Lancer", icon="➡️")
        with c2:
            st.info("### 📊 Humeur (PHQ-9)")
            st.write("Suivi dépression")
            st.page_link("pages/02_Echelles_BDI.py", label="Tester", icon="➡️")
        with c3:
            st.info("### ⚖️ Balance")
            st.write("Pour & Contre")
            st.page_link("pages/11_Balance_Decisionnelle.py", label="Peser", icon="➡️")

        st.divider()

        # --- ROW 2 : ACTION ---
        c4, c5, c6 = st.columns(3)
        with c4:
            st.error("### 🧘 Relaxation")
            st.write("Respiration")
            st.page_link("pages/07_Relaxation.py", label="Lancer", icon="➡️")
        with c5:
            st.error("### 💡 Résolution")
            st.write("Trouver solutions")
            st.page_link("pages/06_Resolution_Probleme.py", label="Lancer", icon="➡️")
        with c6:
            st.error("### 🧗 Exposition")
            st.write("Affronter peurs")
            st.page_link("pages/09_Exposition.py", label="Planifier", icon="➡️")

        st.divider()

        # --- ROW 3 : TRACKING ---
        c7, c8, c9 = st.columns(3)
        with c7:
            st.warning("### 🌙 Sommeil")
            st.write("Agenda sommeil")
            st.page_link("pages/10_Agenda_Sommeil.py", label="Noter", icon="➡️")
        with c8:
            st.warning("### 📝 Activités")
            st.write("Plaisir & Maîtrise")
            st.page_link("pages/05_Registre_Activites.py", label="Ouvrir", icon="➡️")
        with c9:
            st.warning("### 🍷 Consos") 
            st.write("Envies & Substances")
            st.page_link("pages/13_Agenda_Consos.py", label="Ouvrir", icon="➡️") 

        st.divider()

        # --- ROW 4 : DATA ---
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

        # --- SIDEBAR ---
        with st.sidebar:
            st.write(f"👤 ID: **{st.session_state.user_id}**")
            st.divider()
            st.title("Navigation")
            st.page_link("streamlit_app.py", label="🏠 Accueil")
            st.page_link("pages/01_Colonnes_Beck.py", label="🧩 Tableau de Beck")
            st.page_link("pages/02_Echelles_BDI.py", label="📊 BDI / PHQ-9")
            st.page_link("pages/05_Registre_Activites.py", label="📝 Activités")
            st.page_link("pages/06_Resolution_Probleme.py", label="💡 Résolution")
            st.page_link("pages/07_Relaxation.py", label="🧘 Relaxation")
            st.page_link("pages/09_Exposition.py", label="🧗 Exposition")
            st.page_link("pages/10_Agenda_Sommeil.py", label="🌙 Sommeil")
            st.page_link("pages/11_Balance_Decisionnelle.py", label="⚖️ Balance")
            st.page_link("pages/13_Agenda_Consos.py", label="🍷 Consommation")
            st.page_link("pages/03_Ressources.py", label="📚 Ressources")