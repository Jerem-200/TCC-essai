import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, timedelta


# ==============================================================================
# 1. VISUEL ACTIVITÉS (Activités + Humeur)
# ==============================================================================
def afficher_activites(df_activites, df_humeur, current_user_id):
    if not df_activites.empty:
        # --- A. TABLEAU ---
        df_display = df_activites.copy()
        
        # Tentative récupération nom dossier (Optionnel pour l'affichage pur)
        if "Patient" in df_display.columns:
            df_display["Patient"] = str(current_user_id)
        
        st.dataframe(
            df_display.sort_values(by=["Date", "Heure"], ascending=False),
            column_config={"Patient": st.column_config.TextColumn("Dossier")},
            use_container_width=True,
            hide_index=True
        )
        st.divider()

        # --- B. FILTRES ---
        st.subheader("📅 Période d'analyse")
        c1, c2 = st.columns([1, 2])
        with c1:
            vue = st.selectbox("Vue :", ["Tout l'historique", "Journée", "Semaine", "Mois"], key="vue_act")
        with c2:
            date_ref = st.date_input("Date référence :", datetime.now(), key="date_act")

        # --- C. PRÉPARATION DONNÉES ---
        df_filtre = df_activites.copy()
        cols_num = ["Plaisir (0-10)", "Maîtrise (0-10)", "Satisfaction (0-10)"]
        for c in cols_num: 
            if c in df_filtre.columns:
                df_filtre[c] = pd.to_numeric(df_filtre[c], errors='coerce')
        
        df_filtre["Date_Obj"] = pd.to_datetime(df_filtre["Date"], errors='coerce')
        # Construction Datetime
        try:
            df_filtre["Datetime_Full"] = pd.to_datetime(
                df_filtre["Date"].astype(str) + " " + df_filtre["Heure"].astype(str), 
                errors='coerce'
            )
        except:
            df_filtre["Datetime_Full"] = df_filtre["Date_Obj"]

        df_filtre = df_filtre.dropna(subset=["Datetime_Full", "Activité"])

        # Logique Filtre
        titre_graphique = "Historique complet"
        format_axe_x = '%d/%m'
        titre_axe_x = "Date"

        if vue == "Journée":
            df_filtre = df_filtre[df_filtre['Datetime_Full'].dt.date == date_ref]
            titre_graphique = f"du {date_ref.strftime('%d/%m/%Y')}"
            format_axe_x = '%H:%M'
            titre_axe_x = "Heure"
        elif vue == "Semaine":
            start = date_ref - timedelta(days=date_ref.weekday())
            end = start + timedelta(days=6)
            df_filtre = df_filtre[(df_filtre['Datetime_Full'].dt.date >= start) & (df_filtre['Datetime_Full'].dt.date <= end)]
            titre_graphique = f"Semaine du {start.strftime('%d/%m')}"
        elif vue == "Mois":
            df_filtre = df_filtre[(df_filtre['Datetime_Full'].dt.month == date_ref.month) & (df_filtre['Datetime_Full'].dt.year == date_ref.year)]
            titre_graphique = f"Mois de {date_ref.strftime('%m/%Y')}"

        if not df_filtre.empty:
            # 1. MOYENNES (Bar Chart)
            st.subheader(f"📊 Moyennes {titre_graphique}")
            df_grp = df_filtre.groupby("Activité")[cols_num].mean().reset_index()
            df_long = df_grp.melt(id_vars=["Activité"], value_vars=cols_num, var_name="Critère", value_name="Note")
            
            c_bar = alt.Chart(df_long).mark_bar().encode(
                x=alt.X('Activité:N', axis=alt.Axis(labelAngle=-45)),
                y=alt.Y('Note:Q', scale=alt.Scale(domain=[0, 10])),
                color='Critère:N', xOffset='Critère:N', tooltip=['Activité', 'Critère', alt.Tooltip('Note', format='.1f')]
            ).properties(height=350)
            st.altair_chart(c_bar, use_container_width=True)

            # 2. ÉVOLUTION (Line Chart)
            st.subheader(f"📈 Évolution {titre_graphique}")
            if vue != "Journée":
                df_evol_raw = df_filtre.groupby("Date_Obj")[cols_num].mean().reset_index()
                x_def = alt.X('Date_Obj:T', title=titre_axe_x, axis=alt.Axis(format=format_axe_x))
                col_x = 'Date_Obj'
            else:
                df_evol_raw = df_filtre
                x_def = alt.X('Datetime_Full:T', title=titre_axe_x, axis=alt.Axis(format=format_axe_x))
                col_x = 'Datetime_Full'

            df_evol = df_evol_raw.melt(id_vars=[col_x], value_vars=cols_num, var_name="Critère", value_name="Note")
            
            c_line = alt.Chart(df_evol).mark_line(point=True).encode(
                x=x_def,
                y=alt.Y('Note:Q', scale=alt.Scale(domain=[0, 10])),
                color='Critère:N',
                tooltip=[alt.Tooltip(col_x, title=titre_axe_x, format=format_axe_x), 'Critère', 'Note']
            ).properties(height=300).interactive()
            st.altair_chart(c_line, use_container_width=True)
        else:
            st.info("Aucune activité sur cette période.")

        st.divider()

        # --- D. HUMEUR ---
        st.subheader(f"🌈 Humeur {titre_graphique}")
        if not df_humeur.empty:
            df_h = df_humeur.copy()
            df_h["Date_Obj"] = pd.to_datetime(df_h["Date"], errors='coerce')
            if "Humeur Globale (0-10)" in df_h.columns:
                df_h["Humeur Globale (0-10)"] = pd.to_numeric(df_h["Humeur Globale (0-10)"], errors='coerce')
                df_h = df_h.dropna(subset=["Date_Obj"]).sort_values("Date_Obj")

                # Filtre Humeur
                if vue == "Semaine":
                    df_h = df_h[(df_h['Date_Obj'].dt.date >= start) & (df_h['Date_Obj'].dt.date <= end)]
                elif vue == "Mois":
                    df_h = df_h[(df_h['Date_Obj'].dt.month == date_ref.month) & (df_h['Date_Obj'].dt.year == date_ref.year)]
                elif vue == "Journée":
                    df_h = df_h[df_h['Date_Obj'].dt.date == date_ref]

                if not df_h.empty:
                    c_hum = alt.Chart(df_h).mark_line(point=True, color="#FFA500").encode(
                        x=alt.X('Date_Obj:T', title="Date", axis=alt.Axis(format='%d/%m')),
                        y=alt.Y('Humeur Globale (0-10):Q', scale=alt.Scale(domain=[0, 10])),
                        tooltip=['Date', 'Humeur Globale (0-10)']
                    ).properties(height=250).interactive()
                    st.altair_chart(c_hum, use_container_width=True)
                else:
                    st.info("Pas d'humeur sur cette période.")
        else:
            st.info("Pas de données d'humeur.")
    else:
        st.info("Aucune activité enregistrée.")


