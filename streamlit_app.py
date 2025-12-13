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
    st.session_state.user_type = None # "patient" ou "therapeute"
if "user_id" not in st.session_state:
    st.session_state.user_id = "" 

# =========================================================
# 1. FONCTIONS DE BASE DE DONNÉES (OPTIMISÉES)
# =========================================================

@st.cache_data(ttl=300) # Cache de 5 minutes pour éviter de recharger à chaque clic
def verifier_therapeute(identifiant, mot_de_passe):
    """Vérifie les accès dans l'onglet 'Therapeutes'"""
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
        st.error(f"Erreur connexion Thérapeute : {e}")
    return None

@st.cache_data(ttl=300)
def verifier_code_patient(code):
    """Vérifie si le code existe dans 'Codes_Patients'"""
    try:
        from connect_db import load_data
        data = load_data("Codes_Patients")
        if data:
            df = pd.DataFrame(data)
            if "Code" in df.columns:
                if code.upper() in df["Code"].astype(str).str.upper().values:
                    return True
    except Exception as e:
        st.error(f"Erreur connexion Patient : {e}")
    return False

# Optimisation : On ne charge pas à chaque interaction, on utilise le cache
@st.cache_data(ttl=60) 
def recuperer_mes_patients(therapeute_id):
    """Récupère la liste des patients liés à ce thérapeute"""
    try:
        from connect_db import load_data
        data = load_data("Codes_Patients")
        if data:
            df = pd.DataFrame(data)
            return df[df["Therapeute_ID"] == therapeute_id]
    except: pass
    return pd.DataFrame()

# Nouvelle fonction optimisée pour charger les données d'un seul patient
@st.cache_data(ttl=60)
def charger_donnees_patient(type_donnee, patient_id):
    try:
        from connect_db import load_data
        data = load_data(type_donnee)
        if data:
            df = pd.DataFrame(data)
            if "Patient" in df.columns:
                return df[df["Patient"] == patient_id]
    except: pass
    return pd.DataFrame()

# =========================================================
# 2. ÉCRAN DE CONNEXION (NON CONNECTÉ)
# =========================================================

