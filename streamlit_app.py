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
                    
                    # --- CORRECTION : ON RÉCUPÈRE LE VRAI ID (PAT-01) ---
                    # Par défaut, on garde le code, mais on va essayer de trouver mieux
                    final_id = clean_code 
                    
                    try:
                        from connect_db import load_data
                        data_patients = load_data("Codes_Patients")
                        if data_patients:
                            df_p = pd.DataFrame(data_patients)
                            # On cherche la ligne qui contient ce Code
                            match = df_p[df_p["Code"].astype(str).str.upper() == clean_code]
                            if not match.empty:
                                # On capture la colonne Identifiant (ex: PAT-01)
                                final_id = match.iloc[0]["Identifiant"]
                    except Exception as e:
                        print(f"Erreur récupération ID: {e}")

                    # C'est ici que la magie opère : on stocke PAT-01 au lieu du code secret
                    st.session_state.user_id = final_id 
                    # --------------------------------------------------------

                    st.success(f"Connexion réussie ! Bienvenue {final_id}")
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

        # =========================================================
        # ZONE DE NOTIFICATION (CODE PATIENT)
        # C'est ici que le code s'affiche et RESTE affiché
        # =========================================================
        if "new_patient_created" in st.session_state and st.session_state.new_patient_created:
            info = st.session_state.new_patient_created
            
            st.success("✅ Création réussie !")
            with st.container(border=True):
                st.markdown(f"### 📂 Dossier : **{info['id']}**")
                st.markdown("Transmettez ce code d'accès au patient :")
                st.code(info['code'], language="text")
                st.warning("⚠️ Notez-le dans votre dossier papier maintenant.")
                
                # Le bouton pour fermer la notification manuellement
                if st.button("C'est bon, j'ai noté le code"):
                    # On nettoie la mémoire et on ferme
                    del st.session_state.new_patient_created
                    st.rerun()
            st.divider()
        # =========================================================
        
        # --- 1. PROVISIONING (AUTOMATISÉ) ---
        st.subheader("➕ Nouveau Patient")
        
        # Calcul automatique du prochain ID
        df_pats = recuperer_mes_patients(st.session_state.user_id)
        prochain_id = "PAT-001"
        if not df_pats.empty:
            ids_existants = df_pats["Identifiant"].tolist()
            for i in range(1, 1000):
                test_id = f"PAT-{i:03d}"
                if test_id not in ids_existants:
                    prochain_id = test_id
                    break

        st.info(f"Création du dossier : **{prochain_id}**")
        
        with st.form("create_patient"):
            # Plus besoin de colonnes (c1, c2) car il n'y a qu'un seul champ
            id_dossier = st.text_input("Identifiant (Auto)", value=prochain_id, disabled=True)
            
            submitted = st.form_submit_button("Générer l'accès")
            
            if submitted:
                # Génération Code
                access_code = generer_code_securise(prefix="TCC")
                
                try:
                    from connect_db import save_data
                    save_data("Codes_Patients", [
                        access_code, 
                        st.session_state.user_id, 
                        id_dossier, 
                        str(datetime.now().date())
                    ])
                    
                    # Stockage session pour affichage persistant (Pop-up vert)
                    st.session_state.new_patient_created = {
                        "id": id_dossier,
                        "code": access_code
                    }
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Erreur : {e}")
        
        # --- 2. LISTE DE MES PATIENTS ---
        st.subheader("📂 Mes Patients actifs")
        df_pats = recuperer_mes_patients(st.session_state.user_id)
        
        if not df_pats.empty:
            # On affiche uniquement les colonnes utiles
            cols_to_show = ["Code", "Identifiant", "Date_Creation"]
            # On vérifie qu'elles existent pour éviter les bugs
            final_cols = [c for c in cols_to_show if c in df_pats.columns]
            
            st.dataframe(
                df_pats[final_cols], 
                use_container_width=True, 
                hide_index=True
            )
        else:
            st.info("Aucun patient enregistré pour le moment.")
            

