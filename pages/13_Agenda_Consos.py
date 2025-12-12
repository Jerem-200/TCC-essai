import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, time, timedelta

st.set_page_config(page_title="Agenda Consos", page_icon="🍷")

# 1. Vérification de l'authentification
if "authentifie" not in st.session_state or not st.session_state.authentifie:
    st.warning("🔒 Accès restreint. Veuillez entrer votre Code Patient sur l'accueil.")
    st.page_link("streamlit_app.py", label="Retourner à l'accueil", icon="🏠")
    st.stop()

# 2. Récupération sécurisée de l'ID
CURRENT_USER_ID = st.session_state.get("user_id", "")
if not CURRENT_USER_ID:
    CURRENT_USER_ID = st.session_state.get("patient_id", "")

if not CURRENT_USER_ID:
    st.error("Erreur d'identité. Veuillez vous reconnecter.")
    st.stop()

# 3. VERROUILLAGE ANTI-FUITE (Nettoyage des listes si changement de patient)
if "conso_owner" not in st.session_state or st.session_state.conso_owner != CURRENT_USER_ID:
    if "data_addictions" in st.session_state: del st.session_state.data_addictions
    if "liste_substances" in st.session_state: del st.session_state.liste_substances # Important !
    st.session_state.conso_owner = CURRENT_USER_ID

st.title("🍷 Agenda des Envies & Consommations")
st.info("Notez vos envies (craving) et vos consommations pour identifier les déclencheurs.")

# ==============================================================================
# 1. INITIALISATION, CHARGEMENT & GESTION DES SUBSTANCES (TOUT EN UN)
# ==============================================================================

# A. Liste des substances
if "liste_substances" not in st.session_state:
    st.session_state.liste_substances = []

# --- AJOUT : Liste des unités ---
if "liste_unites" not in st.session_state:
    # On met des unités classiques par défaut
    st.session_state.liste_unites = ["Verres", "Cigarettes", "Joints", "ml", "cl", "grammes"]
# -------------------------------

# B. Chargement des données et récupération des substances de l'historique
if "data_addictions" not in st.session_state:
    # --- CHANGEMENT ICI : AJOUT DE QUANTITÉ ET UNITÉ ---
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
                # On vérifie les variations de noms (minuscule/majuscule)
                if col in df_cloud.columns:
                    df_final[col] = df_cloud[col]
                elif col.lower() in df_cloud.columns:
                    df_final[col] = df_cloud[col.lower()]
                # Si la colonne n'existe pas dans le cloud (anciennes données), on met des valeurs vides
                else:
                    df_final[col] = None 
            
            # FILTRE SÉCURITÉ CRUCIAL
            if "Patient" in df_final.columns:
                df_final = df_final[df_final["Patient"].astype(str) == str(CURRENT_USER_ID)]
            else:
                df_final = pd.DataFrame(columns=cols_conso)
            
            # Nettoyage numérique (votre code existant continue après ça) ...

            # Nettoyage numérique
            for col_num in ["Intensité", "Quantité"]:
                if col_num in df_final.columns:
                    df_final[col_num] = df_final[col_num].astype(str).str.replace(',', '.')
                    df_final[col_num] = pd.to_numeric(df_final[col_num], errors='coerce')

    except Exception as e:
        pass

    st.session_state.data_addictions = df_final

    # C. MAGIE : Remplissage liste substances
    if not df_final.empty and "Substance" in df_final.columns:
        subs_history = df_final["Substance"].dropna().unique().tolist()
        for s in subs_history:
            s_propre = str(s).strip()
            if s_propre and s_propre not in st.session_state.liste_substances:
                st.session_state.liste_substances.append(s_propre)

