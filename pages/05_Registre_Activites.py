import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime

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
    
    # 1. TABLEAU (Affichage Lecture Seule pour supporter la conversion de nom)
    if not st.session_state.data_activites.empty:
        df_display = st.session_state.data_activites.copy()
        
        # --- RÉCUPÉRATION DU NOM DU DOSSIER (PAT-XXX) ---
        nom_dossier = CURRENT_USER_ID
        try:
            from connect_db import load_data
            infos = load_data("Codes_Patients")
            if infos:
                df_i = pd.DataFrame(infos)
                col_id = "Identifiant" if "Identifiant" in df_i.columns else "Commentaire"
                match = df_i[df_i["Code"] == CURRENT_USER_ID]
                if not match.empty: nom_dossier = match.iloc[0][col_id]
        except: pass
        
        # Remplacement pour l'affichage
        if "Patient" in df_display.columns:
            df_display["Patient"] = nom_dossier
        
        # Affichage
        st.dataframe(
            df_display.sort_values(by=["Date", "Heure"], ascending=False),
            column_config={"Patient": st.column_config.TextColumn("Dossier")},
            use_container_width=True,
            hide_index=True
        )
        st.caption("Utilisez l'onglet 'Saisie' pour supprimer une ligne en cas d'erreur.")

        st.divider()

        # --- FILTRE TEMPOREL ---
        st.subheader("📅 Période d'analyse")
        col_vue, col_date = st.columns([1, 2])
        
        with col_vue:
            # AJOUT DE L'OPTION "JOURNÉE" ICI
            vue_temporelle = st.selectbox(
                "Vue :", 
                ["Tout l'historique", "Journée", "Semaine", "Mois"],
                label_visibility="collapsed"
            )

        with col_date:
            from datetime import timedelta
            date_ref = st.date_input("Choisir la date de référence :", datetime.now(), label_visibility="collapsed")

        # --- PRÉPARATION DES DONNÉES FILTRÉES ---
        df_filtre = st.session_state.data_activites.copy()
        
        # Nettoyage et conversion
        cols_num = ["Plaisir (0-10)", "Maîtrise (0-10)", "Satisfaction (0-10)"]
        for c in cols_num: df_filtre[c] = pd.to_numeric(df_filtre[c], errors='coerce')
        
        # Création Date Complète (Date + Heure)
        df_filtre["Date_Obj"] = pd.to_datetime(df_filtre["Date"], errors='coerce')
        df_filtre["Datetime_Full"] = pd.to_datetime(
            df_filtre["Date"].astype(str) + " " + df_filtre["Heure"].astype(str), 
            errors='coerce'
        )
        
        df_filtre = df_filtre.dropna(subset=["Datetime_Full", "Activité"])

        # Variables dynamiques pour le graphique
        titre_graphique = "Historique complet"
        format_axe_x = '%d/%m'
        titre_axe_x = "Date"

        # Application du filtre
        if vue_temporelle == "Journée":
            # Filtre sur la journée exacte
            df_filtre = df_filtre[df_filtre['Datetime_Full'].dt.date == date_ref]
            titre_graphique = f"du {date_ref.strftime('%d/%m/%Y')}"
            # On change l'axe pour afficher les heures
            format_axe_x = '%H:%M'
            titre_axe_x = "Heure"

        elif vue_temporelle == "Semaine":
            start_week = date_ref - timedelta(days=date_ref.weekday())
            end_week = start_week + timedelta(days=6)
            df_filtre = df_filtre[(df_filtre['Datetime_Full'].dt.date >= start_week) & (df_filtre['Datetime_Full'].dt.date <= end_week)]
            st.caption(f"🔎 Semaine du {start_week.strftime('%d/%m')} au {end_week.strftime('%d/%m')}")
            titre_graphique = f"du {start_week.strftime('%d/%m/%y')} au {end_week.strftime('%d/%m/%y')}"

        elif vue_temporelle == "Mois":
            df_filtre = df_filtre[(df_filtre['Datetime_Full'].dt.month == date_ref.month) & (df_filtre['Datetime_Full'].dt.year == date_ref.year)]
            st.caption(f"🔎 Mois de {date_ref.strftime('%B %Y')}")
            titre_graphique = f"- Mois de {date_ref.strftime('%m/%Y')}"
            
        else:
            st.caption(f"🔎 Historique complet ({len(df_filtre)} activités)")

        if not df_filtre.empty:
            
            # 2. GRAPHIQUE MOYENNES (Sur données filtrées)
            st.subheader(f"📊 Moyennes par Activité {titre_graphique}")
            df_grp = df_filtre.groupby("Activité")[cols_num].mean().reset_index()
            df_long = df_grp.melt(id_vars=["Activité"], value_vars=cols_num, var_name="Critère", value_name="Note")
            
            chart_bar = alt.Chart(df_long).mark_bar().encode(
                x=alt.X('Activité:N', axis=alt.Axis(labelAngle=-45)),
                y=alt.Y('Note:Q', scale=alt.Scale(domain=[0, 10])),
                color='Critère:N', xOffset='Critère:N', tooltip=['Activité', 'Critère', alt.Tooltip('Note', format='.1f')]
            ).properties(height=400)
            st.altair_chart(chart_bar, use_container_width=True)

            # 3. GRAPHIQUE ÉVOLUTION (Adaptatif Journée vs Semaine)
            st.subheader(f"📈 Évolution des activités {titre_graphique}")
            
            # Préparation pour le graphique ligne
            if vue_temporelle != "Journée":
                # Agrégation par jour (Moyenne des notes) si on regarde une semaine ou un mois
                df_evol_raw = df_filtre.groupby("Date_Obj")[cols_num].mean().reset_index()
                # On utilise Date_Obj pour l'axe X (Date uniquement)
                x_axis_def = alt.X('Date_Obj:T', title=titre_axe_x, axis=alt.Axis(format=format_axe_x))
            else:
                # Pas d'agrégation si on regarde une journée, on garde chaque activité précise
                df_evol_raw = df_filtre
                # On utilise Datetime_Full pour l'axe X (Date + Heure)
                x_axis_def = alt.X('Datetime_Full:T', title=titre_axe_x, axis=alt.Axis(format=format_axe_x))

            # Transformation format long pour Altair
            # L'astuce ici est de récupérer le nom de la colonne utilisée pour l'axe X dynamiquement
            nom_col_x = x_axis_def.shorthand.split(':')[0]
            
            df_evol = df_evol_raw.melt(id_vars=[nom_col_x], value_vars=cols_num, var_name="Critère", value_name="Note")
            
            chart_line = alt.Chart(df_evol).mark_line(point=True).encode(
                x=x_axis_def,
                y=alt.Y('Note:Q', title='Note (0-10)', scale=alt.Scale(domain=[0, 10])),
                color='Critère:N',
                tooltip=[alt.Tooltip(nom_col_x, title=titre_axe_x, format=format_axe_x), 'Critère', alt.Tooltip('Note', format='.1f')]
            ).properties(height=300).interactive()
            st.altair_chart(chart_line, use_container_width=True)

        else:
            st.info("Aucune activité sur cette période.")

        st.divider()
        
        # 4. GRAPHIQUE HUMEUR
        st.subheader(f"🌈 Évolution de l'Humeur {titre_graphique}")
        df_h = st.session_state.data_humeur_jour.copy()
        
        if not df_h.empty:
            df_h["Date_Obj"] = pd.to_datetime(df_h["Date"], errors='coerce')
            df_h["Humeur Globale (0-10)"] = pd.to_numeric(df_h["Humeur Globale (0-10)"], errors='coerce')
            df_h = df_h.dropna(subset=["Date_Obj", "Humeur Globale (0-10)"]).sort_values("Date_Obj")
            
            # Filtre Temporel Humeur
            if vue_temporelle == "Semaine":
                df_h = df_h[(df_h['Date_Obj'].dt.date >= start_week) & (df_h['Date_Obj'].dt.date <= end_week)]
            elif vue_temporelle == "Mois":
                df_h = df_h[(df_h['Date_Obj'].dt.month == date_ref.month) & (df_h['Date_Obj'].dt.year == date_ref.year)]
            elif vue_temporelle == "Journée":
                df_h = df_h[df_h['Date_Obj'].dt.date == date_ref]

            if not df_h.empty:
                c_humeur = alt.Chart(df_h).mark_line(point=True, color="#FFA500").encode(
                    x=alt.X('Date_Obj:T', title="Date", axis=alt.Axis(format='%d/%m')),
                    y=alt.Y('Humeur Globale (0-10):Q', scale=alt.Scale(domain=[0, 10])),
                    tooltip=[alt.Tooltip('Date_Obj', title='Date', format='%d/%m'), 'Humeur Globale (0-10)']
                ).properties(height=300).interactive()
                st.altair_chart(c_humeur, use_container_width=True)
            else:
                st.info("Pas d'humeur enregistrée sur cette période.")
        else:
            st.info("Pas encore de données d'humeur.")