# -----------------------------------------------------
    # SCÉNARIO B : TABLEAU DE BORD PATIENT (ORGANISÉ)
    # -----------------------------------------------------
    elif st.session_state.user_type == "patient":
        
        c_titre, c_logout = st.columns([4, 1])
        with c_titre:
            st.title(f"🧠 Espace Patient")
        with c_logout:
            if st.button("Se déconnecter"):
                st.session_state.authentifie = False
                st.session_state.user_id = "" 
                st.rerun()

        st.divider()

        # --- SECTION 1 : AGENDAS (Suivi quotidien) ---
        st.markdown("### 📅 Mes Agendas (Suivi quotidien)")
        st.caption("À remplir régulièrement pour suivre vos habitudes.")
        
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.warning("**Sommeil**")
            st.page_link("pages/10_Agenda_Sommeil.py", label="Ouvrir", icon="🌙")
        with c2:
            st.warning("**Activités**")
            st.page_link("pages/05_Registre_Activites.py", label="Ouvrir", icon="📝")
        with c3:
            st.warning("**Consommations**")
            st.page_link("pages/13_Agenda_Consos.py", label="Ouvrir", icon="🍷")
        with c4:
            st.warning("**Compulsions**")
            st.page_link("pages/14_Agenda_Compulsions.py", label="Ouvrir", icon="🛑")

        st.write("") # Espace

        # --- SECTION 2 : OUTILS TCC (Exercices ponctuels) ---
        st.markdown("### 🛠️ Outils Thérapeutiques (Exercices)")
        st.caption("À utiliser face à une difficulté ou pour travailler sur soi.")
        
        c5, c6, c7 = st.columns(3)
        with c5:
            st.info("**Restructuration (Beck)**")
            st.write("Analyser une pensée")
            st.page_link("pages/01_Colonnes_Beck.py", label="Lancer", icon="🧩")
            st.write("")
            st.info("**Analyse SORC**")
            st.write("Décortiquer une situation")
            st.page_link("pages/12_Analyse_SORC.py", label="Lancer", icon="🔍")
            
        with c6:
            st.info("**Résolution Problème**")
            st.write("Trouver des solutions")
            st.page_link("pages/06_Resolution_Probleme.py", label="Lancer", icon="💡")
            st.write("")
            st.info("**Balance Décisionnelle**")
            st.write("Faire un choix")
            st.page_link("pages/11_Balance_Decisionnelle.py", label="Lancer", icon="⚖️")

        with c7:
            st.info("**Exposition**")
            st.write("Affronter une peur")
            st.page_link("pages/09_Exposition.py", label="Lancer", icon="🧗")
            st.write("")
            st.info("**Relaxation**")
            st.write("Se détendre")
            st.page_link("pages/07_Relaxation.py", label="Lancer", icon="🧘")

        st.write("") # Espace

        # --- SECTION 3 : ANALYSE & RESSOURCES ---
        st.markdown("### 📊 Mesures & Bilan")
        
        c8, c9, c10 = st.columns(3)
        with c8:
            st.success("**Échelles (BDI)**")
            st.page_link("pages/02_Echelles_BDI.py", label="Mesurer l'humeur", icon="📉")
        with c9:
            st.success("**Historique Global**")
            st.page_link("pages/04_Historique.py", label="Voir mes progrès", icon="📜")
        with c10:
            st.success("**Exporter Données**")
            st.page_link("pages/08_Export_Rapport.py", label="Créer un PDF", icon="📤")

        st.divider()
        
        # Petit lien ressources discret en bas
        st.page_link("pages/03_Ressources.py", label="📚 Consulter les Fiches & Ressources", icon="🔖")


        # --- SIDEBAR (MENU LATÉRAL) ---
        with st.sidebar:
            
            # LOGIQUE D'AFFICHAGE NOM PATIENT
            display_id = st.session_state.user_id 
            try:
                from connect_db import load_data
                infos = load_data("Codes_Patients")
                if infos:
                    df_infos = pd.DataFrame(infos)
                    code_actuel = str(st.session_state.user_id).strip().upper()
                    match = df_infos[df_infos["Code"].astype(str).str.strip().str.upper() == code_actuel]
                    if not match.empty:
                        col_id = "Identifiant" if "Identifiant" in df_infos.columns else "Commentaire"
                        display_id = match.iloc[0][col_id]
            except: pass
            
            st.write(f"👤 ID: **{display_id}**")
            
            st.divider()
            st.title("Navigation Rapide")
            st.page_link("streamlit_app.py", label="🏠 Accueil")
            st.caption("Agendas")
            st.page_link("pages/10_Agenda_Sommeil.py", label="🌙 Sommeil")
            st.page_link("pages/05_Registre_Activites.py", label="📝 Activités")
            st.page_link("pages/13_Agenda_Consos.py", label="🍷 Consommations")
            st.page_link("pages/14_Agenda_Compulsions.py", label="🛑 Compulsions")
            st.caption("Outils")
            st.page_link("pages/01_Colonnes_Beck.py", label="🧩 Beck")
            st.page_link("pages/12_Analyse_SORC.py", label="🔍 SORC")
            st.page_link("pages/06_Resolution_Probleme.py", label="💡 Problèmes")
            st.page_link("pages/11_Balance_Decisionnelle.py", label="⚖️ Balance")
            st.page_link("pages/09_Exposition.py", label="🧗 Exposition")
            st.page_link("pages/07_Relaxation.py", label="🧘 Relaxation")
            st.caption("Suivi")
            st.page_link("pages/02_Echelles_BDI.py", label="📊 BDI")
            st.page_link("pages/04_Historique.py", label="📜 Historique")