if not st.session_state.authentifie:
    st.title("🧠 Compagnon TCC")
    st.write("Bienvenue dans votre espace de travail thérapeutique.")

    tab_patient, tab_pro = st.tabs(["👤 Accès Patient", "🩺 Accès Thérapeute"])
    
    # --- A. CONNEXION PATIENT ---
    with tab_patient:
        st.info("🔒 Entrez votre code unique fourni par votre thérapeute.")
        with st.form("login_patient"):
            code_input = st.text_input("Code Patient (ex: TCC-X9J...)", type="password")
            btn_pat = st.form_submit_button("Accéder à mon journal")
            
            if btn_pat:
                clean_code = code_input.strip().upper()
                
                if verifier_code_patient(clean_code):
                    st.session_state.authentifie = True
                    st.session_state.user_type = "patient"
                    
                    # RÉCUPÉRATION DU VRAI ID (PAT-001)
                    final_id = clean_code 
                    try:
                        from connect_db import load_data
                        data_patients = load_data("Codes_Patients")
                        if data_patients:
                            df_p = pd.DataFrame(data_patients)
                            match = df_p[df_p["Code"].astype(str).str.upper() == clean_code]
                            if not match.empty:
                                col_cible = "Identifiant" if "Identifiant" in df_p.columns else "Commentaire"
                                if col_cible in df_p.columns:
                                    final_id = match.iloc[0][col_cible]
                    except Exception as e:
                        print(f"Erreur conversion ID: {e}")

                    st.session_state.user_id = final_id 
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
    # SCÉNARIO A : TABLEAU DE BORD THÉRAPEUTE (COCKPIT)
    # -----------------------------------------------------
    if st.session_state.user_type == "therapeute":
        st.title("🩺 Espace Thérapeute")
        
        # --- EN-TÊTE ---
        c_user, c_deco = st.columns([3, 1])
        with c_user:
            st.write(f"Praticien connecté : **{st.session_state.user_id}**")
        with c_deco:
            if st.button("Se déconnecter", key="logout_th"):
                st.session_state.authentifie = False
                st.rerun()
        st.divider()

        # --- 1. GESTION DES PATIENTS ---
        with st.expander("➕ Créer un nouveau patient (Générer Code)", expanded=False):
            # Calcul auto ID
            df_pats = recuperer_mes_patients(st.session_state.user_id)
            prochain_id = "PAT-001"
            if not df_pats.empty:
                try:
                    ids = df_pats["Identifiant"].tolist()
                    nums = [int(x.split('-')[1]) for x in ids if x.startswith("PAT-") and '-' in x]
                    if nums: prochain_id = f"PAT-{max(nums)+1:03d}"
                except: pass

            c_gen1, c_gen2 = st.columns([1, 2])
            with c_gen1:
                id_dossier = st.text_input("Identifiant Dossier", value=prochain_id)
            with c_gen2:
                st.write(" ")
                if st.button("Générer l'accès"):
                    access_code = generer_code_securise(prefix="TCC")
                    try:
                        from connect_db import save_data
                        save_data("Codes_Patients", [
                            access_code, 
                            st.session_state.user_id, 
                            id_dossier, 
                            str(datetime.now().date())
                        ])
                        st.success(f"✅ Patient créé : {id_dossier}")
                        st.info(f"🔑 CODE D'ACCÈS À DONNER AU PATIENT : **{access_code}**")
                        # On invalide le cache pour voir le nouveau patient tout de suite
                        recuperer_mes_patients.clear()
                    except Exception as e:
                        st.error(f"Erreur : {e}")

        # --- 2. SÉLECTION DU PATIENT À ANALYSER ---
        st.subheader("📂 Suivi Clinique")
        
        df_mes_patients = recuperer_mes_patients(st.session_state.user_id)
        
        if df_mes_patients.empty:
            st.warning("Vous n'avez pas encore de patients enregistrés.")
        else:
            liste_patients = df_mes_patients["Identifiant"].unique().tolist()
            patient_selectionne = st.selectbox("Sélectionnez le dossier à consulter :", liste_patients)

            if patient_selectionne:
                st.markdown(f"### 👤 Dossier : {patient_selectionne}")
                
                # ONGLETS DE VISUALISATION
                t1, t2, t3, t4, t5 = st.tabs(["🧩 Beck", "🌙 Sommeil", "📝 Activités", "🍷 Conso", "🛑 Compulsions"])
                
                # BECK
                with t1:
                    st.caption(f"Exercices de restructuration cognitive pour {patient_selectionne}")

                    # A. FORMULAIRE DE SAISIE "EN SÉANCE"
                    with st.expander("➕ Remplir une colonne de Beck avec le patient (En séance)"):
                        with st.form("beck_therapeute_form"):
                            c_dt, c_sit = st.columns([1, 2])
                            date_th = c_dt.date_input("Date", datetime.now(), key="th_date")
                            situation_th = c_sit.text_input("Situation", key="th_sit")
                            
                            c_emo, c_int = st.columns(2)
                            emo_th = c_emo.text_input("Émotion", key="th_emo")
                            int_th = c_int.slider("Intensité (0-10)", 0, 10, 7, key="th_int")
                            
                            pensee_th = st.text_area("Pensée Automatique", key="th_auto")
                            rationnel_th = st.text_area("Pensée Alternative / Rationnelle", key="th_rat")
                            
                            submit_th = st.form_submit_button("Enregistrer dans le dossier du patient")

                            if submit_th:
                                new_entry = [
                                    patient_selectionne, 
                                    str(date_th), situation_th, emo_th, int_th, 
                                    pensee_th, 0, rationnel_th, 0, 0, 0
                                ]
                                try:
                                    from connect_db import save_data
                                    save_data("Beck", new_entry)
                                    st.success(f"✅ Exercice ajouté !")
                                    time.sleep(1)
                                    # On invalide le cache pour voir la nouvelle donnée
                                    charger_donnees_patient.clear()
                                    st.rerun() 
                                except Exception as e:
                                    st.error(f"Erreur : {e}")

                    st.divider()

                    # B. AFFICHAGE DE L'HISTORIQUE (Lecture seule)
                    df_b = charger_donnees_patient("Beck", patient_selectionne)
                    if not df_b.empty:
                        # On trie par date récente
                        if "Date" in df_b.columns:
                            df_b = df_b.sort_values(by="Date", ascending=False)
                        st.dataframe(
                            df_b[["Date", "Situation", "Émotion", "Pensée Auto", "Pensée Rationnelle"]], 
                            use_container_width=True, 
                            hide_index=True
                        )
                    else:
                        st.info("Ce patient n'a pas encore rempli de colonnes de Beck.")

                # SOMMEIL
                with t2:
                    df_s = charger_donnees_patient("Sommeil", patient_selectionne)
                    if not df_s.empty:
                        if "Efficacité" in df_s.columns:
                            eff_val = pd.to_numeric(df_s["Efficacité"].astype(str).str.replace('%',''), errors='coerce').mean()
                            st.metric("Efficacité Moyenne", f"{eff_val:.1f} %")
                        st.dataframe(df_s, use_container_width=True, hide_index=True)
                    else: st.info("Aucune donnée.")

                # ACTIVITÉS
                with t3:
                    df_a = charger_donnees_patient("Activites", patient_selectionne)
                    if not df_a.empty:
                        st.dataframe(df_a, use_container_width=True, hide_index=True)
                    else: st.info("Aucune donnée.")

                # ADDICTIONS
                with t4:
                    df_add = charger_donnees_patient("Addictions", patient_selectionne)
                    if not df_add.empty:
                        st.dataframe(df_add, use_container_width=True, hide_index=True)
                    else: st.info("Aucune donnée.")

                # COMPULSIONS
                with t5:
                    df_c = charger_donnees_patient("Compulsions", patient_selectionne)
                    if not df_c.empty:
                        st.dataframe(df_c, use_container_width=True, hide_index=True)
                    else: st.info("Aucune donnée.")


    # -----------------------------------------------------
    # SCÉNARIO B : TABLEAU DE BORD PATIENT
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

        st.write("") 

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

        st.write("") 

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
        st.page_link("pages/03_Ressources.py", label="📚 Consulter les Fiches & Ressources", icon="🔖")


    # =========================================================
    # 4. SIDEBAR (MENU LATÉRAL) - CORRIGÉ
    # =========================================================
    with st.sidebar:
        
        # A. LOGIQUE PATIENT (ID + MENU COMPLET)
        if st.session_state.user_type == "patient":
            display_id = st.session_state.user_id 
            try:
                from connect_db import load_data
                infos = load_data("Codes_Patients")
                if infos:
                    df_infos = pd.DataFrame(infos)
                    # On utilise l'Identifiant (PAT-XXX) pour chercher
                    code_actuel = str(st.session_state.user_id).strip().upper()
                    match = df_infos[df_infos["Identifiant"].astype(str).str.strip().str.upper() == code_actuel]
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

        # B. LOGIQUE THÉRAPEUTE (JUSTE RETOUR ACCUEIL)
        else:
            st.title("Navigation")
            st.page_link("streamlit_app.py", label="🏠 Accueil")