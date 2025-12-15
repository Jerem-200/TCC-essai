import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime
from visualisations import afficher_activites

st.set_page_config(page_title="Registre des Activités", page_icon="📝")

# ==============================================================================
# 0. SÉCURITÉ & NETTOYAGE (OBLIGATOIRE)
# ==============================================================================

# 1. Vérification auth
if "authentifie" not in st.session_state or not st.session_state.authentifie:
    st.warning("🔒 Accès restreint. Veuillez entrer votre Code Patient sur l'accueil.")
    st.page_link("streamlit_app.py", label="Retourner à l'accueil", icon="🏠")
    st.stop()

# 2. Récupération simple de l'ID
# Grâce à votre modification dans l'accueil, ceci contient DÉJÀ "PAT-001"
CURRENT_USER_ID = st.session_state.get("user_id", "")

if not CURRENT_USER_ID:
    st.error("Session expirée. Veuillez vous reconnecter.")
    st.stop()

# 3. Système Anti-Fuite (Nettoyage mémoire si changement de patient)
if "activite_owner" not in st.session_state or st.session_state.activite_owner != CURRENT_USER_ID:
    if "data_activites" in st.session_state: del st.session_state.data_activites
    if "data_humeur_jour" in st.session_state: del st.session_state.data_humeur_jour
    st.session_state.activite_owner = CURRENT_USER_ID

# D. LE VIGILE (PERMISSIONS) - NOUVEAU
CLE_PAGE = "activites" # <--- Changez ceci selon la page (ex: "activites", "conso"...)

if st.session_state.get("user_type") == "patient":
    try:
        from connect_db import load_data
        perms = load_data("Permissions")
        if perms:
            df_perm = pd.DataFrame(perms)
            # On cherche si le patient a des blocages
            row = df_perm[df_perm["Patient"] == CURRENT_USER_ID]
            if not row.empty:
                bloques = str(row.iloc[0]["Bloques"]).split(",")
                # Si la clé de la page est dans la liste des blocages
                if CLE_PAGE in [b.strip() for b in bloques]:
                    st.error("🔒 Cette fonctionnalité n'est pas activée dans votre programme.")
                    st.info("Voyez avec votre thérapeute si vous pensez qu'il s'agit d'une erreur.")
                    if st.button("Retour à l'accueil"):
                        st.switch_page("streamlit_app.py")
                    st.stop() # Arrêt immédiat
    except Exception as e:
        pass # En cas d'erreur technique (ex: pas de connexion), on laisse passer par défaut

st.title("📝 Registre des Activités")

# ==============================================================================
# 1. INITIALISATION ET CHARGEMENT
# ==============================================================================

# A. CHARGEMENT ACTIVITÉS
cols_act = ["Patient", "Date", "Heure", "Activité", "Plaisir (0-10)", "Maîtrise (0-10)", "Satisfaction (0-10)"]

if "data_activites" not in st.session_state:
    df_final_act = pd.DataFrame(columns=cols_act)
    try:
        from connect_db import load_data
        data_cloud = load_data("Activites")
        if data_cloud:
            df_cloud = pd.DataFrame(data_cloud)
            for col in cols_act:
                if col in df_cloud.columns:
                    df_final_act[col] = df_cloud[col]
                elif col.lower() in df_cloud.columns:
                    df_final_act[col] = df_cloud[col.lower()]
            
            # Nettoyage numérique
            cols_num = ["Plaisir (0-10)", "Maîtrise (0-10)", "Satisfaction (0-10)"]
            for c in cols_num:
                if c in df_final_act.columns:
                    df_final_act[c] = pd.to_numeric(df_final_act[c], errors='coerce')

            # --- FILTRE SÉCURITÉ ---
            if "Patient" in df_final_act.columns:
                df_final_act = df_final_act[df_final_act["Patient"].astype(str) == str(CURRENT_USER_ID)]
            else:
                df_final_act = pd.DataFrame(columns=cols_act)

    except: pass
    st.session_state.data_activites = df_final_act

# B. CHARGEMENT HUMEUR
cols_hum = ["Patient", "Date", "Humeur Globale (0-10)"]

