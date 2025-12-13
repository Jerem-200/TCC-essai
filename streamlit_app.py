import streamlit as st
import pandas as pd
import altair as alt
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

        # 2. VISUALISATION COMPLÈTE
        st.subheader("📂 Dossiers Patients")
        
        df_mes_patients = recuperer_mes_patients(st.session_state.user_id)
        
        if not df_mes_patients.empty:
            liste_patients = df_mes_patients["Identifiant"].unique().tolist()
            patient_sel = st.selectbox("Sélectionner un dossier :", liste_patients)

            if patient_sel:
                st.markdown(f"### 👤 {patient_sel}")
                
                # --- LES 10 ONGLETS ---
                # On utilise des noms courts pour que ça rentre sur l'écran
                t1, t2, t3, t4, t5, t6, t7, t8, t9, t10 = st.tabs([
                    "🧩 Beck", "📉 BDI", "📝 Activités", "💡 Problèmes", "🧗 Expo", 
                    "🌙 Sommeil", "⚖️ Balance", "🔍 SORC", "🍷 Conso", "🛑 Compulsions"
                ])
                
                # 1. BECK
                with t1:
                    df = charger_donnees_specifiques("Beck", patient_sel)
                    if not df.empty:
                        st.dataframe(df.sort_values(by="Date", ascending=False), use_container_width=True, hide_index=True)
                    else: st.info("Aucune colonne de Beck.")

                # 2. BDI (Avec Graphique)
                with t2:
                    df = charger_donnees_specifiques("BDI", patient_sel)
                    if not df.empty:
                        # On suppose une colonne 'Score' ou 'Total' et 'Date'
                        cols = df.columns
                        col_score = next((c for c in cols if "score" in c.lower() or "total" in c.lower()), None)
                        
                        if col_score and "Date" in df.columns:
                            df["Date"] = pd.to_datetime(df["Date"], errors='coerce')
                            df[col_score] = pd.to_numeric(df[col_score], errors='coerce')
                            df = df.dropna(subset=["Date", col_score]).sort_values("Date")
                            
                            c_bdi = alt.Chart(df).mark_line(point=True, color="red").encode(
                                x=alt.X('Date:T', axis=alt.Axis(format='%d/%m')),
                                y=alt.Y(f'{col_score}:Q', title='Score Depression'),
                                tooltip=['Date', col_score]
                            ).interactive()
                            st.altair_chart(c_bdi, use_container_width=True)
                            st.dataframe(df, use_container_width=True)
                        else:
                            st.dataframe(df, use_container_width=True)
                    else: st.info("Aucun test BDI.")

                # 3. ACTIVITÉS (Avec Graphiques)
                with t3:
                    df = charger_donnees_specifiques("Activites", patient_sel)
                    if not df.empty:
                        df["Date_Obj"] = pd.to_datetime(df["Date"], errors='coerce')
                        cols_num = ["Plaisir (0-10)", "Maîtrise (0-10)", "Satisfaction (0-10)"]
                        for c in cols_num: 
                            if c in df.columns: df[c] = pd.to_numeric(df[c], errors='coerce')
                        
                        # Graphique d'évolution
                        df_evol = df.groupby("Date_Obj")[cols_num].mean().reset_index().melt('Date_Obj', var_name='Type', value_name='Note')
                        chart = alt.Chart(df_evol).mark_line(point=True).encode(
                            x='Date_Obj:T', y='Note:Q', color='Type:N', tooltip=['Date_Obj', 'Type', 'Note']
                        ).interactive()
                        st.altair_chart(chart, use_container_width=True)
                        st.dataframe(df.sort_values("Date", ascending=False), use_container_width=True)
                    else: st.info("Aucune activité.")

                # 4. PROBLÈMES
                with t4:
                    df = charger_donnees_specifiques("Résolution_Problème", patient_sel)
                    if not df.empty:
                        st.dataframe(df.sort_values("Date", ascending=False), use_container_width=True, hide_index=True)
                    else: st.info("Aucun problème traité.")

                # 5. EXPOSITION
                with t5:
                    df = charger_donnees_specifiques("Exposition", patient_sel)
                    if not df.empty:
                        st.dataframe(df.sort_values("Date", ascending=False), use_container_width=True, hide_index=True)
                    else: st.info("Aucune exposition.")

                # 6. SOMMEIL (Complet)
                with t6:
                    df = charger_donnees_specifiques("Sommeil", patient_sel)
                    if not df.empty:
                        df["Date_Obj"] = pd.to_datetime(df["Date"], errors='coerce')
                        if "Efficacité" in df.columns:
                            df["Efficacité_Num"] = pd.to_numeric(df["Efficacité"].astype(str).str.replace('%',''), errors='coerce')
                            
                            c_eff = alt.Chart(df).mark_line(point=True, color="#3498db").encode(
                                x='Date_Obj:T', y=alt.Y('Efficacité_Num:Q', title='Efficacité %'), tooltip=['Date', 'Efficacité']
                            ).interactive()
                            st.altair_chart(c_eff, use_container_width=True)
                        st.dataframe(df.sort_values("Date", ascending=False), use_container_width=True)
                    else: st.info("Aucune donnée sommeil.")

                # 7. BALANCE
                with t7:
                    df = charger_donnees_specifiques("Balance_Decisionnelle", patient_sel)
                    if not df.empty:
                        st.dataframe(df, use_container_width=True, hide_index=True)
                    else: st.info("Aucune balance.")

                # 8. SORC
                with t8:
                    df = charger_donnees_specifiques("SORC", patient_sel)
                    if not df.empty:
                        st.dataframe(df.sort_values("Date", ascending=False), use_container_width=True, hide_index=True)
                    else: st.info("Aucune analyse SORC.")

                # 9. CONSO (Graphique)
                with t9:
                    df = charger_donnees_specifiques("Addictions", patient_sel)
                    if not df.empty:
                        try:
                            df['Full_Date'] = pd.to_datetime(df['Date'].astype(str) + ' ' + df['Heure'].astype(str), errors='coerce')
                        except: df['Full_Date'] = pd.to_datetime(df['Date'], errors='coerce')
                        
                        df_conso = df[df["Type"].astype(str).str.contains("CONSOMMÉ", na=False)]
                        if not df_conso.empty and "Quantité" in df_conso.columns:
                            df_conso["Quantité"] = pd.to_numeric(df_conso["Quantité"], errors='coerce')
                            c_conso = alt.Chart(df_conso).mark_bar(color="#e74c3c").encode(
                                x='Full_Date:T', y='Quantité:Q', tooltip=['Date', 'Substance', 'Quantité', 'Unité']
                            ).interactive()
                            st.altair_chart(c_conso, use_container_width=True)
                        st.dataframe(df.sort_values("Date", ascending=False), use_container_width=True)
                    else: st.info("Aucune consommation.")

                # 10. COMPULSIONS (Graphique)
                with t10:
                    df = charger_donnees_specifiques("Compulsions", patient_sel)
                    if not df.empty:
                        df["Date_Obj"] = pd.to_datetime(df["Date"], errors='coerce')
                        df["Répétitions"] = pd.to_numeric(df["Répétitions"], errors='coerce')
                        
                        base = alt.Chart(df).encode(x='Date_Obj:T')
                        l_rep = base.mark_line(color="red").encode(y='Répétitions:Q')
                        st.altair_chart(l_rep.interactive(), use_container_width=True)
                        st.dataframe(df.sort_values("Date", ascending=False), use_container_width=True)
                    else: st.info("Aucune compulsion.")

        else:
            st.warning("Aucun patient trouvé.")

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