# 5. SUPPRESSION DEPUIS L'HISTORIQUE
        st.divider()
        with st.expander("🗑️ Supprimer une activité"):
            # On récupère toutes les activités triées par date
            df_hist_del = st.session_state.data_activites.sort_values(by=["Date", "Heure"], ascending=False)
            
            if not df_hist_del.empty:
                # Création des labels pour le menu déroulant
                opts_del = {}
                for i, row in df_hist_del.iterrows():
                    # Format : Date (Heure) | Activité (Notes P/M/S)
                    lbl = f"📅 {row['Date']} ({row['Heure']}) | {row['Activité']} | P:{row.get('Plaisir (0-10)',0)} M:{row.get('Maîtrise (0-10)',0)}"
                    opts_del[lbl] = i
                
                # Menu de sélection
                choix_del = st.selectbox("Sélectionnez l'activité à supprimer :", list(opts_del.keys()), index=None, key="sel_del_tab2")
                
                # Bouton d'action
                if st.button("Confirmer la suppression", key="btn_del_tab2") and choix_del:
                    idx = opts_del[choix_del]
                    row_to_del = df_hist_del.loc[idx]
                    
                    # 1. Suppression Cloud
                    try:
                        from connect_db import delete_data_flexible
                        delete_data_flexible("Activites", {
                            "Patient": CURRENT_USER_ID, 
                            "Date": str(row_to_del['Date']),
                            "Heure": str(row_to_del['Heure']),
                            "Activité": str(row_to_del['Activité'])
                        })
                    except: pass
                    
                    # 2. Suppression Locale
                    st.session_state.data_activites = st.session_state.data_activites.drop(idx).reset_index(drop=True)
                    st.success("Activité supprimée !")
                    st.rerun()
            else:
                st.info("Historique vide.")

