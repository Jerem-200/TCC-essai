import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Analyse SORC", page_icon="🔍")

# ==============================================================================
# 0. SÉCURITÉ & IDENTIFICATION
# ==============================================================================

if "authentifie" not in st.session_state or not st.session_state.authentifie:
    st.warning("🔒 Accès restreint. Veuillez entrer votre Code Patient sur l'accueil.")
    st.page_link("streamlit_app.py", label="Retourner à l'accueil", icon="🏠")
    st.stop()

# 1. Récupération du Code Technique
CURRENT_USER_ID = st.session_state.get("user_id", "")
if not CURRENT_USER_ID:
    CURRENT_USER_ID = st.session_state.get("patient_id", "")

if not CURRENT_USER_ID:
    st.error("Erreur d'identité. Veuillez vous reconnecter.")
    st.stop()

# 2. Récupération de l'Identifiant Lisible (PAT-001)
USER_IDENTIFIER = CURRENT_USER_ID 
try:
    from connect_db import load_data
    infos = load_data("Codes_Patients")
    if infos:
        df_infos = pd.DataFrame(infos)
        code_clean = str(CURRENT_USER_ID).strip().upper()
        match = df_infos[df_infos["Code"].astype(str).str.strip().str.upper() == code_clean]
        if not match.empty:
            col_id = "Identifiant" if "Identifiant" in df_infos.columns else "Commentaire"
            val = str(match.iloc[0][col_id]).strip()
            if val: USER_IDENTIFIER = val
except: pass

# 3. Système Anti-Fuite
if "sorc_owner" not in st.session_state or st.session_state.sorc_owner != CURRENT_USER_ID:
    if "data_sorc" in st.session_state: del st.session_state.data_sorc
    st.session_state.sorc_owner = CURRENT_USER_ID

st.title("🔍 Analyse SORC")
st.info(f"Dossier : {USER_IDENTIFIER}")

# ==============================================================================
# 1. CHARGEMENT DES DONNÉES
# ==============================================================================
# Mise à jour des colonnes pour inclure l'heure et les deux types de conséquences
COLS_SORC = [
    "Patient", "Date", "Heure", "Situation", 
    "Pensées", "Émotions", "Intensité Emo", 
    "Douleur Active", "Desc Douleur", "Intensité Douleur",
    "Réponse", "Csg Court Terme", "Csg Long Terme"
]

if "data_sorc" not in st.session_state:
    df_init = pd.DataFrame(columns=COLS_SORC)
    try:
        from connect_db import load_data
        data_cloud = load_data("SORC")
        if data_cloud:
            df_cloud = pd.DataFrame(data_cloud)
            
            if "Patient" not in df_cloud.columns:
                df_cloud["Patient"] = str(USER_IDENTIFIER)
            
            # Remplissage intelligent
            for col in COLS_SORC:
                if col in df_cloud.columns:
                    df_init[col] = df_cloud[col]
            
            # Filtre Sécurité
            ids_ok = [str(CURRENT_USER_ID).strip(), str(USER_IDENTIFIER).strip()]
            df_init["Patient"] = df_init["Patient"].astype(str).str.strip()
            df_init = df_init[df_init["Patient"].isin(ids_ok)]
            
            # Nettoyage numérique
            for c in ["Intensité Emo", "Intensité Douleur"]:
                if c in df_init.columns:
                    df_init[c] = pd.to_numeric(df_init[c], errors='coerce').fillna(0).astype(int)

    except: pass
    st.session_state.data_sorc = df_init

# ==============================================================================
# ONGLETS
# ==============================================================================
tab1, tab2 = st.tabs(["📝 Nouvelle Analyse", "🗂️ Historique"])