# --- MEMOIRE INTELLIGENTE (Heure/Unité) ---
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
                # Gestion sécurité mémoire (si l'unité en mémoire a été supprimée, on gère)
                if st.session_state.memoire_unite and st.session_state.memoire_unite not in st.session_state.liste_unites:
                     # On remet à vide ou on l'ajoute ? Ici on reset pour éviter les erreurs
                     idx_def = 0
                else:
                    try:
                        idx_def = st.session_state.liste_unites.index(st.session_state.memoire_unite)
                    except:
                        idx_def = 0
                
                # Le menu est maintenant toujours propre (sans "Autre")
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
                     
                     # --- NOUVELLE LOGIQUE ---
                     # Conso : Intensité est vide (ou 0), on remplit Quantité/Unité
                     val_intensite = None 
                     val_quantite = valeur_numerique
                     val_unite = unite_finale
                else:
                    # Envie : On remplit Intensité, Quantité/Unité sont vides
                    val_intensite = valeur_numerique
                    val_quantite = None
                    val_unite = None
                
                # C. SAUVEGARDE LOCALE
                new_row = {
                    "Date": str(date_evt),
                    "Heure": heure_str,
                    "Substance": substance_active,
                    "Type": type_evt,
                    "Intensité": val_intensite,
                    "Quantité": val_quantite,   # Nouvelle colonne
                    "Unité": val_unite,         # Nouvelle colonne
                    "Pensées" : pensees         # Ne contient plus que le texte !
                }
                st.session_state.data_addictions = pd.concat([st.session_state.data_addictions, pd.DataFrame([new_row])], ignore_index=True)
                
                # D. SAUVEGARDE CLOUD
                try:
                    from connect_db import save_data
                    patient = CURRENT_USER_ID
                    # Attention l'ordre doit correspondre à vos colonnes Excel
                    save_data("Addictions", [
                        patient, str(date_evt), heure_str, substance_active, 
                        type_evt, val_intensite, val_quantite, val_unite, pensees
                    ])
                    st.success("Enregistré !")
                    
                except Exception as e:
                    st.error(f"Erreur sauvegarde : {e}")

    # ---------------------------------------------------------
    # ZONE DE GESTION DES UNITÉS (VERSION EXPANDER)
    # ---------------------------------------------------------
    if "CONSOMMÉ" in type_evt:
        # On utilise un expander au lieu d'une checkbox
        with st.expander("⚙️ Gérer les unités (Ajout / Suppression)"):
            st.caption("Ajoutez une nouvelle unité à la liste ou supprimez-en une existante.")
            
            c_add, c_del = st.columns(2)
            
            # BLOC AJOUTER
            with c_add:
                st.markdown("**Ajouter**")
                new_unit_name = st.text_input("Nom de l'unité :", placeholder="ex: Pintes", label_visibility="collapsed")
                if st.button("➕ Créer", key="btn_add_unit"):
                    if new_unit_name:
                        if new_unit_name not in st.session_state.liste_unites:
                            st.session_state.liste_unites.append(new_unit_name)
                            st.success(f"'{new_unit_name}' ajouté !")
                            st.rerun()
                        else:
                            st.warning("Cette unité existe déjà.")
                    else:
                        st.warning("Veuillez écrire un nom.")

            # BLOC SUPPRIMER
            with c_del:
                st.markdown("**Supprimer**")
                if st.session_state.liste_unites:
                    del_unit_name = st.selectbox("Choisir l'unité :", st.session_state.liste_unites, label_visibility="collapsed")
                    if st.button("🗑️ Effacer", key="btn_del_unit"):
                        if del_unit_name in st.session_state.liste_unites:
                            st.session_state.liste_unites.remove(del_unit_name)
                            
                            # Si on supprime l'unité qui était en mémoire par défaut, on vide la mémoire
                            if st.session_state.memoire_unite == del_unit_name:
                                st.session_state.memoire_unite = ""
                                
                            st.success(f"'{del_unit_name}' supprimé !")
                            st.rerun()
                else:
                    st.info("La liste est vide.")