# ==============================================================================
# 2. VISUEL SOMMEIL
# ==============================================================================
def afficher_sommeil(df_sommeil, current_user_id):
    if not df_sommeil.empty:
        # A. TABLEAU
        df_display = df_sommeil.copy()
        if "Patient" in df_display.columns:
            df_display["Patient"] = str(current_user_id)
        
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        st.divider()

        # B. ANALYSE
        df_chart = df_sommeil.copy()
        df_chart["Date_Obj"] = pd.to_datetime(df_chart["Date"], errors='coerce')
        
        cols_num = ["Efficacité", "Forme", "Qualité"]
        for c in cols_num:
            if c in df_chart.columns:
                df_chart[c] = pd.to_numeric(df_chart[c].astype(str).str.replace('%', ''), errors='coerce')
        
        df_chart = df_chart.dropna(subset=["Date_Obj"])

        # Filtres
        st.subheader("📅 Période d'analyse")
        c1, c2 = st.columns([1, 2])
        with c1: vue = st.selectbox("Vue :", ["Tout l'historique", "Semaine", "Mois"], key="vue_som")
        with c2: date_ref = st.date_input("Date référence :", datetime.now(), key="date_som")

        titre = "Historique"
        if vue == "Semaine":
            start = date_ref - timedelta(days=date_ref.weekday())
            end = start + timedelta(days=6)
            df_chart = df_chart[(df_chart['Date_Obj'].dt.date >= start) & (df_chart['Date_Obj'].dt.date <= end)]
            titre = f"Semaine du {start.strftime('%d/%m')}"
        elif vue == "Mois":
            df_chart = df_chart[(df_chart['Date_Obj'].dt.month == date_ref.month) & (df_chart['Date_Obj'].dt.year == date_ref.year)]
            titre = f"Mois de {date_ref.strftime('%m/%Y')}"

        if not df_chart.empty:
            # KPI
            df_plot = df_chart.groupby("Date_Obj")[cols_num].mean().reset_index()
            k1, k2, k3 = st.columns(3)
            k1.metric("Efficacité Moy.", f"{df_plot['Efficacité'].mean():.1f} %")
            k2.metric("Forme Moy.", f"{df_plot['Forme'].mean():.1f} / 5")
            k3.metric("Qualité Moy.", f"{df_plot['Qualité'].mean():.1f} / 5")
            
            st.divider()
            
            # G1 : Efficacité
            st.subheader(f"🌙 Efficacité {titre}")
            c_eff = alt.Chart(df_plot).mark_line(point=True, color="#3498db").encode(
                x=alt.X('Date_Obj:T', axis=alt.Axis(format='%d/%m')),
                y=alt.Y('Efficacité:Q', scale=alt.Scale(domain=[0, 100])),
                tooltip=['Date_Obj', 'Efficacité']
            ).interactive()
            st.altair_chart(c_eff, use_container_width=True)

            # G2 : Forme/Qualité
            st.subheader(f"🔋 Forme & Qualité {titre}")
            base = alt.Chart(df_plot).encode(x=alt.X('Date_Obj:T', axis=alt.Axis(format='%d/%m')))
            l_forme = base.mark_line(point=True, color="#e67e22").encode(
                y=alt.Y('Forme:Q', scale=alt.Scale(domain=[0, 6])), tooltip=['Date_Obj', 'Forme']
            )
            l_qual = base.mark_line(point=True, color="#9b59b6", strokeDash=[5, 5]).encode(
                y=alt.Y('Qualité:Q'), tooltip=['Date_Obj', 'Qualité']
            )
            st.altair_chart((l_forme + l_qual).interactive(), use_container_width=True)
        else:
            st.info("Aucune donnée sur cette période.")
    else:
        st.info("Aucune donnée de sommeil.")