# --- ONGLET 1 : SAISIE ---
with tab1:
    st.subheader("Décortiquer une situation")
    
    # --- INTERACTIVITÉ HORS FORMULAIRE ---
    # On met la case à cocher ici pour qu'elle recharge la page immédiatement
    has_pain = st.toggle("⚠️ Cette situation inclut-elle des douleurs chroniques ?", value=False)
    
    st.divider()

    with st.form("sorc_form"):
        # 1. S - SITUATION
        st.markdown("### 1. Situation (S)")
        c_date, c_heure, c_sit = st.columns([1, 1, 3])
        with c_date: 
            date_evt = st.date_input("Date", datetime.now())
        with c_heure:
            heure_evt = st.time_input("Heure", datetime.now())
        with c_sit: 
            situation = st.text_area("Que se passait-il ? (Où, quand, avec qui ?)", height=80, help="Décrivez les faits objectivement, comme une caméra.")
        
        st.divider()
        
        # 2. O - ORGANISME
        st.markdown("### 2. Organisme (O)")
        
        # A. Douleurs (Conditionnel, géré par le toggle au-dessus)
        desc_douleur = ""
        int_douleur = 0
        
        if has_pain:
            st.info("🩸 **Focus Douleur**")
            c_p1, c_p2 = st.columns([3, 1])
            with c_p1: desc_douleur = st.text_area("Description de la douleur / sensation physique :", height=80)
            with c_p2: 
                st.write("")
                int_douleur = st.slider("Intensité Douleur (0-10)", 0, 10, 5)
        
        # B. Pensées & Emotions
        pensees = st.text_area("💭 Pensées : Qu'est-ce qui vous a traversé l'esprit ?", height=80)
        
        c_emo, c_int = st.columns([3, 1])
        with c_emo: 
            # MODIFICATION : Text Area au lieu de Input pour avoir plus de place
            emotions = st.text_area("❤️ Émotions / Sensations (ex: Peur, Colère, Boule au ventre)", height=80)
        with c_int: 
            st.write("") # Petit espace pour aligner le slider
            int_emo = st.slider("Intensité Émotion", 0, 10, 7)
        
        st.divider()
        
        # 3. R - RÉPONSE
        st.markdown("### 3. Réponse (R)")
        reponse = st.text_area("🏃‍♂️ Comportement : Qu'avez-vous fait concrètement ?", height=80, placeholder="Ex: J'ai quitté la pièce, j'ai crié, j'ai pris un médicament, j'ai ruminé...")
        
        st.divider()
        
        # 4. C - CONSÉQUENCES
        st.markdown("### 4. Conséquences (C)")
        st.caption("Analysez l'impact de votre réaction.")
        
        c_court, c_long = st.columns(2)
        with c_court:
            csg_court = st.text_area("🟢 Court Terme (Soulagement immédiat ?)", height=100, placeholder="Ex: Baisse de l'anxiété, la douleur semble diminuer...")
        with c_long:
            csg_long = st.text_area("🔴 Long Terme (Le problème persiste ?)", height=100, placeholder="Ex: Je me sens coupable, la douleur revient plus fort, je suis isolé...")
        
        # VALIDATION
        st.write("")
        submitted = st.form_submit_button("Enregistrer l'analyse SORC", type="primary")
        
        if submitted:
            # Formatage
            heure_str = str(heure_evt)[:5]
            douleur_active_str = "Oui" if has_pain else "Non"
            
            new_row = {
                "Patient": USER_IDENTIFIER,
                "Date": str(date_evt),
                "Heure": heure_str,
                "Situation": situation,
                "Pensées": pensees,
                "Émotions": emotions,
                "Intensité Emo": int_emo,
                "Douleur Active": douleur_active_str,
                "Desc Douleur": desc_douleur if has_pain else "",
                "Intensité Douleur": int_douleur if has_pain else 0,
                "Réponse": reponse,
                "Csg Court Terme": csg_court,
                "Csg Long Terme": csg_long
            }
            
            # Sauvegarde Locale
            st.session_state.data_sorc = pd.concat([st.session_state.data_sorc, pd.DataFrame([new_row])], ignore_index=True)
            
            # Sauvegarde Cloud
            try:
                from connect_db import save_data
                values_list = [
                    USER_IDENTIFIER, str(date_evt), heure_str, situation, 
                    pensees, emotions, int_emo, 
                    douleur_active_str, desc_douleur, int_douleur,
                    reponse, csg_court, csg_long
                ]
                save_data("SORC", values_list)
                st.success("✅ Analyse SORC enregistrée avec succès !")
            except Exception as e:
                st.error(f"Erreur sauvegarde Cloud : {e}")

