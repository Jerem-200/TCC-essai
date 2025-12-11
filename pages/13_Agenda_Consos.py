import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, time 

st.set_page_config(page_title="Agenda Consos", page_icon="🍷")

# --- VIGILE DE SÉCURITÉ ---
if "authentifie" not in st.session_state or not st.session_state.authentifie:
    st.warning("⛔ Veuillez vous connecter sur la page d'accueil.")
    st.switch_page("streamlit_app.py")
    st.stop()

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
    cols_conso = ["Patient", "Date", "Heure", "Substance", "Type", "Intensité", "Pensées"]
    df_final = pd.DataFrame(columns=cols_conso)
    
    # Tentative de chargement Cloud
    try:
        from connect_db import load_data
        data_cloud = load_data("Addictions") # Vérifiez que l'onglet Excel s'appelle bien "Addictions"
        
        if data_cloud:
            df_cloud = pd.DataFrame(data_cloud)
            
            # Remplissage intelligent (Gestion Majuscules/Minuscules)
            for col in cols_conso:
                if col in df_cloud.columns:
                    df_final[col] = df_cloud[col]
                elif col.lower() in df_cloud.columns:
                    df_final[col] = df_cloud[col.lower()]
            
            # Nettoyage numérique (Virgules -> Points)
            if "Intensité" in df_final.columns:
                df_final["Intensité"] = df_final["Intensité"].astype(str).str.replace(',', '.')
                df_final["Intensité"] = pd.to_numeric(df_final["Intensité"], errors='coerce')

    except Exception as e:
        # st.warning(f"Info : Démarrage à vide ({e})")
        pass

    # Sauvegarde en mémoire
    st.session_state.data_addictions = df_final

    # C. MAGIE : On remplit la liste des substances à partir de l'historique chargé
    if not df_final.empty and "Substance" in df_final.columns:
        # On prend toutes les substances uniques non vides
        subs_history = df_final["Substance"].dropna().unique().tolist()
        
        for s in subs_history:
            s_propre = str(s).strip() # On enlève les espaces inutiles
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
# ==============================================================================
# ONGLET 1 : SAISIE ADAPTATIVE
# ==============================================================================
with tab1:
    st.header(f"Journal : {substance_active}")
    
    # 1. LE TYPE D'ÉVÉNEMENT
    type_evt = st.radio(
        "Qu'est-ce qui s'est passé ?", 
        ["⚡ J'ai eu une ENVIE (Craving)", "🍷 J'ai CONSOMMÉ"], 
        horizontal=True
    )
    
    # 2. LOGIQUE UNITÉ (Placée AVANT le formulaire pour être réactive)
    # On initialise la variable pour qu'elle existe quoi qu'il arrive
    unite_finale = "" 
    ajout_unite = False
    
    # Ce bloc ne s'affiche que si on a choisi "Consommé"
    if "CONSOMMÉ" in type_evt:
        st.info("Choisissez l'unité ci-dessous :")

    # 3. LE FORMULAIRE (Date, Heure, Quantité...)
    with st.form("form_addiction"):
        st.write("---") # Séparateur visuel
        c_date, c_heure = st.columns(2)
        with c_date: 
            date_evt = st.date_input("Date", datetime.now())
        with c_heure: 
            heure_evt = st.time_input("Heure", value=st.session_state.memoire_heure)
            
        valeur_numerique = 0.0
        pensees = ""

                # On fait 2 colonnes : gauche pour cocher, droite pour choisir/saisir
        col_check, col_input = st.columns([1, 2])
        
        with col_check:
            # LA CASE À COCHER QUE VOUS VOULIEZ
            # Le fait d'être hors du form permet l'affichage instantané du champ à droite
            ajout_unite = st.checkbox("➕ Ajouter une nouvelle unité")
        
        with col_input:
            if ajout_unite:
                # Si coché : Champ texte libre qui apparaît instantanément
                unite_finale = st.text_input("Nom de la nouvelle unité", placeholder="ex: Pintes, Litres...")
            else:
                # Sinon : Menu déroulant standard avec mémoire intelligente
                
                # Petite sécurité : si la mémoire n'est pas dans la liste, on l'ajoute temporairement
                if st.session_state.memoire_unite and st.session_state.memoire_unite not in st.session_state.liste_unites:
                     st.session_state.liste_unites.append(st.session_state.memoire_unite)
                
                # On trouve l'index par défaut
                idx_def = 0
                if st.session_state.memoire_unite in st.session_state.liste_unites:
                    idx_def = st.session_state.liste_unites.index(st.session_state.memoire_unite)
                    
                unite_finale = st.selectbox("Unité standard", st.session_state.liste_unites, index=idx_def)
        
        # Bloc Contenu Spécifique
        if "ENVIE" in type_evt:
            st.markdown("#### Évaluation de l'envie")
            valeur_numerique = st.slider("Intensité (0-10)", 0, 10, 5)
            
            with st.expander("ℹ️ Aide : Les types de pensées"):
                st.markdown("* **Permissives** (Juste un...)\n* **Soulageantes** (Ça va calmer...)\n* **Positives** (Je serai mieux...)")
            
            pensees = st.text_area("Pensées / Contexte :")

        else: # CONSOMMATION
            st.markdown("#### Quantité")
            # On demande le chiffre. L'unité est déjà choisie au-dessus du formulaire.
            # J'ai ajouté un label dynamique pour que ce soit plus joli (ex: Combien de Verres ?)
            label_qte = f"Combien de **{unite_finale if unite_finale else '...'}** ?"
            valeur_numerique = st.number_input(label_qte, min_value=0.0, step=0.5)
            
            # On formate le texte pour l'historique
            if unite_finale:
                pensees = f"Consommation : {valeur_numerique} {unite_finale}"
            else:
                pensees = f"Consommation : {valeur_numerique}"

        st.divider()
        submitted = st.form_submit_button("💾 Enregistrer")
        
        if submitted:
            # A. GESTION LISTE (Si c'était une nouvelle unité, on l'ajoute définitivement)
            if "CONSOMMÉ" in type_evt and ajout_unite and unite_finale:
                if unite_finale not in st.session_state.liste_unites:
                    st.session_state.liste_unites.append(unite_finale)
            
            # B. FORMATAGE & MÉMOIRE
            heure_str = heure_evt.strftime("%H:%M")
            st.session_state.memoire_heure = heure_evt
            
            if "CONSOMMÉ" in type_evt and unite_finale:
                 st.session_state.memoire_unite = unite_finale
            
            # C. SAUVEGARDE
            new_row = {
                "Date": str(date_evt),
                "Heure": heure_str,
                "Substance": substance_active,
                "Type": type_evt,
                "Intensité": valeur_numerique,
                "Pensées" : pensees
            }
            st.session_state.data_addictions = pd.concat([st.session_state.data_addictions, pd.DataFrame([new_row])], ignore_index=True)
            
            # Cloud
            try:
                from connect_db import save_data
                patient = st.session_state.get("patient_id", "Anonyme")
                save_data("Addictions", [
                    patient, str(date_evt), heure_str, substance_active, 
                    type_evt, valeur_numerique, pensees
                ])
                st.success("Enregistré !")
                
                # Si on a créé une nouvelle unité, on recharge la page pour qu'elle 
                # apparaisse directement dans la liste déroulante au prochain coup
                if ajout_unite:
                    st.rerun()
                    
            except Exception as e:
                st.error(f"Erreur sauvegarde : {e}")

