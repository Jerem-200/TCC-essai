import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, timedelta

st.set_page_config(page_title="Agenda des Compulsions", page_icon="🛑")

# ==============================================================================
# 0. SÉCURITÉ & IDENTIFICATION
# ==============================================================================

if "authentifie" not in st.session_state or not st.session_state.authentifie:
    st.warning("🔒 Accès restreint. Veuillez entrer votre Code Patient sur l'accueil.")
    st.page_link("streamlit_app.py", label="Retourner à l'accueil", icon="🏠")
    st.stop()

# 1. Récupération ID
CURRENT_USER_ID = st.session_state.get("user_id", "")
if not CURRENT_USER_ID:
    CURRENT_USER_ID = st.session_state.get("patient_id", "")

if not CURRENT_USER_ID:
    st.error("Erreur d'identité. Veuillez vous reconnecter.")
    st.stop()

# 2. Traduction Identifiant (PAT-001)
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

# 3. Anti-Fuite
if "compulsion_owner" not in st.session_state or st.session_state.compulsion_owner != CURRENT_USER_ID:
    if "data_compulsions" in st.session_state: del st.session_state.data_compulsions
    st.session_state.compulsion_owner = CURRENT_USER_ID

st.title("🛑 Agenda des Compulsions")
st.info(f"Dossier : {USER_IDENTIFIER}")

# ==============================================================================
# 1. CHARGEMENT DES DONNÉES
# ==============================================================================
COLS_COMP = ["Patient", "Date", "Heure", "Nature", "Répétitions", "Durée (min)"]

if "data_compulsions" not in st.session_state:
    df_init = pd.DataFrame(columns=COLS_COMP)
    try:
        from connect_db import load_data
        data_cloud = load_data("Compulsions")
        if data_cloud:
            df_cloud = pd.DataFrame(data_cloud)
            
            if "Patient" not in df_cloud.columns:
                df_cloud["Patient"] = str(USER_IDENTIFIER)
            
            for col in COLS_COMP:
                if col in df_cloud.columns:
                    df_init[col] = df_cloud[col]
            
            ids_ok = [str(CURRENT_USER_ID).strip(), str(USER_IDENTIFIER).strip()]
            df_init["Patient"] = df_init["Patient"].astype(str).str.strip()
            df_init = df_init[df_init["Patient"].isin(ids_ok)]
            
            for c in ["Répétitions", "Durée (min)"]:
                if c in df_init.columns:
                    df_init[c] = pd.to_numeric(df_init[c], errors='coerce').fillna(0).astype(int)

    except: pass
    st.session_state.data_compulsions = df_init

# ==============================================================================
# ONGLETS
# ==============================================================================
tab1, tab2 = st.tabs(["📝 Saisie", "📊 Analyse & Historique"])

# --- ONGLET 1 : SAISIE ---
with tab1:
    st.subheader("Noter un épisode")
    
    with st.form("form_compulsion"):
        c_date, c_heure = st.columns(2)
        with c_date: 
            date_evt = st.date_input("Date", datetime.now())
        with c_heure:
            heure_evt = st.time_input("Heure", datetime.now())
            
        nature = st.text_input("Nature de la compulsion", placeholder="Ex: Lavage des mains, Vérification porte...")
        
        c_rep, c_dur = st.columns(2)
        with c_rep:
            repetitions = st.number_input("Nombre de répétitions", min_value=1, value=1, step=1)
        with c_dur:
            # MODIFICATION ICI : Pas de 5 minutes (step=5)
            duree = st.number_input("Temps total (minutes)", min_value=0, value=5, step=5)
            
        st.write("")
        submitted = st.form_submit_button("Enregistrer", type="primary")
        
        if submitted:
            heure_str = str(heure_evt)[:5]
            
            new_row = {
                "Patient": USER_IDENTIFIER,
                "Date": str(date_evt),
                "Heure": heure_str,
                "Nature": nature,
                "Répétitions": repetitions,
                "Durée (min)": duree
            }
            
            st.session_state.data_compulsions = pd.concat([st.session_state.data_compulsions, pd.DataFrame([new_row])], ignore_index=True)
            
            try:
                from connect_db import save_data
                save_data("Compulsions", [
                    USER_IDENTIFIER, str(date_evt), heure_str, 
                    nature, repetitions, duree
                ])
                st.success("✅ Enregistré !")
            except Exception as e:
                st.error(f"Erreur Cloud : {e}")

    st.divider()
    with st.expander("🗑️ Annuler une saisie récente"):
        df_act = st.session_state.data_compulsions
        if not df_act.empty:
            df_act_s = df_act.sort_values(by=["Date", "Heure"], ascending=False)
            opts = {f"{r['Date']} {r['Heure']} - {r['Nature']}": i for i, r in df_act_s.iterrows()}
            choix = st.selectbox("Choisir :", list(opts.keys()), key="del_quick")
            
            if st.button("Supprimer", key="btn_del_quick") and choix:
                idx = opts[choix]
                row = df_act_s.loc[idx]
                try:
                    from connect_db import delete_data_flexible
                    delete_data_flexible("Compulsions", {
                        "Patient": USER_IDENTIFIER, 
                        "Date": str(row['Date']),
                        "Nature": str(row['Nature'])
                    })
                except: pass
                st.session_state.data_compulsions = df_act.drop(idx).reset_index(drop=True)
                st.success("Supprimé !")
                st.rerun()

