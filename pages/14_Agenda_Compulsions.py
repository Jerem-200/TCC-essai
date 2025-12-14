import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, timedelta
from visualisations import afficher_conso

st.set_page_config(page_title="Agenda des Compulsions", page_icon="🛑")

# ==============================================================================
# 0. SÉCURITÉ & IDENTIFICATION
# ==============================================================================

if "authentifie" not in st.session_state or not st.session_state.authentifie:
    st.warning("🔒 Accès restreint. Veuillez entrer votre Code Patient sur l'accueil.")
    st.page_link("streamlit_app.py", label="Retourner à l'accueil", icon="🏠")
    st.stop()

# 1. Récupération simple de l'ID (Standardisé)
# Grâce à votre modification dans l'accueil, ceci contient DÉJÀ "PAT-001"
CURRENT_USER_ID = st.session_state.get("user_id", "")

if not CURRENT_USER_ID:
    st.error("Session expirée. Veuillez vous reconnecter.")
    st.stop()

# 2. Anti-Fuite
if "compulsion_owner" not in st.session_state or st.session_state.compulsion_owner != CURRENT_USER_ID:
    if "data_compulsions" in st.session_state: del st.session_state.data_compulsions
    st.session_state.compulsion_owner = CURRENT_USER_ID

st.title("🛑 Agenda des Compulsions")
st.info(f"Suivi des rituels et compulsions pour le dossier : {CURRENT_USER_ID}")

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
            
            # Correction si colonne manquante
            if "Patient" not in df_cloud.columns:
                df_cloud["Patient"] = str(CURRENT_USER_ID)
            
            # Remplissage
            for col in COLS_COMP:
                if col in df_cloud.columns:
                    df_init[col] = df_cloud[col]
            
            # FILTRE SÉCURITÉ SIMPLIFIÉ
            if "Patient" in df_init.columns:
                df_init = df_init[df_init["Patient"].astype(str) == str(CURRENT_USER_ID)]
            else:
                df_init = pd.DataFrame(columns=COLS_COMP)
            
            # Nettoyage numérique
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
            duree = st.number_input("Temps total (minutes)", min_value=0, value=5, step=5)
            
        st.write("")
        submitted = st.form_submit_button("Enregistrer", type="primary")
        
        if submitted:
            heure_str = str(heure_evt)[:5]
            
            new_row = {
                "Patient": CURRENT_USER_ID, # Utilisation directe
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
                    CURRENT_USER_ID, str(date_evt), heure_str, 
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
                        "Patient": CURRENT_USER_ID, 
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
        if "Patient" in df_display.columns: df_display["Patient"] = str(CURRENT_USER_ID)
        if "Heure" not in df_display.columns: df_display["Heure"] = "00:00"
        
        # Conversion numérique
        df_display["Répétitions"] = pd.to_numeric(df_display["Répétitions"], errors='coerce').fillna(0)
        df_display["Durée (min)"] = pd.to_numeric(df_display["Durée (min)"], errors='coerce').fillna(0)
        
        # CRÉATION D'UNE DATE COMPLÈTE
        df_display["Date_Obj"] = pd.to_datetime(df_display["Date"], errors='coerce')
        df_display["Datetime_Full"] = pd.to_datetime(
            df_display["Date"].astype(str) + " " + df_display["Heure"].astype(str), 
            errors='coerce'
        )
        
        # 2. FILTRE TEMPOREL
        st.subheader("📅 Période d'analyse")
        col_vue, col_date = st.columns([1, 2])
        with col_vue:
            vue = st.selectbox("Vue :", ["Tout l'historique", "Semaine", "Mois", "Journée"], label_visibility="collapsed")
        with col_date:
            date_ref = st.date_input("Date de référence :", datetime.now(), label_visibility="collapsed")

        # LOGIQUE D'AFFICHAGE DU GRAPHIQUE
        format_axe_x = '%d/%m'
        titre_axe_x = "Date"
        titre_graphique = ""
        
        if vue == "Journée":
            format_axe_x = '%H:%M'
            titre_axe_x = "Heure"

        # Application Filtre & Construction du Titre
        df_filtered = df_display.copy().dropna(subset=["Datetime_Full"])
        
        if vue == "Semaine":
            start = date_ref - timedelta(days=date_ref.weekday())
            end = start + timedelta(days=6)
            df_filtered = df_filtered[(df_filtered['Datetime_Full'].dt.date >= start) & (df_filtered['Datetime_Full'].dt.date <= end)]
            st.caption(f"🔎 Semaine du {start.strftime('%d/%m')} au {end.strftime('%d/%m')}")
            titre_graphique = f"Évolution du {start.strftime('%d/%m/%y')} au {end.strftime('%d/%m/%y')}"
            
        elif vue == "Mois":
            df_filtered = df_filtered[(df_filtered['Datetime_Full'].dt.month == date_ref.month) & (df_filtered['Datetime_Full'].dt.year == date_ref.year)]
            st.caption(f"🔎 Mois de {date_ref.strftime('%B %Y')}")
            titre_graphique = f"Évolution - Mois de {date_ref.strftime('%m/%Y')}"
            
        elif vue == "Journée":
            df_filtered = df_filtered[df_filtered['Datetime_Full'].dt.date == date_ref]
            st.caption(f"🔎 Journée du {date_ref.strftime('%d/%m/%Y')}")
            titre_graphique = f"Évolution du {date_ref.strftime('%d/%m/%Y')}"
        
        else:
            titre_graphique = "Évolution - Historique complet"

        st.divider()

        # 3. STATISTIQUES & GRAPHIQUES
        if not df_filtered.empty:
            
            # --- AGRÉGATION DES DONNÉES ---
            if vue != "Journée":
                # Si on est en vue Semaine/Mois/Historique, on groupe par jour et on fait la moyenne
                df_to_plot = df_filtered.groupby("Date_Obj").agg({
                    "Répétitions": "mean",
                    "Durée (min)": "mean"
                }).reset_index()
                
                df_to_plot["Répétitions"] = df_to_plot["Répétitions"].round(1)
                df_to_plot["Durée (min)"] = df_to_plot["Durée (min)"].round(1)
                
                x_axis_def = alt.X('Date_Obj:T', title=titre_axe_x, axis=alt.Axis(format=format_axe_x))
                tooltip_rep = ['Date_Obj', alt.Tooltip('Répétitions', title="Moyenne Rép.")]
                tooltip_dur = ['Date_Obj', alt.Tooltip('Durée (min)', title="Moyenne Durée")]
                
            else:
                # Vue Journée : détail heure par heure
                df_to_plot = df_filtered
                x_axis_def = alt.X('Datetime_Full:T', title=titre_axe_x, axis=alt.Axis(format=format_axe_x))
                tooltip_rep = ['Date', 'Heure', 'Nature', 'Répétitions']
                tooltip_dur = ['Date', 'Heure', 'Nature', 'Durée (min)']

            # --- KPI ---
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Épisodes", len(df_filtered))
            c2.metric("Temps Total (Cumulé)", f"{int(df_filtered['Durée (min)'].sum())} min")
            c3.metric("Moyenne Répétitions", f"{df_filtered['Répétitions'].mean():.1f}")

            # --- GRAPHIQUE ---
            st.subheader(f"📈 {titre_graphique}")
            
            base = alt.Chart(df_to_plot).encode(x=x_axis_def)
            
            # Ligne 1 : Répétitions (Axe Y Gauche - Rouge)
            line_rep = base.mark_line(point=True, color="#e74c3c").encode(
                y=alt.Y('Répétitions:Q', title='Moy. Répétitions' if vue != "Journée" else 'Répétitions', axis=alt.Axis(titleColor="#e74c3c")),
                tooltip=tooltip_rep
            )
            
            # Ligne 2 : Durée (Axe Y Droite - Bleu)
            line_dur = base.mark_line(point=True, color="#3498db", strokeDash=[5,5]).encode(
                y=alt.Y('Durée (min):Q', title='Moy. Durée (min)' if vue != "Journée" else 'Durée (min)', axis=alt.Axis(titleColor="#3498db")),
                tooltip=tooltip_dur
            )
            
            # COMBINAISON
            final_chart = alt.layer(line_rep, line_dur).resolve_scale(y='independent')
            
            st.altair_chart(final_chart.interactive(), use_container_width=True)
            
            if vue != "Journée":
                st.caption("ℹ️ Les points représentent la **moyenne journalière**.")
            else:
                st.caption("ℹ️ Les points représentent chaque épisode de la journée.")
            
            st.caption("🔴 Axe Gauche : Répétitions | 🔵 Axe Droit : Durée (min)")

            # Tableau détaillé
            st.subheader("📋 Détails des épisodes")
            cols_show = ["Date", "Heure", "Nature", "Répétitions", "Durée (min)"]
            df_table = df_filtered.sort_values(by=["Date", "Heure"], ascending=False)
            
            st.dataframe(
                df_table[cols_show], 
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
                        "Patient": CURRENT_USER_ID, 
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