# 6. SUPPRESSION HUMEUR DEPUIS L'HISTORIQUE
        with st.expander("🗑️ Supprimer un relevé d'humeur"):
            df_hum_del = st.session_state.data_humeur_jour.sort_values(by="Date", ascending=False)
            
            if not df_hum_del.empty:
                # Création des labels
                opts_hum = {}
                for i, row in df_hum_del.iterrows():
                    lbl = f"📅 {row['Date']} | Note : {row['Humeur Globale (0-10)']}/10"
                    opts_hum[lbl] = i
                
                # Menu de sélection
                choix_hum = st.selectbox("Sélectionnez l'humeur à supprimer :", list(opts_hum.keys()), index=None, key="sel_del_hum_tab2")
                
                # Bouton
                if st.button("Confirmer la suppression", key="btn_del_hum_tab2") and choix_hum:
                    idx = opts_hum[choix_hum]
                    row_to_del = df_hum_del.loc[idx]
                    
                    # 1. Suppression Cloud
                    try:
                        from connect_db import delete_data_flexible
                        delete_data_flexible("Humeur", {
                            "Patient": CURRENT_USER_ID, 
                            "Date": str(row_to_del['Date'])
                        })
                    except: pass
                    
                    # 2. Suppression Locale
                    st.session_state.data_humeur_jour = st.session_state.data_humeur_jour.drop(idx).reset_index(drop=True)
                    st.success("Humeur supprimée !")
                    st.rerun()
            else:
                st.info("Aucun historique d'humeur.")

    else:
        st.info("Aucune activité enregistrée.")

st.divider()
st.page_link("streamlit_app.py", label="Retour à l'accueil", icon="🏠")