if "data_humeur_jour" not in st.session_state:
    df_final_hum = pd.DataFrame(columns=cols_hum)
    try:
        from connect_db import load_data
        data_cloud_hum = load_data("Humeur")
        if data_cloud_hum:
            df_cloud_hum = pd.DataFrame(data_cloud_hum)
            for col in cols_hum:
                if col in df_cloud_hum.columns:
                    df_final_hum[col] = df_cloud_hum[col]
            
            # --- FILTRE SÉCURITÉ ---
            if "Patient" in df_final_hum.columns:
                df_final_hum = df_final_hum[df_final_hum["Patient"].astype(str) == str(CURRENT_USER_ID)]
            else:
                df_final_hum = pd.DataFrame(columns=cols_hum)
                
            if "Humeur Globale (0-10)" in df_final_hum.columns:
                df_final_hum["Humeur Globale (0-10)"] = pd.to_numeric(df_final_hum["Humeur Globale (0-10)"], errors='coerce')

    except: pass
    st.session_state.data_humeur_jour = df_final_hum

# C. MÉMOIRES TEMPORAIRES
if "memoire_h" not in st.session_state:
    st.session_state.memoire_h = datetime.now().hour
if "memoire_m" not in st.session_state:
    st.session_state.memoire_m = datetime.now().minute

# ==============================================================================
# ONGLETS
# ==============================================================================
tab1, tab2 = st.tabs(["📝 Saisie (Journal)", "📊 Résumé & Historique"])

# --- ONGLET 1 : SAISIE ---
with tab1:
    st.subheader("1. Ajouter une activité")
    with st.form("activity_form"):
        c_date, c_h, c_m = st.columns([2, 1, 1])
        with c_date: date_act = st.date_input("Date", datetime.now())
        with c_h: heure_h = st.number_input("Heure", 0, 23, st.session_state.memoire_h)
        with c_m: heure_m = st.number_input("Minute", 0, 59, st.session_state.memoire_m, step=5)

        activite_desc = st.text_input("Qu'avez-vous fait ?", placeholder="Ex: Petit déjeuner...")
        st.write("**Évaluation :**")
        c1, c2, c3 = st.columns(3)
        with c1: plaisir = st.slider("🎉 Plaisir", 0, 10, 5)
        with c2: maitrise = st.slider("💪 Maîtrise", 0, 10, 5)
        with c3: satisfaction = st.slider("🏆 Satisfaction", 0, 10, 5)

        if st.form_submit_button("Ajouter l'activité"):
            heure_str = f"{heure_h:02d}:{heure_m:02d}"
            
            # Sauvegarde Locale
            new_row = {
                "Patient": CURRENT_USER_ID,
                "Date": str(date_act), "Heure": heure_str, "Activité": activite_desc, 
                "Plaisir (0-10)": plaisir, "Maîtrise (0-10)": maitrise, "Satisfaction (0-10)": satisfaction
            }
            st.session_state.data_activites = pd.concat([st.session_state.data_activites, pd.DataFrame([new_row])], ignore_index=True)
            
            st.session_state.memoire_h = heure_h
            st.session_state.memoire_m = heure_m
            
            # Sauvegarde Cloud
            try:
                from connect_db import save_data
                save_data("Activites", [CURRENT_USER_ID, str(date_act), heure_str, activite_desc, plaisir, maitrise, satisfaction])
                st.success(f"Activité ajoutée à {heure_str} !")
            except Exception as e:
                st.warning(f"Sauvegardé en local seulement.")

    st.divider()

    # --- SUPPRESSION RAPIDE (ONGLET 1) ---
    with st.expander("🗑️ Supprimer une activité (Erreur de saisie)"):
        df_act = st.session_state.data_activites
        if not df_act.empty:
            df_act_sorted = df_act.sort_values(by=["Date", "Heure"], ascending=False)
            options_act = {f"{row['Date']} à {row['Heure']} - {row['Activité']}": i for i, row in df_act_sorted.iterrows()}
            choice_act = st.selectbox("Choisir l'activité :", list(options_act.keys()), key="del_t1")
            
            if st.button("Confirmer suppression", key="btn_del_t1") and choice_act:
                idx = options_act[choice_act]
                row = df_act_sorted.loc[idx]
                try:
                    from connect_db import delete_data_flexible
                    delete_data_flexible("Activites", {
                        "Patient": CURRENT_USER_ID, 
                        "Date": str(row['Date']), 
                        "Heure": str(row['Heure']), 
                        "Activité": row['Activité']
                    })
                except: pass
                st.session_state.data_activites = df_act.drop(idx).reset_index(drop=True)
                st.success("Activité supprimée !")
                st.rerun()

    # --- HUMEUR ---
    st.subheader("2. Bilan de la journée")
    with st.form("humeur_form"):
        date_humeur = st.date_input("Date du bilan", datetime.now())
        humeur_globale = st.slider("🌈 Humeur globale (0-10)", 0, 10, 5)
        
        if st.form_submit_button("Enregistrer l'humeur"):
            new_humeur = {"Patient": CURRENT_USER_ID, "Date": str(date_humeur), "Humeur Globale (0-10)": humeur_globale}
            st.session_state.data_humeur_jour = pd.concat([st.session_state.data_humeur_jour, pd.DataFrame([new_humeur])], ignore_index=True)
            try:
                from connect_db import save_data
                save_data("Humeur", [CURRENT_USER_ID, str(date_humeur), humeur_globale])
                st.success("Humeur enregistrée !")
            except: pass

    # --- SUPPRESSION HUMEUR (ONGLET 1) ---
    st.write("")
    with st.expander("🗑️ Supprimer un relevé d'humeur"):
        df_hum = st.session_state.data_humeur_jour
        if not df_hum.empty:
            df_hum_s = df_hum.sort_values("Date", ascending=False)
            opts_h = {f"{row['Date']} - Note: {row['Humeur Globale (0-10)']}/10": i for i, row in df_hum_s.iterrows()}
            ch_h = st.selectbox("Choisir :", list(opts_h.keys()), key="del_hum_t1")
            
            if st.button("Supprimer", key="btn_del_hum_t1") and ch_h:
                idx = opts_h[ch_h]
                r = df_hum_s.loc[idx]
                try:
                    from connect_db import delete_data_flexible
                    delete_data_flexible("Humeur", {"Patient": CURRENT_USER_ID, "Date": str(r['Date'])})
                except: pass
                st.session_state.data_humeur_jour = df_hum.drop(idx).reset_index(drop=True)
                st.success("Supprimé !")
                st.rerun()