# --- ZONE DE SUPPRESSION (ONGLET 1) ---
    with st.expander("🗑️ Supprimer une entrée récente"):
        df_actuel = st.session_state.data_addictions
        df_substance = df_actuel[df_actuel["Substance"] == substance_active].sort_values(by=["Date", "Heure"], ascending=False)
        
        if not df_substance.empty:
            options_suppr = {f"{row['Date']} à {row['Heure']} : {row['Type']} ({row['Intensité']})": i for i, row in df_substance.iterrows()}
            choix_suppr = st.selectbox("Choisir la ligne à effacer :", list(options_suppr.keys()), key="select_suppr_tab1", index=None)
            
            if st.button("❌ Supprimer définitivement", key="btn_suppr_tab1") and choix_suppr:
                idx_to_drop = options_suppr[choix_suppr]
                row_to_delete = df_substance.loc[idx_to_drop]
                try:
                    from connect_db import delete_data_flexible
                    pid = st.session_state.get("patient_id", "Anonyme")
                    delete_data_flexible("Addictions", {
                        "Patient": pid, 
                        "Date": str(row_to_delete["Date"]),
                        "Heure": str(row_to_delete["Heure"]),
                        "Substance": str(row_to_delete["Substance"])
                    })
                except: pass
                
                st.session_state.data_addictions = st.session_state.data_addictions.drop(idx_to_drop).reset_index(drop=True)
                st.success("Entrée supprimée !")
                st.rerun()
        else:
            st.info("Aucune donnée récente.")

