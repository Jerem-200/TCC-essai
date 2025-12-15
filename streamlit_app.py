import streamlit as st
import pandas as pd
import altair as alt
import time
import secrets
from datetime import datetime
# Import de toutes les visualisations
from visualisations import (
    afficher_activites, afficher_sommeil, afficher_conso, afficher_compulsions,
    afficher_phq9, afficher_gad7, afficher_isi, afficher_peg, afficher_who5, afficher_wsas
)

st.set_page_config(page_title="Compagnon TCC", page_icon="🧠", layout="wide")

# =========================================================
# 0. SÉCURITÉ & UTILITAIRES
# =========================================================

def generer_code_securise(prefix="PAT", length=6):
    """Génère un code aléatoire sécurisé (ex: PAT-X9J2M)"""
    chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789" 
    suffix = ''.join(secrets.choice(chars) for _ in range(length))
    return f"{prefix}-{suffix}"

# --- INITIALISATION SESSION ---
if "authentifie" not in st.session_state: st.session_state.authentifie = False
if "user_type" not in st.session_state: st.session_state.user_type = None 
if "user_id" not in st.session_state: st.session_state.user_id = "" 

# =========================================================
# 1. FONCTIONS DE BASE DE DONNÉES (OPTIMISÉES AVEC CACHE)
# =========================================================

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
            if not user_row.empty: return user_row.iloc[0]["ID"] 
    except: pass
    return None

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

# Cache de 2 min pour les données cliniques
@st.cache_data(ttl=120)
def charger_donnees_specifiques(nom_onglet, patient_id):
    try:
        from connect_db import load_data
        data = load_data(nom_onglet)
        if data:
            df = pd.DataFrame(data)
            if "Patient" in df.columns:
                return df[df["Patient"] == patient_id]
    except: pass
    return pd.DataFrame()

@st.cache_data(ttl=300)
def verifier_code_patient(code):
    try:
        from connect_db import load_data
        data = load_data("Codes_Patients")
        if data:
            df = pd.DataFrame(data)
            if "Code" in df.columns:
                if code.upper() in df["Code"].astype(str).str.upper().values: return True
    except: pass
    return False

# =========================================================
# 2. ÉCRAN DE CONNEXION
# =========================================================

if not st.session_state.authentifie:
    st.title("🧠 Compagnon TCC")
    st.write("Bienvenue dans votre espace de travail thérapeutique.")

    tab_patient, tab_pro = st.tabs(["👤 Accès Patient", "🩺 Accès Thérapeute"])
    
    with tab_patient:
        st.info("🔒 Entrez votre code unique fourni par votre thérapeute.")
        with st.form("login_patient"):
            code_input = st.text_input("Code Patient (ex: TCC-X9J...)", type="password")
            if st.form_submit_button("Accéder à mon journal"):
                clean_code = code_input.strip().upper()
                if verifier_code_patient(clean_code):
                    st.session_state.authentifie = True
                    st.session_state.user_type = "patient"
                    
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
                else: st.error("❌ Code non reconnu.")

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
                else: st.error("❌ Identifiants incorrects.")

