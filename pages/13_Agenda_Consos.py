import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, time, timedelta

st.set_page_config(page_title="Agenda Consos", page_icon="🍷")

# ==============================================================================
# 0. SÉCURITÉ & IDENTIFICATION
# ==============================================================================

# 1. Vérification de l'authentification
if "authentifie" not in st.session_state or not st.session_state.authentifie:
    st.warning("🔒 Accès restreint. Veuillez entrer votre Code Patient sur l'accueil.")
    st.page_link("streamlit_app.py", label="Retourner à l'accueil", icon="🏠")
    st.stop()

# 2. Récupération simple de l'ID (Standardisé)
# Grâce à votre modification dans l'accueil, ceci contient DÉJÀ "PAT-001"
CURRENT_USER_ID = st.session_state.get("user_id", "")

if not CURRENT_USER_ID:
    st.error("Session expirée. Veuillez vous reconnecter.")
    st.stop()

# 3. VERROUILLAGE ANTI-FUITE (Nettoyage des listes si changement de patient)
if "conso_owner" not in st.session_state or st.session_state.conso_owner != CURRENT_USER_ID:
    if "data_addictions" in st.session_state: del st.session_state.data_addictions
    if "liste_substances" in st.session_state: del st.session_state.liste_substances
    st.session_state.conso_owner = CURRENT_USER_ID

st.title("🍷 Agenda des Envies & Consommations")
st.info("Notez vos envies (craving) et vos consommations pour identifier les déclencheurs.")

# ==============================================================================
# 1. INITIALISATION, CHARGEMENT & GESTION DES SUBSTANCES
# ==============================================================================

# A. Liste des substances
if "liste_substances" not in st.session_state:
    st.session_state.liste_substances = []

# Liste des unités par défaut
if "liste_unites" not in st.session_state:
    st.session_state.liste_unites = ["Verres", "Cigarettes", "Joints", "ml", "cl", "grammes"]

# B. Chargement des données
if "data_addictions" not in st.session_state:
    cols_conso = ["Patient", "Date", "Heure", "Substance", "Type", "Intensité", "Quantité", "Unité", "Pensées"]
    df_final = pd.DataFrame(columns=cols_conso)
    
    # Tentative de chargement Cloud
    try:
        from connect_db import load_data
        data_cloud = load_data("Addictions")
        
        if data_cloud:
            df_cloud = pd.DataFrame(data_cloud)
            
            # Remplissage intelligent
            for col in cols_conso:
                if col in df_cloud.columns:
                    df_final[col] = df_cloud[col]
                elif col.lower() in df_cloud.columns:
                    df_final[col] = df_cloud[col.lower()]
                else:
                    df_final[col] = None 
            
            # FILTRE SÉCURITÉ
            if "Patient" in df_final.columns:
                df_final = df_final[df_final["Patient"].astype(str) == str(CURRENT_USER_ID)]
            else:
                df_final = pd.DataFrame(columns=cols_conso)
            
            # Nettoyage numérique
            for col_num in ["Intensité", "Quantité"]:
                if col_num in df_final.columns:
                    df_final[col_num] = df_final[col_num].astype(str).str.replace(',', '.')
                    df_final[col_num] = pd.to_numeric(df_final[col_num], errors='coerce')

    except Exception as e:
        pass

    st.session_state.data_addictions = df_final

    # C. Remplissage liste substances depuis l'historique
    if not df_final.empty and "Substance" in df_final.columns:
        subs_history = df_final["Substance"].dropna().unique().tolist()
        for s in subs_history:
            s_propre = str(s).strip()
            if s_propre and s_propre not in st.session_state.liste_substances:
                st.session_state.liste_substances.append(s_propre)

# --- MEMOIRE INTELLIGENTE ---
if "memoire_heure" not in st.session_state:
    st.session_state.memoire_heure = time(12, 00)
if "memoire_unite" not in st.session_state:
    st.session_state.memoire_unite = ""

# ==============================================================================
# ZONE DE SÉLECTION
# ==============================================================================
col_info, col_sel = st.columns([2, 2])
with col_info:
    st.write("**De quoi voulez-vous faire le suivi ?**")