# ==============================================================================
# ONGLET 2 : BILAN (TABLEAU ÉDITABLE + GRAPHIQUE ÉVOLUTION)
# ==============================================================================
with tab2:
    st.header(f"Historique : {substance_active}")
    
    # 1. FILTRAGE ET PRÉPARATION
    df_global = st.session_state.data_addictions
    # On ne garde que les lignes de la substance active pour l'affichage
    df_filtre = df_global[df_global["Substance"] == substance_active].sort_values(by=["Date", "Heure"], ascending=False).reset_index(drop=True)
    
    if not df_filtre.empty:
        st.info("💡 Vous pouvez modifier les valeurs directement dans le tableau (double-cliquez sur une case).")
        
        # 2. TABLEAU ÉDITABLE (Comme Agenda Sommeil)
        # On cache la colonne Substance car on est déjà dans l'onglet de cette substance
        edited_df = st.data_editor(
            df_filtre, 
            column_order=["Date", "Heure", "Type", "Intensité", "Pensées"], 
            use_container_width=True, 
            num_rows="dynamic",
            key=f"editor_{substance_active}" # Clé unique pour éviter les bugs entre substances
        )
        
        # MISE À JOUR DE LA MÉMOIRE SI CHANGEMENT
        # Si le tableau édité est différent de l'original affiché
        if not edited_df.equals(df_filtre):
            # 1. On prend le DF global et on enlève les anciennes lignes de cette substance
            df_others = df_global[df_global["Substance"] != substance_active]
            # 2. On remet la colonne "Substance" dans le DF édité (au cas où elle aurait sauté)
            edited_df["Substance"] = substance_active
            # 3. On fusionne les autres + les nouvelles lignes éditées
            st.session_state.data_addictions = pd.concat([df_others, edited_df], ignore_index=True)
            st.rerun()

# ... (le code du tableau éditable reste au dessus) ...

        st.divider()
        st.write(f"### Évolution : {substance_active}")