# --- ZONE DE SUPPRESSION (ONGLET 1) ---
    with st.expander("🗑️ Supprimer une entrée récente (Correction d'erreur)"):
        # 1. On récupère les données de la substance active UNIQUEMENT
        df_actuel = st.session_state.data_addictions
        df_substance = df_actuel[df_actuel["Substance"] == substance_active].sort_values(by=["Date", "Heure"], ascending=False)
        
        if not df_substance.empty:
            # 2. CRÉATION DES ÉTIQUETTES DÉTAILLÉES (Même design que l'onglet 2)
            options_suppr = {}
            for idx, row in df_substance.iterrows():
                # A. Icône et Type
                is_envie = "ENVIE" in str(row['Type'])
                icone = "⚡" if is_envie else "🍷"
                type_lbl = "Envie" if is_envie else "Conso"
                
                # B. Texte court
                raw_pensees = str(row.get('Pensées', ''))
                pensees_txt = (raw_pensees[:30] + '...') if len(raw_pensees) > 30 else raw_pensees
                
                # C. Label
                label = f"📅 {row['Date']} à {row['Heure']} | {icone} {type_lbl} | 📊 {row['Intensité']} | 📝 {pensees_txt}"
                
                # D. Gestion ID
                if label in options_suppr:
                    label = f"{label} (ID: {idx})"
                
                options_suppr[label] = idx
            
            # 3. Menu Déroulant
            choix_suppr = st.selectbox(
                "Choisir la ligne à effacer :", 
                list(options_suppr.keys()), 
                key="select_suppr_tab1",
                index=None,
                placeholder="Sélectionnez pour corriger..."
            )
            
            # 4. Bouton Suppression
            if st.button("❌ Supprimer définitivement", key="btn_suppr_tab1") and choix_suppr:
                idx_to_drop = options_suppr[choix_suppr]
                row_to_delete = df_substance.loc[idx_to_drop]
                
                # Cloud
                try:
                    from connect_db import delete_data_flexible
                    pid = CURRENT_USER_ID
                    delete_data_flexible("Addictions", {
                        "Patient": pid, 
                        "Date": str(row_to_delete["Date"]),
                        "Heure": str(row_to_delete["Heure"]),
                        "Substance": str(row_to_delete["Substance"])
                    })
                except: pass
                
                # Local
                st.session_state.data_addictions = st.session_state.data_addictions.drop(idx_to_drop).reset_index(drop=True)
                st.success("Entrée corrigée (supprimée) !")
                st.rerun()
        else:
            st.info(f"Aucune donnée récente pour {substance_active}.")