# =========================================================
# 3. TABLEAUX DE BORD (CONNECTÉ)
# =========================================================
else:
    # -----------------------------------------------------
    # A. ESPACE THÉRAPEUTE (OPTIMISÉ & COMPLET)
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
                        recuperer_mes_patients.clear()
                    except Exception as e: st.error(e)

        # 2. VISUALISATION COMPLÈTE (AVEC MENU DÉROULANT RAPIDE)
        st.subheader("📂 Dossiers Patients")
        
        df_mes_patients = recuperer_mes_patients(st.session_state.user_id)
        
        if not df_mes_patients.empty:
            liste_patients = df_mes_patients["Identifiant"].unique().tolist()
            patient_sel = st.selectbox("Sélectionner un dossier :", liste_patients)

            if patient_sel:
                st.markdown(f"### 👤 {patient_sel}")
                st.divider()

                # --- MENU DE SÉLECTION (RAPIDE - SANS BDI) ---
                type_outil = st.selectbox(
                    "🔍 Consulter un outil :",
                    [
                        "--- Choisir ---",
                        "📊 Vue d'ensemble (Dashboard)",
                        "📝 Registre Activités",
                        "🌙 Agenda Sommeil",
                        "🍷 Agenda Consos",
                        "🛑 Agenda Compulsions",
                        "🧩 Colonnes de Beck", 
                        "📉 PHQ-9 (Dépression)",
                        "😰 GAD-7 (Anxiété)",
                        "😴 ISI (Insomnie)",
                        "🤕 PEG (Douleur)",
                        "🧩 WSAS (Handicap)",
                        "🌿 WHO-5 (Bien-être)",
                        "💡 Résolution Problèmes",
                        "🧗 Exposition",
                        "⚖️ Balance Décisionnelle",
                        "🔍 Analyse SORC"
                    ]
                )

                # --- CHARGEMENT CONDITIONNEL ---
                if type_outil == "--- Choisir ---":
                    st.info("Sélectionnez un outil ci-dessus pour afficher les données.")

                elif type_outil == "📊 Vue d'ensemble (Dashboard)":
                    st.markdown("### Résumé rapide")
                    st.write("Sélectionnez une échelle spécifique pour voir l'historique complet.")

                elif type_outil == "🧩 Colonnes de Beck":
                    df = charger_donnees_specifiques("Beck", patient_sel)
                    if not df.empty:
                        st.dataframe(df.sort_values(by="Date", ascending=False), use_container_width=True, hide_index=True)
                    else: st.info("Aucune donnée.")

                elif type_outil == "📉 PHQ-9 (Dépression)":
                    df = charger_donnees_specifiques("PHQ9", patient_sel)
                    afficher_phq9(df, patient_sel)

                elif type_outil == "😰 GAD-7 (Anxiété)":
                    df = charger_donnees_specifiques("GAD7", patient_sel)
                    afficher_gad7(df, patient_sel)

                elif type_outil == "😴 ISI (Insomnie)":
                    df = charger_donnees_specifiques("ISI", patient_sel)
                    afficher_isi(df, patient_sel)

                elif type_outil == "🤕 PEG (Douleur)":
                    df = charger_donnees_specifiques("PEG", patient_sel)
                    afficher_peg(df, patient_sel)

                elif type_outil == "🧩 WSAS (Handicap)":
                    df = charger_donnees_specifiques("WSAS", patient_sel)
                    afficher_wsas(df, patient_sel)

                elif type_outil == "🌿 WHO-5 (Bien-être)":
                    df = charger_donnees_specifiques("WHO5", patient_sel)
                    afficher_who5(df, patient_sel)

                elif type_outil == "📝 Registre Activités":
                    df_act = charger_donnees_specifiques("Activites", patient_sel)
                    df_hum = charger_donnees_specifiques("Humeur", patient_sel)
                    if not df_act.empty or not df_hum.empty:
                        afficher_activites(df_act, df_hum, patient_sel)
                    else: st.info("Aucune activité.")

                elif type_outil == "🌙 Agenda Sommeil":
                    df = charger_donnees_specifiques("Sommeil", patient_sel)
                    if not df.empty: afficher_sommeil(df, patient_sel)
                    else: st.info("Pas de données sommeil.")

                elif type_outil == "🍷 Agenda Consos":
                    df = charger_donnees_specifiques("Addictions", patient_sel)
                    if not df.empty: afficher_conso(df, patient_sel)
                    else: st.info("Pas de conso.")

                elif type_outil == "🛑 Agenda Compulsions":
                    df = charger_donnees_specifiques("Compulsions", patient_sel)
                    if not df.empty: afficher_compulsions(df, patient_sel)
                    else: st.info("Pas de compulsions.")

                elif type_outil == "💡 Résolution Problèmes":
                    df = charger_donnees_specifiques("Résolution_Problème", patient_sel)
                    if not df.empty: st.dataframe(df, use_container_width=True)
                    else: st.info("Aucune donnée.")

                elif type_outil == "🧗 Exposition":
                    df = charger_donnees_specifiques("Exposition", patient_sel)
                    if not df.empty: st.dataframe(df, use_container_width=True)
                    else: st.info("Aucune donnée.")

                elif type_outil == "⚖️ Balance Décisionnelle":
                    df = charger_donnees_specifiques("Balance_Decisionnelle", patient_sel)
                    if not df.empty: st.dataframe(df, use_container_width=True)
                    else: st.info("Aucune donnée.")

                elif type_outil == "🔍 Analyse SORC":
                    df = charger_donnees_specifiques("SORC", patient_sel)
                    if not df.empty: st.dataframe(df, use_container_width=True)
                    else: st.info("Aucune donnée.")

        else:
            st.warning("Aucun patient trouvé.")

    # -----------------------------------------------------
    # B. ESPACE PATIENT (ARCHITECURE REVUE & CORRIGÉE)
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

        # =========================================================
        # SECTION 1 : AGENDAS (SUIVI QUOTIDIEN)
        # =========================================================
        st.markdown("### 📅 Mes Agendas (Quotidien)")
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

        # =========================================================
        # SECTION 2 : BOÎTE À OUTILS (EXERCICES)
        # =========================================================
        st.markdown("### 🛠️ Boîte à Outils (Exercices)")
        st.caption("Exercices pour travailler sur vos pensées et comportements.")
        
        c5, c6, c7 = st.columns(3)
        with c5:
            st.info("**Restructuration (Beck)**")
            st.page_link("pages/01_Colonnes_Beck.py", label="Lancer", icon="🧩")
            st.write("")
            st.info("**Analyse SORC**")
            st.page_link("pages/12_Analyse_SORC.py", label="Lancer", icon="🔍")
            
        with c6:
            st.info("**Résolution Problème**")
            st.page_link("pages/06_Resolution_Probleme.py", label="Lancer", icon="💡")
            st.write("")
            st.info("**Balance Décisionnelle**")
            st.page_link("pages/11_Balance_Decisionnelle.py", label="Lancer", icon="⚖️")

        with c7:
            st.info("**Exposition**")
            st.page_link("pages/09_Exposition.py", label="Lancer", icon="🧗")
            st.write("")
            st.info("**Relaxation**")
            st.page_link("pages/07_Relaxation.py", label="Lancer", icon="🧘")

        st.write("") 

        # =========================================================
        # SECTION 3 : MESURES & ÉCHELLES (NOUVEAU BLOC)
        # =========================================================
        st.markdown("### 📊 Mesures & Échelles (Hebdomadaire)")
        st.caption("Questionnaires pour suivre vos progrès (à faire selon demande du thérapeute).")
        
        # Ligne 1 : Humeur & Anxiété
        m1, m2, m3 = st.columns(3)
        with m1:
            st.success("**PHQ-9 (Dépression)**")
            st.page_link("pages/15_Echelle_PHQ9.py", label="Lancer", icon="📊")
        with m2:
            st.success("**GAD-7 (Anxiété)**")
            st.page_link("pages/16_Echelle_GAD7.py", label="Lancer", icon="📊")
        with m3:
            st.success("**WHO-5 (Bien-être)**")
            st.page_link("pages/20_Echelle_WHO5.py", label="Lancer", icon="📊")

        # Ligne 2 : Physique & Fonctionnel
        m4, m5, m6 = st.columns(3)
        with m4:
            st.success("**ISI (Insomnie)**")
            st.page_link("pages/17_Echelle_ISI.py", label="Lancer", icon="📊")
        with m5:
            st.success("**PEG (Douleur)**")
            st.page_link("pages/18_Echelle_PEG.py", label="Lancer", icon="📊")
        with m6:
            st.success("**WSAS (Impact)**")
            st.page_link("pages/19_Echelle_WSAS.py", label="Lancer", icon="📊")

        st.write("")

        # =========================================================
        # SECTION 4 : BILAN & EXPORT
        # =========================================================
        st.markdown("### 📜 Bilan Global")
        
        b1, b2, b3 = st.columns([1, 1, 2])
        with b1:
            st.page_link("pages/04_Historique.py", label="Voir mon Historique", icon="📜")
        with b2:
            st.page_link("pages/08_Export_Rapport.py", label="Exporter en PDF", icon="📤")
        
        st.divider()
        st.page_link("pages/03_Ressources.py", label="Consulter les Fiches & Ressources", icon="📚")


    # =========================================================
    # 4. SIDEBAR (MENU LATÉRAL) - RESTRUCTURÉ
    # =========================================================
    with st.sidebar:
        
        if st.session_state.user_type == "patient":
            display_id = st.session_state.user_id 
            try:
                from connect_db import load_data
                infos = load_data("Codes_Patients")
                if infos:
                    df_infos = pd.DataFrame(infos)
                    code_actuel = str(st.session_state.user_id).strip().upper()
                    match = df_infos[df_infos["Identifiant"].astype(str).str.strip().str.upper() == code_actuel]
                    if not match.empty:
                        col_id = "Identifiant" if "Identifiant" in df_infos.columns else "Commentaire"
                        display_id = match.iloc[0][col_id]
            except: pass
            
            st.write(f"👤 ID: **{display_id}**")
            st.divider()
            
            st.title("Navigation")
            st.page_link("streamlit_app.py", label="🏠 Accueil")
            
            st.caption("📅 Agendas")
            st.page_link("pages/10_Agenda_Sommeil.py", label="🌙 Sommeil")
            st.page_link("pages/05_Registre_Activites.py", label="📝 Activités")
            st.page_link("pages/13_Agenda_Consos.py", label="🍷 Consos")
            st.page_link("pages/14_Agenda_Compulsions.py", label="🛑 Compulsions")
            
            st.caption("🛠️ Outils")
            st.page_link("pages/01_Colonnes_Beck.py", label="🧩 Beck")
            st.page_link("pages/12_Analyse_SORC.py", label="🔍 SORC")
            st.page_link("pages/06_Resolution_Probleme.py", label="💡 Problèmes")
            st.page_link("pages/11_Balance_Decisionnelle.py", label="⚖️ Balance")
            st.page_link("pages/09_Exposition.py", label="🧗 Exposition")
            st.page_link("pages/07_Relaxation.py", label="🧘 Relaxation")
            
            st.caption("📊 Échelles")
            st.page_link("pages/15_Echelle_PHQ9.py", label="📊 PHQ-9")
            st.page_link("pages/16_Echelle_GAD7.py", label="📊 GAD-7")
            st.page_link("pages/20_Echelle_WHO5.py", label="📊 WHO-5")
            st.page_link("pages/17_Echelle_ISI.py", label="📊 ISI")
            st.page_link("pages/18_Echelle_PEG.py", label="📊 PEG")
            st.page_link("pages/19_Echelle_WSAS.py", label="📊 WSAS")
            
            st.caption("📜 Bilan")
            st.page_link("pages/04_Historique.py", label="Historique")
            st.page_link("pages/08_Export_Rapport.py", label="Export")

        else:
            st.title("Navigation")
            st.page_link("streamlit_app.py", label="🏠 Accueil")