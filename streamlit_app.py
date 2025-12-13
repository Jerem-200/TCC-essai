import streamlit as st
import pandas as pd
import time
import secrets
from datetime import datetime

st.set_page_config(page_title="Compagnon TCC", page_icon="🧠", layout="wide")

# =========================================================
# 0. SÉCURITÉ & UTILITAIRES
# =========================================================

def generer_code_securise(prefix="PAT", length=6):
    """Génère un code aléatoire sécurisé (ex: PAT-X9J2M)"""
    chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789" 
    suffix = ''.join(secrets.choice(chars) for _ in range(length))
    return f"{prefix}-{suffix}"

# --- INITIALISATION DE LA SESSION ---
if "authentifie" not in st.session_state:
    st.session_state.authentifie = False
if "user_type" not in st.session_state:
    st.session_state.user_type = None 
if "user_id" not in st.session_state:
    st.session_state.user_id = "" 

# =========================================================
# 1. FONCTIONS DE BASE DE DONNÉES (OPTIMISÉES AVEC CACHE)
# =========================================================

# Cache de 10 min pour les comptes thérapeutes (change rarement)
@st.cache_data(ttl=600)
def verifier_therapeute(identifiant, mot_de_passe):
    try:
        from connect_db import load_data
        data = load_data("Therapeutes")
        if data:
            df = pd.DataFrame(data)
            df["Identifiant"] = df["Identifiant"].astype(str).str.strip()
            df["MotDePasse"] = df["MotDePasse"].astype(str).str.strip()
            
            user_clean = str(identifiant).strip()
            pwd_clean = str(mot_de_passe).strip()

            user_row = df[(df["Identifiant"] == user_clean) & (df["MotDePasse"] == pwd_clean)]
            if not user_row.empty:
                return user_row.iloc[0]["ID"] 
    except Exception as e:
        st.error(f"Erreur connexion : {e}")
    return None

# Cache de 5 min pour la liste des patients
@st.cache_data(ttl=300)
def recuperer_mes_patients(therapeute_id):
    try:
        from connect_db import load_data
        data = load_data("Codes_Patients")
        if data:
            df = pd.DataFrame(data)
            return df[df["Therapeute_ID"] == therapeute_id]
    except: pass
    return pd.DataFrame()

# Cache de 2 min pour les données cliniques (Beck, Sommeil...)
# Cela évite de recharger Google Sheet à chaque clic sur un onglet
@st.cache_data(ttl=120)
def charger_donnees_specifiques(nom_onglet, patient_id):
    try:
        from connect_db import load_data
        data = load_data(nom_onglet)
        if data:
            df = pd.DataFrame(data)
            # On vérifie si la colonne Patient existe et on filtre
            if "Patient" in df.columns:
                return df[df["Patient"] == patient_id]
    except: pass
    return pd.DataFrame()

# Validation patient (Cache rapide)
@st.cache_data(ttl=300)
def verifier_code_patient(code):
    try:
        from connect_db import load_data
        data = load_data("Codes_Patients")
        if data:
            df = pd.DataFrame(data)
            if "Code" in df.columns:
                if code.upper() in df["Code"].astype(str).str.upper().values:
                    return True
    except: pass
    return False

# =========================================================
# 2. ÉCRAN DE CONNEXION
# =========================================================