# ==============================================================================
# ONGLET 2 : BILAN (TABLEAU ÉDITABLE + GRAPHIQUE ÉVOLUTION)
# ==============================================================================
# ==============================================================================
# ONGLET 2 : BILAN (TABLEAU ÉDITABLE + GRAPHIQUE ÉVOLUTION)
# ==============================================================================
with tab2:
    st.header(f"Historique : {substance_active}")
    
    # 1. RECUPERATION ET SECURISATION DES DONNÉES
    df_global = st.session_state.data_addictions

    # Initialisation colonnes manquantes
    if "Quantité" not in df_global.columns: df_global["Quantité"] = 0.0
    if "Unité" not in df_global.columns: df_global["Unité"] = ""
        
    st.session_state.data_addictions = df_global 
    
    # On filtre pour la substance active
    df_filtre = df_global[df_global["Substance"] == substance_active].sort_values(by=["Date", "Heure"], ascending=False).reset_index(drop=True)
    
    if not df_filtre.empty:
        st.info("💡 Vous pouvez modifier les valeurs directement dans le tableau.")
        
        # --- A. TRADUCTION DU NOM (Code -> PAT-XXX) ---
        nom_dossier = CURRENT_USER_ID # Par défaut
        try:
            from connect_db import load_data
            infos = load_data("Codes_Patients")
            if infos:
                df_i = pd.DataFrame(infos)
                col_id = "Identifiant" if "Identifiant" in df_i.columns else "Commentaire"
                match = df_i[df_i["Code"] == CURRENT_USER_ID]
                if not match.empty: nom_dossier = match.iloc[0][col_id]
        except: pass
        
        # On crée une vue pour l'éditeur avec le nom lisible
        df_editor_view = df_filtre.copy()
        df_editor_view["Patient"] = nom_dossier 

        # --- B. TABLEAU ÉDITABLE ---
        edited_df = st.data_editor(
            df_editor_view, 
            # On affiche la colonne Patient en premier
            column_order=["Patient", "Date", "Heure", "Substance", "Type", "Intensité", "Quantité", "Unité", "Pensées"], 
            # On interdit de modifier le Dossier et la Substance
            disabled=["Patient", "Substance"],
            column_config={
                "Patient": st.column_config.TextColumn("Dossier"), # Renommage visuel
            },
            use_container_width=True, 
            num_rows="dynamic",
            key=f"editor_{substance_active}"
        )
        
        # --- C. GESTION DES MODIFICATIONS ---
        if not edited_df.equals(df_editor_view):
            # Si l'utilisateur a modifié quelque chose (ex: l'heure ou la quantité)
            
            # 1. On remet le code technique (TCC-XYZ) à la place du PAT-001 avant de sauvegarder
            # Sinon, on perdrait le lien avec le compte !
            edited_df["Patient"] = CURRENT_USER_ID
            edited_df["Substance"] = substance_active # Sécurité
            
            # 2. On fusionne avec le reste des données
            df_others = df_global[df_global["Substance"] != substance_active]
            st.session_state.data_addictions = pd.concat([df_others, edited_df], ignore_index=True)
            st.rerun()

        st.divider()
        st.write(f"### Évolution : {substance_active}")

        # --- A. PRÉPARATION DES DONNÉES ---
        df_chart = edited_df.copy()
        
        # Création colonne Date complète (indispensable pour le filtrage)
        try:
            df_chart['Full_Date'] = pd.to_datetime(
                df_chart['Date'].astype(str) + ' ' + df_chart['Heure'].astype(str), 
                format="%Y-%m-%d %H:%M", errors='coerce'
            )
        except:
            df_chart['Full_Date'] = pd.to_datetime(df_chart['Date'], errors='coerce')
        
        # On s'assure qu'il n'y a pas de NaT (Not a Time)
        df_chart = df_chart.dropna(subset=['Full_Date'])

        # --- B. FILTRE TEMPOREL (NOUVEAU) ---
        st.markdown("##### 📅 Période d'analyse")
        col_vue, col_date = st.columns([1, 2])
        
        with col_vue:
            vue_temporelle = st.selectbox(
                "Vue :", 
                ["Tout l'historique", "Journée", "Semaine", "Mois"],
                label_visibility="collapsed"
            )

        with col_date:
            date_ref = st.date_input("Choisir la date :", datetime.now(), label_visibility="collapsed")

        # Application du filtre
        if vue_temporelle == "Journée":
            # On garde uniquement les entrées de la date choisie
            df_chart = df_chart[df_chart['Full_Date'].dt.date == date_ref]
            msg_filtre = f"Zoom sur la journée du {date_ref.strftime('%d/%m/%Y')}"

        elif vue_temporelle == "Semaine":
            # On calcule le début (Lundi) et la fin (Dimanche) de la semaine de la date choisie
            start_week = date_ref - timedelta(days=date_ref.weekday())
            end_week = start_week + timedelta(days=6)
            
            df_chart = df_chart[
                (df_chart['Full_Date'].dt.date >= start_week) & 
                (df_chart['Full_Date'].dt.date <= end_week)
            ]
            msg_filtre = f"Semaine du {start_week.strftime('%d/%m')} au {end_week.strftime('%d/%m')}"

        elif vue_temporelle == "Mois":
            # On filtre sur le mois et l'année de la date choisie
            df_chart = df_chart[
                (df_chart['Full_Date'].dt.month == date_ref.month) & 
                (df_chart['Full_Date'].dt.year == date_ref.year)
            ]
            msg_filtre = f"Mois de {date_ref.strftime('%B %Y')}"
            
        else:
            msg_filtre = "Historique complet"

        # Petit texte discret pour confirmer la vue
        st.caption(f"🔎 {msg_filtre} ({len(df_chart)} entrées trouvées)")

        # --- C. SÉPARATION ENVIES / CONSO ---
        # Maintenant que df_chart est filtré, on sépare les types
        df_envie = df_chart[df_chart["Type"].str.contains("ENVIE", na=False)]
        df_conso = df_chart[df_chart["Type"].str.contains("CONSOMMÉ", na=False)]

        # --- GRAPHIQUE 1 : LES ENVIES ---
        if not df_envie.empty:
            st.subheader("⚡ Intensité des Envies")
            
            # Paramètres dynamiques du graphique selon la vue
            # Si c'est une journée, on formate l'axe X en Heures:Minutes, sinon Date complète
            format_x = '%H:%M' if vue_temporelle == "Journée" else '%d/%m %H:%M'
            
            chart_envie = alt.Chart(df_envie).mark_line(
                point=alt.OverlayMarkDef(size=100, filled=True, color="#9B59B6")
            ).encode(
                x=alt.X('Full_Date:T', title='Temps', axis=alt.Axis(format=format_x)),
                y=alt.Y('Intensité:Q', title='Intensité (0-10)', scale=alt.Scale(domain=[0, 10])),
                color=alt.value("#9B59B6"),
                tooltip=['Date', 'Heure', 'Intensité', 'Pensées']
            ).interactive()
            st.altair_chart(chart_envie, use_container_width=True)
        elif vue_temporelle != "Tout l'historique" and "ENVIE" in str(st.session_state.data_addictions['Type'].values):
            st.info(f"Aucune envie enregistrée sur cette période ({msg_filtre}).")
        
        # --- GRAPHIQUE 2 : LES CONSOMMATIONS ---
        if not df_conso.empty:
            st.subheader("🍷 Quantités Consommées")
            
            # Menu déroulant Unité
            unites_dispo = df_conso['Unité'].dropna().unique().tolist()
            if not unites_dispo: unites_dispo = ["Inconnu"]
            
            choix_unite = st.radio("Unité :", options=["Tout voir"] + unites_dispo, horizontal=True)

            if choix_unite != "Tout voir":
                data_plot = df_conso[df_conso['Unité'] == choix_unite]
                title_y = f"Quantité ({choix_unite})"
            else:
                data_plot = df_conso
                title_y = "Quantité (Toutes unités)"
                
            format_x = '%H:%M' if vue_temporelle == "Journée" else '%d/%m %H:%M'

            if not data_plot.empty:
                chart_conso = alt.Chart(data_plot).mark_bar(color="#E74C3C").encode(
                    x=alt.X('Full_Date:T', title='Temps', axis=alt.Axis(format=format_x)),
                    y=alt.Y('Quantité:Q', title=title_y),
                    tooltip=['Date', 'Heure', 'Quantité', 'Unité', 'Pensées']
                ).interactive()
                st.altair_chart(chart_conso, use_container_width=True)
            else:
                st.warning(f"Pas de consommation en '{choix_unite}' sur cette période.")


        # --- ZONE DE SUPPRESSION ---
        st.divider()
        with st.expander("🗑️ Supprimer une entrée depuis l'historique"):
            df_history = st.session_state.data_addictions.sort_values(by=["Date", "Heure"], ascending=False)
            
            if not df_history.empty:
                # Création des labels riches
                options_history = {}
                for idx, row in df_history.iterrows():
                    is_envie = "ENVIE" in str(row['Type'])
                    icone = "⚡" if is_envie else "🍷"
                    type_lbl = "Envie" if is_envie else "Conso"
                    
                    raw_pensees = str(row.get('Pensées', ''))
                    pensees_txt = (raw_pensees[:30] + '...') if len(raw_pensees) > 30 else raw_pensees
                    
                    label = f"📅 {row['Date']} à {row['Heure']} | {icone} {type_lbl} | 📊 {row['Intensité']} | 📝 {pensees_txt}"
                    
                    if label in options_history:
                        label = f"{label} (ID: {idx})"
                        
                    options_history[label] = idx
                
                choice_history = st.selectbox("Sélectionnez l'entrée à supprimer :", list(options_history.keys()), key="del_tab2", index=None)
                
                if st.button("Confirmer la suppression", key="btn_del_tab2") and choice_history:
                    idx_to_drop = options_history[choice_history]
                    row_to_delete = df_history.loc[idx_to_drop]

                    try:
                        from connect_db import delete_data_flexible
                        pid = CURRENT_USER_ID
                        delete_data_flexible("Addictions", {
                            "Patient": pid,
                            "Date": str(row_to_delete['Date']),
                            "Heure": str(row_to_delete['Heure']),
                            "Substance": str(row_to_delete['Substance'])
                        })
                    except Exception as e:
                        pass # Erreur silencieuse ou st.warning

                    st.session_state.data_addictions = st.session_state.data_addictions.drop(idx_to_drop).reset_index(drop=True)
                    st.success("Entrée supprimée !")
                    st.rerun()
            else:
                st.info("Historique vide.")

    else:
        st.info(f"Aucune donnée enregistrée pour '{substance_active}'.")

st.divider()
st.page_link("streamlit_app.py", label="Retour à l'accueil", icon="🏠")