# --- ONGLET 2 : HISTORIQUE ---
with tab2:
    st.header("Historique & Analyse")
    
    # 1. APPEL À LA FONCTION CENTRALISÉE
    # C'est ici que ça change tout : une seule ligne pour tout afficher !
    afficher_activites(
        st.session_state.data_activites, 
        st.session_state.data_humeur_jour, 
        CURRENT_USER_ID
    )

    # 2. GESTION (SUPPRESSION) 
    # On garde les fonctions de suppression ici car c'est de l'édition
    st.divider()
    with st.expander("🗑️ Gérer / Supprimer une entrée depuis l'historique"):
        
        # A. Suppression Activité
        df_hist_del = st.session_state.data_activites.sort_values(by=["Date", "Heure"], ascending=False)
        if not df_hist_del.empty:
            opts_del = {}
            for i, row in df_hist_del.iterrows():
                lbl = f"📅 {row['Date']} ({row['Heure']}) | {row['Activité']} | P:{row.get('Plaisir (0-10)',0)} M:{row.get('Maîtrise (0-10)',0)}"
                opts_del[lbl] = i
            
            choix_del = st.selectbox("Supprimer Activité :", list(opts_del.keys()), index=None, key="sel_del_tab2")
            if st.button("Confirmer suppression activité", key="btn_del_tab2") and choix_del:
                idx = opts_del[choix_del]
                row_to_del = df_hist_del.loc[idx]
                try:
                    from connect_db import delete_data_flexible
                    delete_data_flexible("Activites", {
                        "Patient": CURRENT_USER_ID, 
                        "Date": str(row_to_del['Date']),
                        "Heure": str(row_to_del['Heure']),
                        "Activité": str(row_to_del['Activité'])
                    })
                except: pass
                st.session_state.data_activites = st.session_state.data_activites.drop(idx).reset_index(drop=True)
                st.success("Effacé !")
                st.rerun()

        st.write("---")

        # B. Suppression Humeur
        df_hum_del = st.session_state.data_humeur_jour.sort_values(by="Date", ascending=False)
        if not df_hum_del.empty:
            opts_hum = {}
            for i, row in df_hum_del.iterrows():
                lbl = f"📅 {row['Date']} | Note : {row['Humeur Globale (0-10)']}/10"
                opts_hum[lbl] = i
            
            choix_hum = st.selectbox("Supprimer Humeur :", list(opts_hum.keys()), index=None, key="sel_del_hum_tab2")
            if st.button("Confirmer suppression humeur", key="btn_del_hum_tab2") and choix_hum:
                idx = opts_hum[choix_hum]
                row_to_del = df_hum_del.loc[idx]
                try:
                    from connect_db import delete_data_flexible
                    delete_data_flexible("Humeur", {
                        "Patient": CURRENT_USER_ID, 
                        "Date": str(row_to_del['Date'])
                    })
                except: pass
                st.session_state.data_humeur_jour = st.session_state.data_humeur_jour.drop(idx).reset_index(drop=True)
                st.success("Effacé !")
                st.rerun()

st.divider()
st.page_link("streamlit_app.py", label="Retour à l'accueil", icon="🏠")