# --- ONGLET 2 : HISTORIQUE ---
with tab2:
    st.header("🗂️ Vos Analyses")
    
    if not st.session_state.data_sorc.empty:
        df_display = st.session_state.data_sorc.copy()
        
        # 1. Forçage affichage identifiant
        if "Patient" in df_display.columns:
            df_display["Patient"] = str(USER_IDENTIFIER)
            
        # 2. SÉCURISATION COLONNE HEURE (Le Correctif Anti-Crash)
        if "Heure" not in df_display.columns:
            df_display["Heure"] = "" # On crée la colonne vide si elle manque

        # 3. Tri par date et heure (Sécurisé)
        if "Date" in df_display.columns:
            # On trie par Date, et par Heure seulement si elle existe
            cols_tri = ["Date", "Heure"]
            df_display = df_display.sort_values(by=cols_tri, ascending=False)

        # --- 4. DÉFINITION DE L'ORDRE DES COLONNES (C'EST ICI LE CHANGEMENT) ---
        # On définit l'ordre exact que vous voulez voir à l'écran
        ordre_souhaite = [
            "Patient", "Date", "Heure", "Situation", 
            "Pensées", "Émotions", "Intensité Emo", 
            "Douleur Active", "Descr Douleur", "Intensité Douleur",
            "Réponse", "Csq Court Terme", "Csq Long Terme", 
            
        ]
        
        # On filtre pour ne garder que les colonnes qui existent vraiment (sécurité)
        cols_finales = [c for c in ordre_souhaite if c in df_display.columns]

        # 5. AFFICHAGE TABLEAU (Avec l'ordre imposé)
        st.dataframe(
            df_display[cols_finales], # <--- On applique l'ordre ici
            use_container_width=True, 
            hide_index=True,
            column_config={
                "Heure": st.column_config.TextColumn("Heure", width="small"), # Petit ajustement visuel
                "Situation": st.column_config.TextColumn("Situation", width="medium"),
                "Pensées": st.column_config.TextColumn("Pensées", width="medium"),
                "Réponse": st.column_config.TextColumn("Comportement", width="medium"),
                "Csg Court Terme": st.column_config.TextColumn("Csg Court", width="small"),
                "Csg Long Terme": st.column_config.TextColumn("Csg Long", width="small"),
                "Intensité Emo": st.column_config.NumberColumn("Int. Emo", format="%d/10"),
                "Intensité Douleur": st.column_config.NumberColumn("Douleur", format="%d/10"),
            }
        )
        
        st.divider()
        
        # Suppression
        with st.expander("🗑️ Supprimer une analyse"):
            # On gère l'affichage du sélecteur même si l'heure est vide
            opts = {}
            for i, r in df_display.iterrows():
                h_str = f" à {r['Heure']}" if r.get('Heure') else ""
                label = f"{r['Date']}{h_str} | {str(r['Situation'])[:30]}..."
                opts[label] = i

            choix = st.selectbox("Choisir l'entrée :", list(opts.keys()), index=None)
            
            if st.button("Supprimer définitivement") and choix:
                idx = opts[choix]
                row = df_display.loc[idx]
                
                try:
                    from connect_db import delete_data_flexible
                    delete_data_flexible("SORC", {
                        "Patient": USER_IDENTIFIER, 
                        "Date": str(row['Date']),
                        "Situation": str(row['Situation'])
                    })
                except: pass
                
                st.session_state.data_sorc = st.session_state.data_sorc.drop(idx).reset_index(drop=True)
                st.success("Supprimé !")
                st.rerun()
    else:
        st.info("Aucune analyse SORC pour le moment.")

st.divider()
st.page_link("streamlit_app.py", label="Retour à l'accueil", icon="🏠")