import streamlit as st
import pandas as pd
from datetime import datetime, time

st.set_page_config(page_title="Agenda du Sommeil", page_icon="🌙")

# --- VIGILE DE SÉCURITÉ & NETTOYAGE MÉMOIRE ---
if "authentifie" not in st.session_state or not st.session_state.authentifie:
    st.warning("🔒 Accès restreint. Veuillez entrer votre Code Patient sur l'accueil.")
    st.page_link("streamlit_app.py", label="Retourner à l'accueil", icon="🏠")
    st.stop()

# 1. Récupération sécurisée de l'ID (corrige l'erreur AttributeError)
CURRENT_USER_ID = st.session_state.get("patient_id", "")

# 2. SYSTÈME ANTI-FUITE DE DONNÉES (Le correctif "Jérémy")
# On vérifie si les données en mémoire appartiennent bien à la personne connectée
if "sommeil_owner" not in st.session_state or st.session_state.sommeil_owner != CURRENT_USER_ID:
    # Si l'utilisateur a changé, on supprime immédiatement les données de l'ancien utilisateur
    if "data_sommeil" in st.session_state:
        del st.session_state.data_sommeil
    # On marque le nouveau propriétaire
    st.session_state.sommeil_owner = CURRENT_USER_ID

st.title("🌙 Agenda du Sommeil")
st.info("Remplissez ce formulaire chaque matin pour analyser la qualité de votre sommeil.")

# ==============================================================================
# 1. INITIALISATION ET CHARGEMENT CLOUD
# ==============================================================================
if "data_sommeil" not in st.session_state:
    # A. Vos en-têtes exactes
    cols_sommeil = [
        "Patient", "Date", "Sieste", 
        "Sport", "Cafeine", "Alcool", "Medic_Sommeil",
        "Heure Coucher", "Latence", "Eveil", 
        "Heure Lever", "TTE", "TAL", "TTS", "Forme", "Qualité", "Efficacité"
    ]
    
    # B. DataFrame vide par défaut
    df_final = pd.DataFrame(columns=cols_sommeil)
    
    # C. Chargement des données
    try:
        from connect_db import load_data
        data_cloud = load_data("Sommeil")
        
        if data_cloud:
            df_cloud = pd.DataFrame(data_cloud)
            
            # --- CORRECTION ICI : On force la création de la colonne Patient si elle manque ---
            if "Patient" not in df_cloud.columns:
                # Si l'Excel n'a pas de colonne Patient, on suppose que TOUTES les lignes
                # appartiennent à l'utilisateur actuel (Mode monoposte / ancien fichier)
                # OU on laisse vide pour le moment et on remplira à l'affichage
                df_cloud["Patient"] = str(CURRENT_USER_ID)
            
            # D. Remplissage intelligent
            for col in cols_sommeil:
                if col in df_cloud.columns:
                    df_final[col] = df_cloud[col]
                elif col == "Eveil" and "Eveil Nocturne" in df_cloud.columns:
                    df_final[col] = df_cloud["Eveil Nocturne"]

            # =================================================================
            # 🛑 FILTRAGE SÉCURITÉ (Réparé)
            # =================================================================
            # Maintenant que la colonne Patient existe forcément (créée ou importée)
            # On nettoie les espaces pour être sûr que ça matche
            df_final["Patient"] = df_final["Patient"].astype(str).str.strip()
            user_clean = str(CURRENT_USER_ID).strip()
            
            # On ne garde que les lignes de l'utilisateur
            df_final = df_final[df_final["Patient"] == user_clean]
            # =================================================================

    except Exception as e:
        # En cas d'erreur (ex: fichier vide), on ne fait rien
        pass

    # E. Sauvegarde en mémoire
    st.session_state.data_sommeil = df_final

# C. INITIALISATION DES UNITÉS
if "sommeil_units" not in st.session_state:
    st.session_state.sommeil_units = ["Verres", "Tasses", "mg", "cp", "ml", "Pintes"]

# --- FONCTIONS DE CALCUL ---
def calculer_duree_minutes(heure_debut, heure_fin):
    h_deb = heure_debut.hour * 60 + heure_debut.minute
    h_fin = heure_fin.hour * 60 + heure_fin.minute
    if h_fin < h_deb: return (24 * 60 - h_deb) + h_fin
    return h_fin - h_deb