# --- PRÉPARATION DES DONNÉES (SÉCURISÉE) ---
        df_chart = edited_df.copy()
        
        # 1. Conversion Date/Heure (Gestion des formats multiples)
        try:
            # On combine Date et Heure pour l'axe temporel
            df_chart['Full_Date'] = pd.to_datetime(
                df_chart['Date'].astype(str) + ' ' + df_chart['Heure'].astype(str), 
                format="%Y-%m-%d %H:%M", # On essaie le format standard d'abord
                errors='coerce'
            )
            # Si ça échoue (NaN), on essaie de parser automatiquement
            mask_error = df_chart['Full_Date'].isna()
            if mask_error.any():
                 df_chart.loc[mask_error, 'Full_Date'] = pd.to_datetime(df_chart.loc[mask_error, 'Date'], errors='coerce')
        except:
            df_chart['Full_Date'] = pd.to_datetime(df_chart['Date'], errors='coerce')

        # 2. Conversion Chiffres (Sécurité supplémentaire)
        # On remplace les virgules par des points et on convertit
        if "Intensité" in df_chart.columns:
            df_chart['Intensité'] = df_chart['Intensité'].astype(str).str.replace(',', '.')
            df_chart['Intensité'] = pd.to_numeric(df_chart['Intensité'], errors='coerce')
        
        # 1. Conversion Date/Heure
        try:
            df_chart['Full_Date'] = pd.to_datetime(df_chart['Date'].astype(str) + ' ' + df_chart['Heure'].astype(str), errors='coerce')
        except:
            df_chart['Full_Date'] = pd.to_datetime(df_chart['Date'])

        # 2. Conversion Chiffres
        df_chart['Intensité'] = pd.to_numeric(df_chart['Intensité'], errors='coerce')

        # 3. SÉPARATION DES DEUX TYPES
        # On filtre selon le texte contenu dans la colonne "Type"
        df_envie = df_chart[df_chart["Type"].str.contains("ENVIE", na=False)]
        df_conso = df_chart[df_chart["Type"].str.contains("CONSOMMÉ", na=False)]

        # --- GRAPHIQUE 1 : LES ENVIES (COURBE) ---
        if not df_envie.empty:
            st.subheader("⚡ Évolution des Envies (Craving)")
            st.caption("Intensité du besoin psychologique (0 à 10)")
            
            chart_envie = alt.Chart(df_envie).mark_line(
                point=alt.OverlayMarkDef(size=100, filled=True, color="#9B59B6") # Violet
            ).encode(
                x=alt.X('Full_Date:T', title='Temps', axis=alt.Axis(format='%d/%m %H:%M')),
                y=alt.Y('Intensité:Q', title='Intensité (0-10)', scale=alt.Scale(domain=[0, 10])),
                color=alt.value("#9B59B6"), # Ligne Violette
                tooltip=['Date', 'Heure', 'Intensité', 'Pensées']
            ).interactive()
            
            st.altair_chart(chart_envie, use_container_width=True)
        
        # --- GRAPHIQUE 2 : LES CONSOMMATIONS (BARRES) ---
        if not df_conso.empty:
            st.subheader("🍷 Quantités Consommées")
            st.caption("Volumes ou Unités réels")
            
            chart_conso = alt.Chart(df_conso).mark_bar(
                color="#E74C3C", # Rouge
                size=15 # Largeur des barres
            ).encode(
                x=alt.X('Full_Date:T', title='Temps', axis=alt.Axis(format='%d/%m %H:%M')),
                y=alt.Y('Intensité:Q', title='Quantité'),
                tooltip=['Date', 'Heure', 'Intensité', 'Pensées']
            ).interactive()
            
            st.altair_chart(chart_conso, use_container_width=True)

        if df_envie.empty and df_conso.empty:
            st.info("Pas assez de données pour afficher les graphiques.")

# --- ZONE DE SUPPRESSION (ONGLET 2) ---
        st.divider()
        with st.expander("🗑️ Supprimer une entrée depuis l'historique"):
            # 1. On trie les données (les plus récentes en haut)
            # On utilise le DF global pour avoir accès à tout
            df_history = st.session_state.data_addictions.sort_values(by=["Date", "Heure"], ascending=False)
            
            if not df_history.empty:
                # 2. Création des options
                options_history = {f"{row['Date']} - {row['Heure']} : {row['Substance']} ({row['Type']})": i for i, row in df_history.iterrows()}
                
                # 3. Menu de sélection
                choice_history = st.selectbox("Sélectionnez l'entrée à supprimer :", list(options_history.keys()), key="del_tab2", index=None)
                
                # 4. Bouton de confirmation
                if st.button("Confirmer la suppression", key="btn_del_tab2") and choice_history:
                    idx_to_drop = options_history[choice_history]
                    row_to_delete = df_history.loc[idx_to_drop]

                    # --- A. SUPPRESSION CLOUD ---
                    try:
                        from connect_db import delete_data_flexible
                        pid = st.session_state.get("patient_id", "Anonyme")
                        
                        success = delete_data_flexible("Addictions", {
                            "Patient": pid,
                            "Date": str(row_to_delete['Date']),
                            "Heure": str(row_to_delete['Heure']),
                            "Substance": str(row_to_delete['Substance'])
                        })
                        
                        if not success:
                             st.warning("⚠️ Ligne introuvable sur le Cloud.")

                    except Exception as e:
                        st.warning(f"Info Cloud : {e}")

                    # --- B. SUPPRESSION LOCALE ---
                    st.session_state.data_addictions = st.session_state.data_addictions.drop(idx_to_drop).reset_index(drop=True)
                    st.success("Entrée supprimée avec succès !")
                    st.rerun()
            else:
                st.info("Historique vide.")

    else:
        st.info(f"Aucune donnée enregistrée pour '{substance_active}'.")

st.divider()
st.page_link("streamlit_app.py", label="Retour à l'accueil", icon="🏠")

