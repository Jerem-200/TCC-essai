import streamlit as st
import pandas as pd
from datetime import datetime, time

st.set_page_config(page_title="Agenda du Sommeil", page_icon="🌙")

# ==============================================================================
# 0. SÉCURITÉ & NETTOYAGE
# ==============================================================================

if "authentifie" not in st.session_state or not st.session_state.authentifie:
    st.warning("🔒 Accès restreint. Veuillez entrer votre Code Patient sur l'accueil.")
    st.page_link("streamlit_app.py", label="Retourner à l'accueil", icon="🏠")
    st.stop()

# 1. Récupération sécurisée de l'ID
CURRENT_USER_ID = st.session_state.get("user_id", "")
if not CURRENT_USER_ID:
    CURRENT_USER_ID = st.session_state.get("patient_id", "")
    # --- RÉCUPÉRATION DE L'IDENTIFIANT LISIBLE (PAT-001) ---
# On en a besoin pour sauvegarder proprement dans le Sheet
USER_IDENTIFIER = CURRENT_USER_ID # Par défaut, on garde le code
try:
    from connect_db import load_data
    infos = load_data("Codes_Patients")
    if infos:
        df_infos = pd.DataFrame(infos)
        # Recherche insensible à la casse
        code_clean = str(CURRENT_USER_ID).strip().upper()
        match = df_infos[df_infos["Code"].astype(str).str.strip().str.upper() == code_clean]
        
        if not match.empty:
            col_id = "Identifiant" if "Identifiant" in df_infos.columns else "Commentaire"
            USER_IDENTIFIER = str(match.iloc[0][col_id]).strip()
except:
    pass
# -------------------------------------------------------

if not CURRENT_USER_ID:
    st.error("Erreur d'identité. Veuillez vous reconnecter.")
    st.stop()

# 2. Système Anti-Fuite
if "sommeil_owner" not in st.session_state or st.session_state.sommeil_owner != CURRENT_USER_ID:
    if "data_sommeil" in st.session_state: del st.session_state.data_sommeil
    st.session_state.sommeil_owner = CURRENT_USER_ID

st.title("🌙 Agenda du Sommeil")
st.info("Remplissez ce formulaire chaque matin pour analyser la qualité de votre sommeil.")

# ==============================================================================
# 1. INITIALISATION ET CHARGEMENT CLOUD (CORRIGÉ)
# ==============================================================================
if "data_sommeil" not in st.session_state:
    cols_sommeil = [
        "Patient", "Date", "Sieste", 
        "Sport", "Cafeine", "Alcool", "Medic_Sommeil",
        "Heure Coucher", "Latence", "Eveil", 
        "Heure Lever", "TTE", "TAL", "TTS", "Forme", "Qualité", "Efficacité"
    ]
    df_final = pd.DataFrame(columns=cols_sommeil)
    
    try:
        from connect_db import load_data
        data_cloud = load_data("Sommeil")
        if data_cloud:
            df_cloud = pd.DataFrame(data_cloud)
            
            # --- CORRECTION CRUCIALE : Si colonne Patient manquante, on l'invente ---
            if "Patient" not in df_cloud.columns:
                df_cloud["Patient"] = str(CURRENT_USER_ID)
            
            # Remplissage intelligent
            for col in cols_sommeil:
                if col in df_cloud.columns:
                    df_final[col] = df_cloud[col]
                elif col == "Eveil" and "Eveil Nocturne" in df_cloud.columns:
                    df_final[col] = df_cloud["Eveil Nocturne"]

            # =================================================================
            # 🛑 FILTRAGE SÉCURITÉ (MISE À JOUR)
            # =================================================================
            # On accepte les lignes signées avec le Code (TCC-...) OU l'Identifiant (PAT-...)
            ids_autorises = [str(CURRENT_USER_ID).strip(), str(USER_IDENTIFIER).strip()]
            
            # On nettoie la colonne patient et on filtre
            df_final["Patient"] = df_final["Patient"].astype(str).str.strip()
            df_final = df_final[df_final["Patient"].isin(ids_autorises)]
            # =================================================================

    except: pass
    st.session_state.data_sommeil = df_final