# ==============================================================================
# 3. VISUEL CONSOMMATIONS
# ==============================================================================
def afficher_conso(df_conso, current_user_id):
    if not df_conso.empty:
        # A. TABLEAU
        df_display = df_conso.copy()
        if "Patient" in df_display.columns: df_display["Patient"] = str(current_user_id)
        if "Quantité" not in df_display.columns: df_display["Quantité"] = 0.0
        if "Unité" not in df_display.columns: df_display["Unité"] = ""
        
        # Filtre substance (Optionnel si on veut tout voir d'un coup)
        subs = df_display["Substance"].unique().tolist()
        sub_sel = st.selectbox("Filtrer par substance :", ["Tout"] + subs, key="filtre_sub_conso")
        
        if sub_sel != "Tout":
            df_display = df_display[df_display["Substance"] == sub_sel]

        st.dataframe(df_display, use_container_width=True, hide_index=True)
        st.divider()

        # B. GRAPHIQUES
        df_chart = df_display.copy()
        # Date complete
        try:
            df_chart['Full_Date'] = pd.to_datetime(df_chart['Date'].astype(str) + ' ' + df_chart['Heure'].astype(str), errors='coerce')
        except:
            df_chart['Full_Date'] = pd.to_datetime(df_chart['Date'], errors='coerce')
        df_chart = df_chart.dropna(subset=['Full_Date'])

        # Filtres Temps
        st.subheader("📅 Période d'analyse")
        c1, c2 = st.columns([1, 2])
        with c1: vue = st.selectbox("Vue :", ["Tout", "Journée", "Semaine", "Mois"], key="vue_conso")
        with c2: date_ref = st.date_input("Date référence :", datetime.now(), key="date_conso")

        format_x = '%d/%m'
        titre_x = "Date"
        
        if vue == "Journée":
            df_chart = df_chart[df_chart['Full_Date'].dt.date == date_ref]
            format_x = '%H:%M'
            titre_x = "Heure"
        elif vue == "Semaine":
            start = date_ref - timedelta(days=date_ref.weekday())
            end = start + timedelta(days=6)
            df_chart = df_chart[(df_chart['Full_Date'].dt.date >= start) & (df_chart['Full_Date'].dt.date <= end)]
        elif vue == "Mois":
            df_chart = df_chart[(df_chart['Full_Date'].dt.month == date_ref.month) & (df_chart['Full_Date'].dt.year == date_ref.year)]

        # 1. ENVIES
        df_envie = df_chart[df_chart["Type"].astype(str).str.contains("ENVIE", na=False)]
        if not df_envie.empty:
            st.subheader("⚡ Envies (Craving)")
            df_envie["Intensité"] = pd.to_numeric(df_envie["Intensité"], errors='coerce')
            
            c_env = alt.Chart(df_envie).mark_line(point=True, color="#9B59B6").encode(
                x=alt.X('Full_Date:T', axis=alt.Axis(format=format_x), title=titre_x),
                y=alt.Y('Intensité:Q', scale=alt.Scale(domain=[0, 10])),
                tooltip=['Date', 'Heure', 'Substance', 'Intensité']
            ).interactive()
            st.altair_chart(c_env, use_container_width=True)

        # 2. CONSOS
        df_cons = df_chart[df_chart["Type"].astype(str).str.contains("CONSOMMÉ", na=False)]
        if not df_cons.empty:
            st.subheader("🍷 Consommations")
            df_cons["Quantité"] = pd.to_numeric(df_cons["Quantité"], errors='coerce')
            
            c_con = alt.Chart(df_cons).mark_bar(color="#E74C3C").encode(
                x=alt.X('Full_Date:T', axis=alt.Axis(format=format_x), title=titre_x),
                y='Quantité:Q',
                tooltip=['Date', 'Heure', 'Substance', 'Quantité', 'Unité']
            ).interactive()
            st.altair_chart(c_con, use_container_width=True)
        
        if df_envie.empty and df_cons.empty:
            st.info("Aucune donnée sur cette période.")
    else:
        st.info("Aucune consommation/envie enregistrée.")