# --- ONGLET 2 : ANALYSE ---
with tab2:
    st.header("📊 Tableau de bord")
    
    if not st.session_state.data_compulsions.empty:
        df_display = st.session_state.data_compulsions.copy()
        
        # 1. Préparation Données
        if "Patient" in df_display.columns: df_display["Patient"] = str(USER_IDENTIFIER)
        if "Heure" not in df_display.columns: df_display["Heure"] = "00:00"
        
        # Conversion numérique
        df_display["Répétitions"] = pd.to_numeric(df_display["Répétitions"], errors='coerce').fillna(0)
        df_display["Durée (min)"] = pd.to_numeric(df_display["Durée (min)"], errors='coerce').fillna(0)
        
        # CRÉATION D'UNE DATE COMPLÈTE (DATE + HEURE) pour le graphique précis
        # Cela permet d'afficher l'évolution au sein d'une même journée
        df_display["Datetime_Full"] = pd.to_datetime(
            df_display["Date"].astype(str) + " " + df_display["Heure"].astype(str), 
            errors='coerce'
        )
        
        # 2. FILTRE TEMPOREL (Avec option Journée)
        st.subheader("📅 Période d'analyse")
        col_vue, col_date = st.columns([1, 2])
        with col_vue:
            # MODIFICATION : Ajout de "Journée"
            vue = st.selectbox("Vue :", ["Tout l'historique", "Semaine", "Mois", "Journée"], label_visibility="collapsed")
        with col_date:
            date_ref = st.date_input("Date de référence :", datetime.now(), label_visibility="collapsed")

        # Application Filtre
        df_chart = df_display.copy().dropna(subset=["Datetime_Full"])
        
        if vue == "Semaine":
            start = date_ref - timedelta(days=date_ref.weekday())
            end = start + timedelta(days=6)
            df_chart = df_chart[(df_chart['Datetime_Full'].dt.date >= start) & (df_chart['Datetime_Full'].dt.date <= end)]
            st.caption(f"🔎 Semaine du {start.strftime('%d/%m')} au {end.strftime('%d/%m')}")
            
        elif vue == "Mois":
            df_chart = df_chart[(df_chart['Datetime_Full'].dt.month == date_ref.month) & (df_chart['Datetime_Full'].dt.year == date_ref.year)]
            st.caption(f"🔎 Mois de {date_ref.strftime('%B %Y')}")
            
        elif vue == "Journée":
            # MODIFICATION : Filtre sur la journée précise
            df_chart = df_chart[df_chart['Datetime_Full'].dt.date == date_ref]
            st.caption(f"🔎 Journée du {date_ref.strftime('%d/%m/%Y')}")

        st.divider()

        # 3. STATISTIQUES & GRAPHIQUES
        if not df_chart.empty:
            # KPI
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Épisodes", len(df_chart))
            c2.metric("Temps Total", f"{int(df_chart['Durée (min)'].sum())} min")
            c3.metric("Moyenne Répétitions", f"{df_chart['Répétitions'].mean():.1f}")

            # Graphique d'évolution
            st.subheader("📈 Évolution")
            
            # MODIFICATION : Axe X utilise 'Datetime_Full' pour montrer les heures si on zoome sur une journée
            base = alt.Chart(df_chart).encode(
                x=alt.X('Datetime_Full:T', title='Moment', axis=alt.Axis(format='%d/%m %H:%M'))
            )
            
            line_rep = base.mark_line(point=True, color="#e74c3c").encode(
                y=alt.Y('Répétitions:Q', title='Répétitions'),
                tooltip=['Date', 'Heure', 'Nature', 'Répétitions']
            )
            
            line_dur = base.mark_line(point=True, color="#3498db", strokeDash=[5,5]).encode(
                y=alt.Y('Durée (min):Q', title='Durée (min)'),
                tooltip=['Date', 'Heure', 'Durée (min)']
            )
            
            st.altair_chart((line_rep + line_dur).interactive(), use_container_width=True)
            st.caption("🔴 Rouge : Nombre de répétitions | 🔵 Bleu (pointillés) : Durée en minutes")

            # Tableau détaillé
            st.subheader("📋 Détails")
            cols_show = ["Date", "Heure", "Nature", "Répétitions", "Durée (min)"]
            df_chart = df_chart.sort_values(by=["Date", "Heure"], ascending=False)
            
            st.dataframe(
                df_chart[cols_show], 
                use_container_width=True, 
                hide_index=True,
                column_config={
                    "Heure": st.column_config.TimeColumn("Heure", format="HH:mm"),
                    "Durée (min)": st.column_config.NumberColumn("Durée", format="%d min"),
                }
            )
        else:
            st.info("Aucune donnée sur cette période.")

        # 4. Suppression Historique
        st.divider()
        with st.expander("🗑️ Supprimer une entrée ancienne"):
            opts = {}
            for i, r in df_display.sort_values(by=["Date", "Heure"], ascending=False).iterrows():
                opts[f"{r['Date']} {r['Heure']} | {r['Nature']}"] = i
            
            choix = st.selectbox("Choisir :", list(opts.keys()), index=None, key="del_hist")
            if st.button("Confirmer", key="btn_del_hist") and choix:
                idx = opts[choix]
                row = df_display.loc[idx]
                try:
                    from connect_db import delete_data_flexible
                    delete_data_flexible("Compulsions", {
                        "Patient": USER_IDENTIFIER, 
                        "Date": str(row['Date']),
                        "Nature": str(row['Nature'])
                    })
                except: pass
                st.session_state.data_compulsions = st.session_state.data_compulsions.drop(idx).reset_index(drop=True)
                st.success("Supprimé !")
                st.rerun()

    else:
        st.info("Aucune compulsion enregistrée.")

st.divider()
st.page_link("streamlit_app.py", label="Retour à l'accueil", icon="🏠")