def format_minutes_en_h_m(minutes):
    h = int(minutes // 60)
    m = int(minutes % 60)
    return f"{h}h{m:02d}"

# ==============================================================================
# ONGLETS
# ==============================================================================
tab1, tab2 = st.tabs(["📝 Saisie du jour", "📊 Analyse & Moyennes"])

# --- ONGLET 1 : FORMULAIRE DESIGN ---
with tab1:
    st.subheader("📝 Saisie de la nuit dernière")

    # --- LE FORMULAIRE VISUEL ---
    with st.form("form_sommeil"):
        # DATE
        c_date, _ = st.columns([1, 2])
        with c_date:
            date_nuit = st.date_input("Date du lever (Ce matin)", datetime.now())

        st.divider()
        
        # Listes horaires
        liste_heures_activites = ["Non"] + [f"{h}h{m:02d}" for h in range(24) for m in (0, 15, 30, 45)]
        liste_durees = ["15 min", "30 min", "45 min", "1h00", "1h30", "2h00", "3h+"]

        # 1. SIESTE & SPORT
        st.markdown("### 🌞 Activités Physiques & Repos")
        
        col_s1, col_s2, col_s3 = st.columns([2, 1, 1])
        with col_s1:
            h_sieste = st.selectbox("💤 Sieste (Heure début)", liste_heures_activites)
        with col_s2:
            d_sieste = st.selectbox("Durée", liste_durees, key="d_sieste")
        with col_s3: st.empty()

        col_sp1, col_sp2, col_sp3 = st.columns([2, 1, 1])
        with col_sp1:
            h_sport = st.selectbox("🏋️ Sport (Heure début)", liste_heures_activites)
        with col_sp2:
            d_sport = st.selectbox("Durée", liste_durees, key="d_sport")
        with col_sp3: st.empty()

        st.write("") 
        
        # 2. CONSOMMATIONS (Fonction helper pour le design)
        st.markdown("### 🍷 Consommations (Dernière prise)")
        
        def ligne_conso(label, icon, key_prefix, default_idx=0):
            c_h, c_qty, c_u = st.columns([2, 1, 1])
            with c_h:
                heure = st.selectbox(f"{icon} {label} (Heure)", liste_heures_activites, key=f"{key_prefix}_h")
            with c_qty:
                qty = st.number_input("Qté", min_value=0.0, step=0.5, key=f"{key_prefix}_q")
            with c_u:
                # Sécurité index
                safe_idx = default_idx if default_idx < len(st.session_state.sommeil_units) else 0
                unit = st.selectbox("Unité", st.session_state.sommeil_units, index=safe_idx, key=f"{key_prefix}_u")
            return heure, qty, unit

        h_cafe, q_cafe, u_cafe = ligne_conso("Caféine", "☕", "cafe", 0) 
        h_alcool, q_alcool, u_alcool = ligne_conso("Alcool", "🍷", "alcool", 1) 
        h_med, q_med, u_med = ligne_conso("Médicament", "💊", "med", 2) 

        st.divider()

        # 3. LA NUIT
        st.markdown("### 🌙 Votre Nuit")
        
        col_coucher, col_lever = st.columns(2)
        with col_coucher:
            st.info("**Au Coucher**")
            h_coucher = st.time_input("Heure au lit", time(23, 0))
            latence = st.number_input("Latence (min)", 0, 300, 15, step=5, help="Temps pour s'endormir")
        
        with col_lever:
            st.success("**Au Lever**")
            h_lever = st.time_input("Heure de sortie du lit", time(7, 0))
            eveil_nocturne = st.number_input("Éveil nocturne (min)", 0, 300, 0, step=5)

        st.write("")
        
        # 4. RESSENTI
        st.markdown("### ⭐ Bilan")
        c_forme, c_qualite = st.columns(2)
        with c_forme:
            forme = st.slider("🔋 Forme (1=HS, 5=Top)", 1, 5, 3)
        with c_qualite:
            qualite = st.slider("✨ Qualité Sommeil (1=Mauvais, 5=Top)", 1, 5, 3)

        st.write("")
        
        # BOUTON
        _, c_btn, _ = st.columns([1, 2, 1])
        with c_btn:
            submitted = st.form_submit_button("💾 Enregistrer ma nuit", use_container_width=True, type="primary")

        if submitted:
            # FORMATAGE
            sieste_final = "Non" if h_sieste == "Non" else f"{h_sieste} ({d_sieste})"
            sport_final = "Non" if h_sport == "Non" else f"{h_sport} ({d_sport})"
            cafe_final = "Non" if h_cafe == "Non" else f"{h_cafe} - {q_cafe} {u_cafe}"
            alcool_final = "Non" if h_alcool == "Non" else f"{h_alcool} - {q_alcool} {u_alcool}"
            med_final = "Non" if h_med == "Non" else f"{h_med} - {q_med} {u_med}"

            # CALCULS
            tal_minutes = calculer_duree_minutes(h_coucher, h_lever)
            tte_minutes = latence + eveil_nocturne
            tts_minutes = tal_minutes - tte_minutes
            efficacite = round((tts_minutes / tal_minutes) * 100, 1) if tal_minutes > 0 else 0

            st.success("✅ Données enregistrées !")
            
            # KPI
            res1, res2, res3, res4 = st.columns(4)
            res1.metric("Au lit", format_minutes_en_h_m(tal_minutes))
            res2.metric("Sommeil", format_minutes_en_h_m(tts_minutes))
            res3.metric("Éveil", format_minutes_en_h_m(tte_minutes))
            res4.metric("Efficacité", f"{efficacite} %")

            # SAUVEGARDE
            new_row = {
                "Patient": CURRENT_USER_ID,  # <--- IL MANQUAIT CETTE LIGNE !
                "Date": str(date_nuit),
                "Sieste": sieste_final, "Sport": sport_final, 
                "Cafeine": cafe_final, "Alcool": alcool_final, "Medic_Sommeil": med_final,
                "Heure Coucher": str(h_coucher)[:5], "Heure Lever": str(h_lever)[:5],
                "Latence": latence, "Eveil": eveil_nocturne,
                "TTE": format_minutes_en_h_m(tte_minutes),
                "TAL": format_minutes_en_h_m(tal_minutes),
                "TTS": format_minutes_en_h_m(tts_minutes),
                "Forme": forme, "Qualité": qualite, "Efficacité": efficacite
            }
            st.session_state.data_sommeil = pd.concat([st.session_state.data_sommeil, pd.DataFrame([new_row])], ignore_index=True)
            
            # CLOUD
            try:
                from connect_db import save_data
                # On utilise CURRENT_USER_ID (défini tout en haut du fichier)
                save_data("Sommeil", [
                    CURRENT_USER_ID,  # <--- C'est ici qu'on met l'ID sécurisé
                    str(date_nuit), 
                    sieste_final, sport_final, cafe_final, alcool_final, med_final,
                    str(h_coucher)[:5], latence, eveil_nocturne, str(h_lever)[:5],
                    format_minutes_en_h_m(tte_minutes),
                    format_minutes_en_h_m(tal_minutes),
                    format_minutes_en_h_m(tts_minutes),
                    forme, qualite, f"{efficacite}%"
                ])
            except Exception as e:
                st.error(f"Erreur Cloud : {e}")

    # --- GESTIONNAIRE D'UNITÉS (Expander discret) ---
    with st.expander("⚙️ Gérer les unités (Ajouter/Supprimer)"):
        c_add, c_del = st.columns(2)
        with c_add:
            new_u = st.text_input("Nouvelle unité :", placeholder="ex: Bol", label_visibility="collapsed")
            if st.button("➕ Ajouter", key="btn_add_u"):
                if new_u and new_u not in st.session_state.sommeil_units:
                    st.session_state.sommeil_units.append(new_u)
                    st.success(f"Ajouté !")
                    st.rerun()
        with c_del:
            if st.session_state.sommeil_units:
                del_u = st.selectbox("Supprimer :", st.session_state.sommeil_units, label_visibility="collapsed")
                if st.button("🗑️ Supprimer", key="btn_del_u"):
                    st.session_state.sommeil_units.remove(del_u)
                    st.rerun()

# ==============================================================================
# ONGLET 2 : ANALYSE (HISTORIQUE)
# ==============================================================================
with tab2:
    st.header("📊 Tableau de bord")
    
    # On vérifie s'il y a des données
    if not st.session_state.data_sommeil.empty:
        
        # 1. On travaille sur une copie pour l'affichage
        df_display = st.session_state.data_sommeil.copy()
        
        # 2. On récupère l'identifiant "joli" (PAT-001)
        identifiant_final = CURRENT_USER_ID # Par défaut
        
        try:
            from connect_db import load_data
            infos = load_data("Codes_Patients")
            if infos:
                df_i = pd.DataFrame(infos)
                # Recherche insensible à la casse/espaces
                match = df_i[df_i["Code"].astype(str).str.strip() == str(CURRENT_USER_ID).strip()]
                if not match.empty:
                    col_id = "Identifiant" if "Identifiant" in df_i.columns else "Commentaire"
                    identifiant_final = match.iloc[0][col_id]
        except: pass

        # 3. FORÇAGE VISUEL (Le Correctif)
        # Même si la colonne est vide dans Excel, on la remplit ici pour l'affichage
        df_display["Patient"] = str(identifiant_final)

        # 4. AFFICHAGE
        st.dataframe(
            df_display, 
            use_container_width=True, 
            hide_index=True # Supprime la colonne de chiffres 0,1,2...
        )
        
        st.divider()
        
        # 5. GRAPHIQUES (Suite du code...)
        df = st.session_state.data_sommeil.copy()
        
        try:
            # Conversion numérique pour les moyennes
            df["Efficacité"] = pd.to_numeric(df["Efficacité"].astype(str).str.replace('%', ''), errors='coerce')
            df["Forme"] = pd.to_numeric(df["Forme"], errors='coerce')
            df["Qualité"] = pd.to_numeric(df["Qualité"], errors='coerce')
            
            c1, c2, c3 = st.columns(3)
            if pd.notna(df["Efficacité"].mean()): 
                c1.metric("Efficacité Moyenne", f"{df['Efficacité'].mean():.1f} %")
            if pd.notna(df["Forme"].mean()): 
                c2.metric("Forme Moyenne", f"{df['Forme'].mean():.1f} / 5")
            if pd.notna(df["Qualité"].mean()): 
                c3.metric("Qualité Moyenne", f"{df['Qualité'].mean():.1f} / 10")
        except: pass

        st.write("### Évolution")
        import altair as alt
        
        # Préparation graphique
        df_chart = df.copy()
        df_chart["Date"] = pd.to_datetime(df_chart["Date"], errors='coerce')
        df_chart = df_chart.dropna(subset=["Date", "Efficacité"])
        
        chart = alt.Chart(df_chart).mark_line(point=True).encode(
            x=alt.X('Date:T', title='Date', axis=alt.Axis(format='%d/%m')),
            y=alt.Y('Efficacité:Q', title='Efficacité (%)', scale=alt.Scale(domain=[0, 100])),
            tooltip=['Date', 'Efficacité', 'Forme', 'Qualité']
        ).interactive()
        
        st.altair_chart(chart, use_container_width=True)

        # 6. SUPPRESSION
        st.divider()
        with st.expander("🗑️ Supprimer une entrée"):
            df_h = df.sort_values(by="Date", ascending=False)
            # Création d'une liste lisible pour le menu déroulant
            options_history = {
                f"📅 {row['Date']} | Efficacité: {row.get('Efficacité', '?')}%": i 
                for i, row in df_h.iterrows()
            }
            choix = st.selectbox("Sélectionnez la nuit à supprimer :", list(options_history.keys()), index=None)
            
            if st.button("Confirmer la suppression", key="btn_del"):
                if choix:
                    idx = options_history[choix]
                    row_to_del = df_h.loc[idx]
                    
                    try:
                        from connect_db import delete_data_flexible
                        # Suppression dans le Cloud avec l'ID sécurisé
                        delete_data_flexible("Sommeil", {
                            "Patient": CURRENT_USER_ID, 
                            "Date": str(row_to_del['Date'])
                        })
                    except: pass
                    
                    # Suppression Locale
                    st.session_state.data_sommeil = st.session_state.data_sommeil.drop(idx).reset_index(drop=True)
                    st.success("Entrée supprimée !")
                    st.rerun()
                else:
                    st.warning("Veuillez sélectionner une ligne.")
    else:
        st.info("Aucune donnée de sommeil enregistrée pour ce patient.")

st.divider()
st.page_link("streamlit_app.py", label="Retour à l'accueil", icon="🏠")