if "sommeil_units" not in st.session_state:
    st.session_state.sommeil_units = ["Verres", "Tasses", "mg", "cp", "ml", "Pintes"]

# --- FONCTIONS CALCUL ---
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

# --- ONGLET 1 : SAISIE ---
with tab1:
    st.subheader("📝 Saisie de la nuit dernière")

    with st.form("form_sommeil"):
        c_date, _ = st.columns([1, 2])
        with c_date: date_nuit = st.date_input("Date du lever (Ce matin)", datetime.now())
        st.divider()
        
        liste_heures_activites = ["Non"] + [f"{h}h{m:02d}" for h in range(24) for m in (0, 15, 30, 45)]
        liste_durees = ["15 min", "30 min", "45 min", "1h00", "1h30", "2h00", "3h+"]

        st.markdown("### 🌞 Activités Physiques & Repos")
        col_s1, col_s2, col_s3 = st.columns([2, 1, 1])
        with col_s1: h_sieste = st.selectbox("💤 Sieste (Heure début)", liste_heures_activites)
        with col_s2: d_sieste = st.selectbox("Durée", liste_durees, key="d_sieste")
        
        col_sp1, col_sp2, col_sp3 = st.columns([2, 1, 1])
        with col_sp1: h_sport = st.selectbox("🏋️ Sport (Heure début)", liste_heures_activites)
        with col_sp2: d_sport = st.selectbox("Durée", liste_durees, key="d_sport")

        st.write("") 
        st.markdown("### 🍷 Consommations (Dernière prise)")
        
        def ligne_conso(label, icon, key_prefix, default_idx=0):
            c_h, c_qty, c_u = st.columns([2, 1, 1])
            with c_h: heure = st.selectbox(f"{icon} {label} (Heure)", liste_heures_activites, key=f"{key_prefix}_h")
            with c_qty: qty = st.number_input("Qté", min_value=0.0, step=0.5, key=f"{key_prefix}_q")
            with c_u:
                safe_idx = default_idx if default_idx < len(st.session_state.sommeil_units) else 0
                unit = st.selectbox("Unité", st.session_state.sommeil_units, index=safe_idx, key=f"{key_prefix}_u")
            return heure, qty, unit

        h_cafe, q_cafe, u_cafe = ligne_conso("Caféine", "☕", "cafe", 0) 
        h_alcool, q_alcool, u_alcool = ligne_conso("Alcool", "🍷", "alcool", 1) 
        h_med, q_med, u_med = ligne_conso("Médicament", "💊", "med", 2) 

        st.divider()
        st.markdown("### 🌙 Votre Nuit")
        col_coucher, col_lever = st.columns(2)
        with col_coucher:
            st.info("**Au Coucher**")
            h_coucher = st.time_input("Heure au lit", time(23, 0))
            latence = st.number_input("Latence (min)", 0, 300, 15, step=5)
        with col_lever:
            st.success("**Au Lever**")
            h_lever = st.time_input("Heure de sortie du lit", time(7, 0))
            eveil_nocturne = st.number_input("Éveil nocturne (min)", 0, 300, 0, step=5)

        st.write("")
        st.markdown("### ⭐ Bilan")
        c_forme, c_qualite = st.columns(2)
        with c_forme: forme = st.slider("🔋 Forme (1=HS, 5=Top)", 1, 5, 3)
        with c_qualite: qualite = st.slider("✨ Qualité Sommeil (1=Mauvais, 5=Top)", 1, 5, 3)

        st.write("")
        submitted = st.form_submit_button("💾 Enregistrer ma nuit", use_container_width=True, type="primary")

        if submitted:
            sieste_final = "Non" if h_sieste == "Non" else f"{h_sieste} ({d_sieste})"
            sport_final = "Non" if h_sport == "Non" else f"{h_sport} ({d_sport})"
            cafe_final = "Non" if h_cafe == "Non" else f"{h_cafe} - {q_cafe} {u_cafe}"
            alcool_final = "Non" if h_alcool == "Non" else f"{h_alcool} - {q_alcool} {u_alcool}"
            med_final = "Non" if h_med == "Non" else f"{h_med} - {q_med} {u_med}"

            tal_minutes = calculer_duree_minutes(h_coucher, h_lever)
            tte_minutes = latence + eveil_nocturne
            tts_minutes = tal_minutes - tte_minutes
            efficacite = round((tts_minutes / tal_minutes) * 100, 1) if tal_minutes > 0 else 0

            st.success("✅ Données enregistrées !")
            r1, r2, r3, r4 = st.columns(4)
            r1.metric("Au lit", format_minutes_en_h_m(tal_minutes))
            r2.metric("Sommeil", format_minutes_en_h_m(tts_minutes))
            r3.metric("Éveil", format_minutes_en_h_m(tte_minutes))
            r4.metric("Efficacité", f"{efficacite} %")

            new_row = {
                "Patient": USER_IDENTIFIER,
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
            
            try:
                from connect_db import save_data
                save_data("Sommeil", [
                    USER_IDENTIFIER, str(date_nuit), 
                    sieste_final, sport_final, cafe_final, alcool_final, med_final,
                    str(h_coucher)[:5], latence, eveil_nocturne, str(h_lever)[:5],
                    format_minutes_en_h_m(tte_minutes),
                    format_minutes_en_h_m(tal_minutes),
                    format_minutes_en_h_m(tts_minutes),
                    forme, qualite, f"{efficacite}%"
                ])
            except Exception as e:
                st.error(f"Erreur Cloud : {e}")

    with st.expander("⚙️ Gérer les unités"):
        c_add, c_del = st.columns(2)
        with c_add:
            new_u = st.text_input("Nouvelle unité :", placeholder="ex: Bol", label_visibility="collapsed")
            if st.button("➕ Ajouter", key="btn_add_u"):
                if new_u: st.session_state.sommeil_units.append(new_u)
        with c_del:
            if st.session_state.sommeil_units:
                del_u = st.selectbox("Supprimer :", st.session_state.sommeil_units, label_visibility="collapsed")
                if st.button("🗑️ Supprimer", key="btn_del_u"):
                    st.session_state.sommeil_units.remove(del_u)

# ==============================================================================
# ONGLET 2 : ANALYSE (HISTORIQUE)
# ==============================================================================
with tab2:
    st.header("📊 Tableau de bord")
    
    if not st.session_state.data_sommeil.empty:
        
        # 1. Préparation pour affichage
        df_display = st.session_state.data_sommeil.copy()
        
        if "Patient" in df_display.columns:
            df_display["Patient"] = str(USER_IDENTIFIER)

        # 2. Affichage Tableau
        st.dataframe(
            df_display, 
            use_container_width=True, 
            hide_index=True 
        )
        
        st.divider()
        
        # 3. ANALYSE AVANCÉE (FILTRES & GRAPHIQUES)
        
        # --- A. PRÉPARATION DES DONNÉES ---
        df_chart = st.session_state.data_sommeil.copy()
        df_chart["Date_Obj"] = pd.to_datetime(df_chart["Date"], errors='coerce')
        
        # Nettoyage des colonnes numériques
        cols_num = ["Efficacité", "Forme", "Qualité"]
        for c in cols_num:
            if c in df_chart.columns:
                df_chart[c] = pd.to_numeric(df_chart[c].astype(str).str.replace('%', ''), errors='coerce')
            
        df_chart = df_chart.dropna(subset=["Date_Obj"])

        # --- B. FILTRE TEMPOREL ---
        st.markdown("##### 📅 Période d'analyse")
        col_vue, col_date = st.columns([1, 2])
        
        with col_vue:
            vue_temporelle = st.selectbox(
                "Vue :", 
                ["Tout l'historique", "Semaine", "Mois"],
                label_visibility="collapsed"
            )

        with col_date:
            date_ref = st.date_input("Choisir la date de référence :", datetime.now(), label_visibility="collapsed")

        # Variables dynamiques
        titre_graphique = "Historique complet"
        
        # Application du filtre
        if vue_temporelle == "Semaine":
            start_week = date_ref - timedelta(days=date_ref.weekday())
            end_week = start_week + timedelta(days=6)
            df_chart = df_chart[(df_chart['Date_Obj'].dt.date >= start_week) & (df_chart['Date_Obj'].dt.date <= end_week)]
            st.caption(f"🔎 Semaine du {start_week.strftime('%d/%m')} au {end_week.strftime('%d/%m')}")
            titre_graphique = f"du {start_week.strftime('%d/%m/%y')} au {end_week.strftime('%d/%m/%y')}"

        elif vue_temporelle == "Mois":
            df_chart = df_chart[(df_chart['Date_Obj'].dt.month == date_ref.month) & (df_chart['Date_Obj'].dt.year == date_ref.year)]
            st.caption(f"🔎 Mois de {date_ref.strftime('%B %Y')}")
            titre_graphique = f"- Mois de {date_ref.strftime('%m/%Y')}"
            
        else:
            st.caption(f"🔎 Historique complet ({len(df_chart)} nuits)")

        # --- C. AGRÉGATION (Moyenne par jour pour éviter doublons graphiques) ---
        if not df_chart.empty:
            df_plot = df_chart.groupby("Date_Obj")[cols_num].mean().reset_index()
            
            # KPI
            c1, c2, c3 = st.columns(3)
            with c1: st.metric("Efficacité Moyenne", f"{df_plot['Efficacité'].mean():.1f} %")
            with c2: st.metric("Forme Moyenne", f"{df_plot['Forme'].mean():.1f} / 5")
            with c3: st.metric("Qualité Moyenne", f"{df_plot['Qualité'].mean():.1f} / 5")
        
            st.divider()

            # --- D. VISUALISATION ---
            import altair as alt

            # GRAPHIQUE 1 : EFFICACITÉ
            st.subheader(f"🌙 Efficacité du Sommeil {titre_graphique}")
            chart_eff = alt.Chart(df_plot).mark_line(point=True, color="#3498db").encode(
                x=alt.X('Date_Obj:T', title='Date', axis=alt.Axis(format='%d/%m')),
                y=alt.Y('Efficacité:Q', title='Efficacité (%)', scale=alt.Scale(domain=[0, 100])),
                tooltip=[alt.Tooltip('Date_Obj', title='Date', format='%d/%m/%Y'), 'Efficacité']
            ).interactive()
            st.altair_chart(chart_eff, use_container_width=True)

            # GRAPHIQUE 2 : FORME & QUALITÉ
            st.subheader(f"🔋 Forme & Qualité {titre_graphique}")
            
            base = alt.Chart(df_plot).encode(x=alt.X('Date_Obj:T', title='Date', axis=alt.Axis(format='%d/%m')))

            line_forme = base.mark_line(point=True, color="#e67e22").encode(
                y=alt.Y('Forme:Q', scale=alt.Scale(domain=[0, 6]), title="Note (0-5)"),
                tooltip=[alt.Tooltip('Date_Obj', title='Date', format='%d/%m/%Y'), 'Forme']
            )
            
            line_qualite = base.mark_line(point=True, color="#9b59b6", strokeDash=[5, 5]).encode(
                y=alt.Y('Qualité:Q'),
                tooltip=[alt.Tooltip('Date_Obj', title='Date', format='%d/%m/%Y'), 'Qualité']
            )

            st.altair_chart((line_forme + line_qualite).interactive(), use_container_width=True)
            st.caption("🟠 Trait continu : Forme | 🟣 Pointillés : Qualité du sommeil")

        else:
            st.info("Aucune donnée sur cette période.")

        # 4. SUPPRESSION
        st.divider()
        with st.expander("🗑️ Supprimer une entrée"):
            df_h = st.session_state.data_sommeil.sort_values(by="Date", ascending=False)
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
                        # Suppression dans le Cloud
                        delete_data_flexible("Sommeil", {
                            "Patient": USER_IDENTIFIER, 
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