with col_sel:
    # Création
    with st.popover("➕ Nouvelle Substance/Comportement"):
        new_sub = st.text_input("Nom (ex: Alcool, Tabac, Jeux...)")
        if st.button("Créer") and new_sub:
            if new_sub not in st.session_state.liste_substances:
                st.session_state.liste_substances.append(new_sub)
                st.rerun()

    # Sélection
    if st.session_state.liste_substances:
        substance_active = st.selectbox("Substance active :", st.session_state.liste_substances)
    else:
        st.warning("Ajoutez une substance ci-dessus pour commencer.")
        st.stop()

# --- ONGLETS ---
tab1, tab2 = st.tabs(["📝 Saisie (Journal)", "📊 Bilan & Historique"])

# ==============================================================================
# ONGLET 1 : SAISIE ADAPTATIVE
# ==============================================================================
with tab1:
    st.header(f"Journal : {substance_active}")
    
    # 1. TYPE D'ÉVÉNEMENT
    type_evt = st.radio(
        "Qu'est-ce qui s'est passé ?", 
        ["⚡ J'ai eu une ENVIE (Craving)", "🍷 J'ai CONSOMMÉ"], 
        horizontal=True
    )

    # 2. LE FORMULAIRE DE SAISIE
    with st.form("form_addiction"):
        
        # A. DATE ET HEURE
        c_date, c_heure = st.columns(2)
        with c_date: 
            date_evt = st.date_input("Date", datetime.now())
        with c_heure: 
            heure_evt = st.time_input("Heure", value=st.session_state.memoire_heure)
            
        st.write("---")

        # B. CONTENU SPÉCIFIQUE
        valeur_numerique = 0.0
        pensees = ""
        unite_finale = ""
        
        if "CONSOMMÉ" in type_evt:
            st.markdown("#### Détails de la consommation")
            
            col_qte, col_unit = st.columns([1, 1])
            
            with col_qte:
                valeur_numerique = st.number_input("Quantité", min_value=0.0, step=0.5)

            with col_unit:
                # Gestion sécurité mémoire
                idx_def = 0
                if st.session_state.memoire_unite in st.session_state.liste_unites:
                     idx_def = st.session_state.liste_unites.index(st.session_state.memoire_unite)
                
                if st.session_state.liste_unites:
                    unite_finale = st.selectbox("Unité", st.session_state.liste_unites, index=idx_def)
                else:
                    st.warning("Aucune unité disponible. Ajoutez-en une au-dessus.")
                    unite_finale = ""

            # Formatage texte
            if unite_finale:
                pensees = f"Consommation : {valeur_numerique} {unite_finale}"
            else:
                pensees = f"Consommation : {valeur_numerique}"

        else: # CAS ENVIE
            st.markdown("#### Évaluation de l'envie")
            valeur_numerique = st.slider("Intensité (0-10)", 0, 10, 5)
            
            with st.expander("ℹ️ Aide : Les 3 types de pensées à repérer"):
                st.markdown("""
                * **🟢 Pensées Permissives :** Autorisations qu'on se donne.  
                *Ex: "Juste un seul, ça ne compte pas".*
                * **🔵 Pensées Soulageantes :** Croyance que le produit aide.  
                *Ex: "Ça va me calmer".*
                * **🟡 Attentes Positives :** Idéalisation des effets.  
                *Ex: "Je serai plus drôle".*
                """)
            
            pensees = st.text_area("Pensées / Contexte :")

        st.divider()
        submitted = st.form_submit_button("💾 Enregistrer")
        
        if submitted:
            # Vérification simple
            if "CONSOMMÉ" in type_evt and not unite_finale:
                st.error("⚠️ Veuillez sélectionner une unité.")
            else:
                # B. FORMATAGE & MÉMOIRE
                heure_str = heure_evt.strftime("%H:%M")
                st.session_state.memoire_heure = heure_evt
                
                if "CONSOMMÉ" in type_evt:
                      st.session_state.memoire_unite = unite_finale
                      
                      val_intensite = None 
                      val_quantite = valeur_numerique
                      val_unite = unite_finale
                else:
                    # Envie
                    val_intensite = valeur_numerique
                    val_quantite = None
                    val_unite = None
                
                # C. SAUVEGARDE LOCALE
                new_row = {
                    "Patient": CURRENT_USER_ID,
                    "Date": str(date_evt),
                    "Heure": heure_str,
                    "Substance": substance_active,
                    "Type": type_evt,
                    "Intensité": val_intensite,
                    "Quantité": val_quantite,
                    "Unité": val_unite,
                    "Pensées" : pensees
                }
                st.session_state.data_addictions = pd.concat([st.session_state.data_addictions, pd.DataFrame([new_row])], ignore_index=True)
                
                # D. SAUVEGARDE CLOUD
                try:
                    from connect_db import save_data
                    save_data("Addictions", [
                        CURRENT_USER_ID, str(date_evt), heure_str, substance_active, 
                        type_evt, val_intensite, val_quantite, val_unite, pensees
                    ])
                    st.success("Enregistré !")
                    
                except Exception as e:
                    st.error(f"Erreur sauvegarde : {e}")

    # ---------------------------------------------------------
    # ZONE DE GESTION DES UNITÉS
    # ---------------------------------------------------------
    if "CONSOMMÉ" in type_evt:
        with st.expander("⚙️ Gérer les unités (Ajout / Suppression)"):
            st.caption("Ajoutez une nouvelle unité à la liste ou supprimez-en une existante.")
            c_add, c_del = st.columns(2)
            
            with c_add:
                st.markdown("**Ajouter**")
                new_unit_name = st.text_input("Nom de l'unité :", placeholder="ex: Pintes", label_visibility="collapsed")
                if st.button("➕ Créer", key="btn_add_unit"):
                    if new_unit_name:
                        if new_unit_name not in st.session_state.liste_unites:
                            st.session_state.liste_unites.append(new_unit_name)
                            st.rerun()
            
            with c_del:
                st.markdown("**Supprimer**")
                if st.session_state.liste_unites:
                    del_unit_name = st.selectbox("Choisir l'unité :", st.session_state.liste_unites, label_visibility="collapsed")
                    if st.button("🗑️ Effacer", key="btn_del_unit"):
                        if del_unit_name in st.session_state.liste_unites:
                            st.session_state.liste_unites.remove(del_unit_name)
                            if st.session_state.memoire_unite == del_unit_name:
                                st.session_state.memoire_unite = ""
                            st.rerun()

    # --- ZONE DE SUPPRESSION RAPIDE ---
    with st.expander("🗑️ Supprimer une entrée récente (Correction d'erreur)"):
        df_actuel = st.session_state.data_addictions
        df_substance = df_actuel[df_actuel["Substance"] == substance_active].sort_values(by=["Date", "Heure"], ascending=False)
        
        if not df_substance.empty:
            options_suppr = {}
            for idx, row in df_substance.iterrows():
                is_envie = "ENVIE" in str(row['Type'])
                icone = "⚡" if is_envie else "🍷"
                type_lbl = "Envie" if is_envie else "Conso"
                raw_pensees = str(row.get('Pensées', ''))
                pensees_txt = (raw_pensees[:30] + '...') if len(raw_pensees) > 30 else raw_pensees
                
                label = f"📅 {row['Date']} à {row['Heure']} | {icone} {type_lbl} | 📊 {row['Intensité']} | 📝 {pensees_txt}"
                if label in options_suppr: label = f"{label} (ID: {idx})"
                options_suppr[label] = idx
            
            choix_suppr = st.selectbox(
                "Choisir la ligne à effacer :", 
                list(options_suppr.keys()), 
                key="select_suppr_tab1",
                index=None,
                placeholder="Sélectionnez pour corriger..."
            )
            
            if st.button("❌ Supprimer définitivement", key="btn_suppr_tab1") and choix_suppr:
                idx_to_drop = options_suppr[choix_suppr]
                row_to_delete = df_substance.loc[idx_to_drop]
                
                try:
                    from connect_db import delete_data_flexible
                    delete_data_flexible("Addictions", {
                        "Patient": CURRENT_USER_ID, 
                        "Date": str(row_to_delete["Date"]),
                        "Heure": str(row_to_delete["Heure"]),
                        "Substance": str(row_to_delete["Substance"])
                    })
                except: pass
                
                st.session_state.data_addictions = st.session_state.data_addictions.drop(idx_to_drop).reset_index(drop=True)
                st.success("Entrée supprimée !")
                st.rerun()
        else:
            st.info(f"Aucune donnée récente pour {substance_active}.")