# ==============================================================================
# 4. VISUEL COMPULSIONS
# ==============================================================================
def afficher_compulsions(df_comp, current_user_id):
    if not df_comp.empty:
        df_display = df_comp.copy()
        if "Patient" in df_display.columns: df_display["Patient"] = str(current_user_id)
        if "Heure" not in df_display.columns: df_display["Heure"] = "00:00"
        
        # Numérique
        df_display["Répétitions"] = pd.to_numeric(df_display["Répétitions"], errors='coerce').fillna(0)
        df_display["Durée (min)"] = pd.to_numeric(df_display["Durée (min)"], errors='coerce').fillna(0)
        df_display["Date_Obj"] = pd.to_datetime(df_display["Date"], errors='coerce')
        df_display["Datetime_Full"] = pd.to_datetime(
            df_display["Date"].astype(str) + " " + df_display["Heure"].astype(str), errors='coerce'
        )

        # Filtres
        st.subheader("📅 Période d'analyse")
        c1, c2 = st.columns([1, 2])
        with c1: vue = st.selectbox("Vue :", ["Tout", "Journée", "Semaine", "Mois"], key="vue_comp")
        with c2: date_ref = st.date_input("Date référence :", datetime.now(), key="date_comp")

        format_x = '%d/%m'
        titre_x = "Date"
        df_filter = df_display.dropna(subset=["Datetime_Full"])

        if vue == "Journée":
            df_filter = df_filter[df_filter['Datetime_Full'].dt.date == date_ref]
            format_x = '%H:%M'
            titre_x = "Heure"
        elif vue == "Semaine":
            start = date_ref - timedelta(days=date_ref.weekday())
            end = start + timedelta(days=6)
            df_filter = df_filter[(df_filter['Datetime_Full'].dt.date >= start) & (df_filter['Datetime_Full'].dt.date <= end)]
        elif vue == "Mois":
            df_filter = df_filter[(df_filter['Datetime_Full'].dt.month == date_ref.month) & (df_filter['Datetime_Full'].dt.year == date_ref.year)]

        if not df_filter.empty:
            # KPI
            k1, k2, k3 = st.columns(3)
            k1.metric("Total Épisodes", len(df_filter))
            k2.metric("Temps Cumulé", f"{int(df_filter['Durée (min)'].sum())} min")
            k3.metric("Moy. Répétitions", f"{df_filter['Répétitions'].mean():.1f}")

            # Graphique
            st.subheader("📈 Évolution")
            base = alt.Chart(df_filter).encode(x=alt.X('Datetime_Full:T', axis=alt.Axis(format=format_x), title=titre_x))
            
            l_rep = base.mark_line(point=True, color="#e74c3c").encode(
                y=alt.Y('Répétitions:Q', axis=alt.Axis(titleColor="#e74c3c")),
                tooltip=['Date', 'Heure', 'Nature', 'Répétitions']
            )
            l_dur = base.mark_line(point=True, color="#3498db", strokeDash=[5,5]).encode(
                y=alt.Y('Durée (min):Q', axis=alt.Axis(titleColor="#3498db")),
                tooltip=['Date', 'Heure', 'Nature', 'Durée (min)']
            )
            st.altair_chart(alt.layer(l_rep, l_dur).resolve_scale(y='independent').interactive(), use_container_width=True)
            
            # Tableau
            st.dataframe(
                df_filter[["Date", "Heure", "Nature", "Répétitions", "Durée (min)"]].sort_values(by=["Date", "Heure"], ascending=False),
                use_container_width=True, hide_index=True
            )
        else:
            st.info("Aucune donnée sur cette période.")
    else:
        st.info("Aucune compulsion.")

# ==============================================================================
# 5. VISUELS SIMPLES (Tableaux seuls)
# ==============================================================================
def afficher_tableau_simple(df, colonnes_utiles=None):
    if not df.empty:
        df_tri = df.sort_values(by="Date", ascending=False) if "Date" in df.columns else df
        if colonnes_utiles:
            # On ne garde que les colonnes qui existent
            cols = [c for c in colonnes_utiles if c in df_tri.columns]
            st.dataframe(df_tri[cols], use_container_width=True, hide_index=True)
        else:
            st.dataframe(df_tri, use_container_width=True, hide_index=True)
    else:
        st.info("Aucune donnée.")