if not st.session_state.authentifie:
    st.title("🧠 Compagnon TCC")
    st.write("Bienvenue dans votre espace de travail thérapeutique.")

    tab_patient, tab_pro = st.tabs(["👤 Accès Patient", "🩺 Accès Thérapeute"])
    
    # --- A. PATIENT ---
    with tab_patient:
        st.info("🔒 Entrez votre code unique fourni par votre thérapeute.")
        with st.form("login_patient"):
            code_input = st.text_input("Code Patient (ex: TCC-X9J...)", type="password")
            if st.form_submit_button("Accéder à mon journal"):
                clean_code = code_input.strip().upper()
                if verifier_code_patient(clean_code):
                    st.session_state.authentifie = True
                    st.session_state.user_type = "patient"
                    
                    # Récupération ID propre
                    final_id = clean_code 
                    try:
                        from connect_db import load_data
                        data_p = load_data("Codes_Patients")
                        if data_p:
                            df_p = pd.DataFrame(data_p)
                            match = df_p[df_p["Code"].astype(str).str.upper() == clean_code]
                            if not match.empty:
                                c_cible = "Identifiant" if "Identifiant" in df_p.columns else "Commentaire"
                                final_id = match.iloc[0][c_cible]
                    except: pass

                    st.session_state.user_id = final_id 
                    st.success(f"Bienvenue {final_id}")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("❌ Code non reconnu.")

    # --- B. THÉRAPEUTE ---
    with tab_pro:
        st.warning("Espace réservé aux professionnels.")
        with st.form("login_therapeute"):
            u_in = st.text_input("Identifiant")
            p_in = st.text_input("Mot de passe", type="password")
            if st.form_submit_button("Connexion Pro"):
                th_id = verifier_therapeute(u_in, p_in)
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
    # A. ESPACE THÉRAPEUTE (OPTIMISÉ)
    # -----------------------------------------------------
    if st.session_state.user_type == "therapeute":
        st.title("🩺 Espace Thérapeute")
        
        c1, c2 = st.columns([3, 1])
        with c1: st.write(f"Praticien : **{st.session_state.user_id}**")
        with c2: 
            if st.button("Déconnexion"):
                st.session_state.authentifie = False
                st.rerun()
        st.divider()

        # 1. CRÉATION PATIENT
        with st.expander("➕ Nouveau Patient"):
            df_pats = recuperer_mes_patients(st.session_state.user_id)
            prochain_id = "PAT-001"
            if not df_pats.empty:
                try:
                    ids = df_pats["Identifiant"].tolist()
                    nums = [int(x.split('-')[1]) for x in ids if x.startswith("PAT-") and '-' in x]
                    if nums: prochain_id = f"PAT-{max(nums)+1:03d}"
                except: pass

            c_gen1, c_gen2 = st.columns([1, 2])
            with c_gen1: id_dossier = st.text_input("Dossier", value=prochain_id)
            with c_gen2:
                st.write(" ")
                if st.button("Générer accès"):
                    ac_code = generer_code_securise("TCC")
                    try:
                        from connect_db import save_data
                        save_data("Codes_Patients", [ac_code, st.session_state.user_id, id_dossier, str(datetime.now().date())])
                        st.success(f"Créé : {id_dossier} -> Code : {ac_code}")
                        recuperer_mes_patients.clear() # On vide le cache pour voir le nouveau
                    except Exception as e: st.error(e)

        # 2. VISUALISATION (Lecture Seule Rapide)
        st.subheader("📂 Dossiers Patients")
        
        df_mes_patients = recuperer_mes_patients(st.session_state.user_id)
        
        if not df_mes_patients.empty:
            liste_patients = df_mes_patients["Identifiant"].unique().tolist()
            patient_sel = st.selectbox("Sélectionner un dossier :", liste_patients)

            if patient_sel:
                st.markdown(f"### 👤 {patient_sel}")
                
                # Onglets de consultation uniquement
                t1, t2, t3, t4, t5 = st.tabs(["🧩 Beck", "🌙 Sommeil", "📝 Activités", "🍷 Conso", "🛑 Compulsions"])
                
                # On utilise la fonction optimisée 'charger_donnees_specifiques'
                with t1:
                    df = charger_donnees_specifiques("Beck", patient_sel)
                    if not df.empty:
                        st.dataframe(df[["Date", "Situation", "Émotion", "Pensée Auto", "Pensée Rationnelle"]], use_container_width=True, hide_index=True)
                    else: st.info("Aucune donnée.")

                with t2:
                    df = charger_donnees_specifiques("Sommeil", patient_sel)
                    if not df.empty:
                        if "Efficacité" in df.columns:
                            val = pd.to_numeric(df["Efficacité"].astype(str).str.replace('%',''), errors='coerce').mean()
                            st.metric("Efficacité Moyenne", f"{val:.1f}%")
                        st.dataframe(df, use_container_width=True, hide_index=True)
                    else: st.info("Aucune donnée.")

                with t3:
                    df = charger_donnees_specifiques("Activites", patient_sel)
                    if not df.empty: st.dataframe(df, use_container_width=True, hide_index=True)
                    else: st.info("Aucune donnée.")

                with t4:
                    df = charger_donnees_specifiques("Addictions", patient_sel)
                    if not df.empty: st.dataframe(df, use_container_width=True, hide_index=True)
                    else: st.info("Aucune donnée.")

                with t5:
                    df = charger_donnees_specifiques("Compulsions", patient_sel)
                    if not df.empty: st.dataframe(df, use_container_width=True, hide_index=True)
                    else: st.info("Aucune donnée.")
        else:
            st.warning("Aucun patient trouvé.")

    # -----------------------------------------------------
    # B. ESPACE PATIENT (Classique)
    # -----------------------------------------------------
    elif st.session_state.user_type == "patient":
        c_ti, c_lo = st.columns([4, 1])
        with c_ti: st.title("🧠 Espace Patient")
        with c_lo: 
            if st.button("Déconnexion"):
                st.session_state.authentifie = False
                st.rerun()
        st.divider()

        st.markdown("### 📅 Suivi quotidien")
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

        st.write("")
        st.markdown("### 🛠️ Exercices TCC")
        c5, c6, c7 = st.columns(3)
        with c5:
            st.info("**Beck**")
            st.page_link("pages/01_Colonnes_Beck.py", label="Restructuration", icon="🧩")
            st.write("")
            st.info("**SORC**")
            st.page_link("pages/12_Analyse_SORC.py", label="Analyse", icon="🔍")
        with c6:
            st.info("**Problèmes**")
            st.page_link("pages/06_Resolution_Probleme.py", label="Résolution", icon="💡")
            st.write("")
            st.info("**Balance**")
            st.page_link("pages/11_Balance_Decisionnelle.py", label="Décision", icon="⚖️")
        with c7:
            st.info("**Exposition**")
            st.page_link("pages/09_Exposition.py", label="Graduée", icon="🧗")
            st.write("")
            st.info("**Relaxation**")
            st.page_link("pages/07_Relaxation.py", label="Détente", icon="🧘")

        st.write("")
        st.markdown("### 📊 Bilan")
        c8, c9, c10 = st.columns(3)
        with c8:
            st.success("**BDI**")
            st.page_link("pages/02_Echelles_BDI.py", label="Humeur", icon="📉")
        with c9:
            st.success("**Historique**")
            st.page_link("pages/04_Historique.py", label="Vue d'ensemble", icon="📜")
        with c10:
            st.success("**Export**")
            st.page_link("pages/08_Export_Rapport.py", label="PDF", icon="📤")
            
        st.divider()
        st.page_link("pages/03_Ressources.py", label="📚 Ressources", icon="🔖")

    # --- SIDEBAR ---
    with st.sidebar:
        if st.session_state.user_type == "patient":
            d_id = st.session_state.user_id
            # Tentative d'affichage propre du nom (Cache léger possible ici si besoin)
            try:
                from connect_db import load_data
                inf = load_data("Codes_Patients")
                if inf:
                    df_i = pd.DataFrame(inf)
                    match = df_i[df_i["Identifiant"] == d_id]
                    if not match.empty: d_id = match.iloc[0]["Identifiant"]
            except: pass
            
            st.write(f"👤 **{d_id}**")
            st.divider()
            st.title("Menu")
            st.page_link("streamlit_app.py", label="Accueil", icon="🏠")
            st.caption("Outils Rapides")
            st.page_link("pages/10_Agenda_Sommeil.py", label="Sommeil")
            st.page_link("pages/01_Colonnes_Beck.py", label="Beck")
            st.page_link("pages/04_Historique.py", label="Historique")
        else:
            st.title("Menu")
            st.page_link("streamlit_app.py", label="Accueil Pro", icon="🩺")