# ==============================================================================
# ONGLET 2 : BILAN (TABLEAU ÉDITABLE + GRAPHIQUES)
# ==============================================================================
with tab2:
    st.header(f"Historique : {substance_active}")
    
    df_global = st.session_state.data_addictions

    if "Quantité" not in df_global.columns: df_global["Quantité"] = 0.0
    if "Unité" not in df_global.columns: df_global["Unité"] = ""
        
    st.session_state.data_addictions = df_global 
    
    # Filtre substance active
    df_filtre = df_global[df_global["Substance"] == substance_active].sort_values(by=["Date", "Heure"], ascending=False).reset_index(drop=True)
    
    if not df_filtre.empty:
        st.info("💡 Vous pouvez modifier les valeurs directement dans le tableau.")
        
        # Affichage avec le nom propre (CURRENT_USER_ID)
        df_editor_view = df_filtre.copy()
        if "Patient" in df_editor_view.columns:
            df_editor_view["Patient"] = str(CURRENT_USER_ID)

        # TABLEAU ÉDITABLE
        edited_df = st.data_editor(
            df_editor_view, 
            column_order=["Patient", "Date", "Heure", "Substance", "Type", "Intensité", "Quantité", "Unité", "Pensées"], 
            disabled=["Patient", "Substance"],
            use_container_width=True, 
            num_rows="dynamic",
            key=f"editor_{substance_active}"
        )
        
        # GESTION DES MODIFICATIONS
        if not edited_df.equals(df_editor_view):
            edited_df["Patient"] = CURRENT_USER_ID
            edited_df["Substance"] = substance_active 
            df_others = df_global[df_global["Substance"] != substance_active]
            st.session_state.data_addictions = pd.concat([df_others, edited_df], ignore_index=True)
            st.rerun()

        st.divider()

        # --- GRAPHIQUES AVANCÉS ---
        df_chart = edited_df.copy()
        try:
            df_chart['Full_Date'] = pd.to_datetime(
                df_chart['Date'].astype(str) + ' ' + df_chart['Heure'].astype(str), 
                format="%Y-%m-%d %H:%M", errors='coerce'
            )
        except:
            df_chart['Full_Date'] = pd.to_datetime(df_chart['Date'], errors='coerce')
        
        df_chart = df_chart.dropna(subset=['Full_Date'])

        # Filtre Temporel
        st.markdown("##### 📅 Période d'analyse")
        col_vue, col_date = st.columns([1, 2])
        
        with col_vue:
            vue_temporelle = st.selectbox("Vue :", ["Tout l'historique", "Journée", "Semaine", "Mois"], label_visibility="collapsed")

        with col_date:
            date_ref = st.date_input("Choisir la date :", datetime.now(), label_visibility="collapsed")

        titre_graphique = "Historique complet"
        format_axe_x = '%d/%m'
        titre_axe_x = "Date"

        if vue_temporelle == "Journée":
            df_chart = df_chart[df_chart['Full_Date'].dt.date == date_ref]
            titre_graphique = f"Évolution du {date_ref.strftime('%d/%m/%Y')}"
            format_axe_x = '%H:%M'
            titre_axe_x = "Heure"

        elif vue_temporelle == "Semaine":
            start_week = date_ref - timedelta(days=date_ref.weekday())
            end_week = start_week + timedelta(days=6)
            df_chart = df_chart[(df_chart['Full_Date'].dt.date >= start_week) & (df_chart['Full_Date'].dt.date <= end_week)]
            titre_graphique = f"Évolution du {start_week.strftime('%d/%m/%y')} au {end_week.strftime('%d/%m/%y')}"

        elif vue_temporelle == "Mois":
            df_chart = df_chart[(df_chart['Full_Date'].dt.month == date_ref.month) & (df_chart['Full_Date'].dt.year == date_ref.year)]
            titre_graphique = f"Évolution - Mois de {date_ref.strftime('%m/%Y')}"

        # 1. ENVIES
        df_envie = df_chart[df_chart["Type"].str.contains("ENVIE", na=False)]
        
        if not df_envie.empty:
            st.subheader(f"⚡ {titre_graphique} (Envies)")
            
            if vue_temporelle != "Journée":
                df_envie_plot = df_envie.groupby("Date").agg({"Intensité": "mean", "Full_Date": "first"}).reset_index()
                tooltip_envie = ['Date', alt.Tooltip('Intensité', title="Moyenne Intensité", format=".1f")]
            else:
                df_envie_plot = df_envie
                tooltip_envie = ['Date', 'Heure', 'Intensité', 'Pensées']

            chart_envie = alt.Chart(df_envie_plot).mark_line(
                point=alt.OverlayMarkDef(size=100, filled=True, color="#9B59B6")
            ).encode(
                x=alt.X('Full_Date:T', title=titre_axe_x, axis=alt.Axis(format=format_axe_x)),
                y=alt.Y('Intensité:Q', title='Intensité (0-10)', scale=alt.Scale(domain=[0, 10])),
                color=alt.value("#9B59B6"),
                tooltip=tooltip_envie
            ).interactive()
            st.altair_chart(chart_envie, use_container_width=True)
        elif vue_temporelle != "Tout l'historique":
            st.info("Aucune envie sur cette période.")

        # 2. CONSOMMATIONS
        df_conso = df_chart[df_chart["Type"].str.contains("CONSOMMÉ", na=False)]
        
        if not df_conso.empty:
            st.subheader(f"🍷 {titre_graphique} (Consommations)")
            
            unites_dispo = df_conso['Unité'].dropna().unique().tolist()
            if not unites_dispo: unites_dispo = ["Inconnu"]
            choix_unite = st.radio("Unité :", options=["Tout voir"] + unites_dispo, horizontal=True)

            if choix_unite != "Tout voir":
                data_plot_raw = df_conso[df_conso['Unité'] == choix_unite]
                title_y = f"Quantité ({choix_unite})"
            else:
                data_plot_raw = df_conso
                title_y = "Quantité (Toutes unités)"

            if not data_plot_raw.empty:
                if vue_temporelle != "Journée":
                    data_plot = data_plot_raw.groupby("Date").agg({"Quantité": "sum", "Full_Date": "first", "Unité": "first"}).reset_index()
                    tooltip_conso = ['Date', alt.Tooltip('Quantité', title="Total Quantité"), 'Unité']
                else:
                    data_plot = data_plot_raw
                    tooltip_conso = ['Date', 'Heure', 'Quantité', 'Unité', 'Pensées']

                chart_conso = alt.Chart(data_plot).mark_bar(color="#E74C3C").encode(
                    x=alt.X('Full_Date:T', title=titre_axe_x, axis=alt.Axis(format=format_axe_x)),
                    y=alt.Y('Quantité:Q', title=title_y),
                    tooltip=tooltip_conso
                ).interactive()
                st.altair_chart(chart_conso, use_container_width=True)
            else:
                st.warning(f"Pas de consommation en '{choix_unite}' sur cette période.")

        # ZONE DE SUPPRESSION (HISTORIQUE)
        st.divider()
        with st.expander("🗑️ Supprimer une entrée depuis l'historique"):
            df_history = st.session_state.data_addictions.sort_values(by=["Date", "Heure"], ascending=False)
            
            if not df_history.empty:
                options_history = {}
                for idx, row in df_history.iterrows():
                    is_envie = "ENVIE" in str(row['Type'])
                    icone = "⚡" if is_envie else "🍷"
                    type_lbl = "Envie" if is_envie else "Conso"
                    raw_pensees = str(row.get('Pensées', ''))
                    pensees_txt = (raw_pensees[:30] + '...') if len(raw_pensees) > 30 else raw_pensees
                    
                    label = f"📅 {row['Date']} à {row['Heure']} | {icone} {type_lbl} | 📊 {row['Intensité']} | 📝 {pensees_txt}"
                    if label in options_history: label = f"{label} (ID: {idx})"
                    options_history[label] = idx
                
                choice_history = st.selectbox("Sélectionnez l'entrée à supprimer :", list(options_history.keys()), key="del_tab2", index=None)
                
                if st.button("Confirmer la suppression", key="btn_del_tab2") and choice_history:
                    idx_to_drop = options_history[choice_history]
                    row_to_delete = df_history.loc[idx_to_drop]

                    try:
                        from connect_db import delete_data_flexible
                        delete_data_flexible("Addictions", {
                            "Patient": CURRENT_USER_ID, 
                            "Date": str(row_to_delete['Date']),
                            "Heure": str(row_to_delete['Heure']),
                            "Substance": str(row_to_delete['Substance'])
                        })
                    except Exception as e: pass

                    st.session_state.data_addictions = st.session_state.data_addictions.drop(idx_to_drop).reset_index(drop=True)
                    st.success("Entrée supprimée !")
                    st.rerun()
            else:
                st.info("Historique vide.")
    else:
        st.info(f"Aucune donnée enregistrée pour '{substance_active}'.")

st.divider()
st.page_link("streamlit_app.py", label="Retour à l'accueil", icon="🏠")