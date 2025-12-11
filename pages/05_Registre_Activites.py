import streamlit as st
import pandas as pd
import altair as alt 
from datetime import datetime

st.set_page_config(page_title="Registre des Activités", page_icon="📝")

# --- VIGILE DE SÉCURITÉ SIMPLIFIÉ ---
if "authentifie" not in st.session_state or not st.session_state.authentifie:
    st.warning("🔒 Accès restreint. Veuillez entrer votre Code Patient sur l'accueil.")
    st.page_link("streamlit_app.py", label="Retourner à l'accueil pour se connecter", icon="🏠")
    st.stop() # Arrête le chargement du reste de la page

# Récupération du code patient pour les sauvegardes
patient_id = st.session_state.patient_id

st.title("📝 Registre des Activités")

# --- 2. INITIALISATION ET CHARGEMENT (ROBUSTE) ---

# A. CHARGEMENT DES ACTIVITÉS
if "data_activites" not in st.session_state:
    cols_act = ["Patient", "Date", "Heure", "Activité", "Plaisir (0-10)", "Maîtrise (0-10)", "Satisfaction (0-10)"]
    df_final_act = pd.DataFrame(columns=cols_act)
    
    try:
        from connect_db import load_data
        data_cloud = load_data("Activites") # Nom de l'onglet GSheet
        
        if data_cloud:
            df_cloud = pd.DataFrame(data_cloud)
            # Remplissage intelligent (Gestion Majuscules/Minuscules)
            for col in cols_act:
                if col in df_cloud.columns:
                    df_final_act[col] = df_cloud[col]
                elif col.lower() in df_cloud.columns:
                    df_final_act[col] = df_cloud[col.lower()]
            
            # Conversion numérique forcée pour les notes (évite les bugs graphiques)
            cols_num = ["Plaisir (0-10)", "Maîtrise (0-10)", "Satisfaction (0-10)"]
            for c in cols_num:
                if c in df_final_act.columns:
                    df_final_act[c] = pd.to_numeric(df_final_act[c], errors='coerce')

    except: pass
    st.session_state.data_activites = df_final_act

# B. CHARGEMENT DE L'HUMEUR
if "data_humeur_jour" not in st.session_state:
    cols_hum = ["Date", "Humeur Globale (0-10)"]
    df_final_hum = pd.DataFrame(columns=cols_hum)
    
    try:
        from connect_db import load_data
        data_cloud_hum = load_data("Humeur") # Nom de l'onglet GSheet
        
        if data_cloud_hum:
            df_cloud_hum = pd.DataFrame(data_cloud_hum)
            for col in cols_hum:
                if col in df_cloud_hum.columns:
                    df_final_hum[col] = df_cloud_hum[col]
                elif col.lower() in df_cloud_hum.columns:
                    df_final_hum[col] = df_cloud_hum[col.lower()]
            
            # Conversion numérique pour le graphique
            if "Humeur Globale (0-10)" in df_final_hum.columns:
                df_final_hum["Humeur Globale (0-10)"] = pd.to_numeric(df_final_hum["Humeur Globale (0-10)"], errors='coerce')

    except: pass
    st.session_state.data_humeur_jour = df_final_hum

# C. MÉMOIRES TEMPORAIRES (Heure/Minute)
if "memoire_h" not in st.session_state:
    st.session_state.memoire_h = datetime.now().hour
if "memoire_m" not in st.session_state:
    st.session_state.memoire_m = datetime.now().minute

# --- CRÉATION DES ONGLETS ---
tab1, tab2 = st.tabs(["📝 Saisie (Journal)", "📊 Résumé & Historique"])

# ==============================================================================
# ONGLET 1 : SAISIE (ACTIVITÉS + HUMEUR)
# ==============================================================================
with tab1:

    st.subheader("1. Ajouter une activité")

    with st.form("activity_form"):
        c_date, c_h, c_m = st.columns([2, 1, 1])
        with c_date:
            date_act = st.date_input("Date", datetime.now())
        with c_h:
            heure_h = st.number_input("Heure", min_value=0, max_value=23, value=st.session_state.memoire_h)
        with c_m:
            heure_m = st.number_input("Minute", min_value=0, max_value=59, value=st.session_state.memoire_m, step=5)

        activite_desc = st.text_input("Qu'avez-vous fait ?", placeholder="Ex: Petit déjeuner, Travail...")

        st.write("**Évaluation :**")
        c1, c2, c3 = st.columns(3)
        with c1: plaisir = st.slider("🎉 Plaisir", 0, 10, 5, help="Joie / Bien-être")
        with c2: maitrise = st.slider("💪 Maîtrise", 0, 10, 5, help="Compétence")
        with c3: satisfaction = st.slider("🏆 Satisfaction", 0, 10, 5, help="Accomplissement")

        submitted_act = st.form_submit_button("Ajouter l'activité")

        if submitted_act:
            heure_str = f"{heure_h:02d}:{heure_m:02d}"
            
            # Sauvegarde Locale
            new_row = {
                "Date": str(date_act), "Heure": heure_str, "Activité": activite_desc, 
                "Plaisir (0-10)": plaisir, "Maîtrise (0-10)": maitrise, "Satisfaction (0-10)": satisfaction
            }
            st.session_state.data_activites = pd.concat([st.session_state.data_activites, pd.DataFrame([new_row])], ignore_index=True)
            
            # Mise à jour mémoire heure
            st.session_state.memoire_h = heure_h
            st.session_state.memoire_m = heure_m
            
            # Sauvegarde Cloud
            from connect_db import save_data
            patient = st.session_state.get("patient_id", "Inconnu")
            save_data("Activites", [patient, str(date_act), heure_str, activite_desc, plaisir, maitrise, satisfaction])
            
            st.success(f"Activité ajoutée à {heure_str} !")

    st.divider()

    # --- AJOUT : SUPPRESSION RAPIDE ACTIVITÉ ---
    with st.expander("🗑️ Supprimer une activité (Erreur de saisie)"):
        df_act = st.session_state.data_activites
        if not df_act.empty:
            # Tri par date décroissante pour voir les dernières en premier
            df_act_sorted = df_act.sort_values(by=["Date", "Heure"], ascending=False)
            
            # Création de la liste déroulante
            options_act = {f"{row['Date']} à {row['Heure']} - {row['Activité']}": i for i, row in df_act_sorted.iterrows()}
            
            choice_act = st.selectbox("Choisir l'activité à effacer :", list(options_act.keys()), key="del_act_tab1", index=None, placeholder="Sélectionnez...")
            
            if st.button("Confirmer suppression activité", key="btn_del_act_tab1") and choice_act:
                idx = options_act[choice_act]
                row = df_act_sorted.loc[idx]
                
                # A. Suppression Cloud (CORRIGÉ AVEC VOS COLONNES)
                try:
                    from connect_db import delete_data_flexible
                    pid = st.session_state.get("patient_id", "Inconnu")
                    
                    # ICI : Les clés doivent être IDENTIQUES à votre Excel
                    delete_data_flexible("Activites", {
                        "Patient": pid,               # Au lieu de "patient_id"
                        "Date": str(row['Date']),     # Au lieu de "date"
                        "Heure": str(row['Heure']),   # Au lieu de "heure"
                        "Activité": row['Activité']   # Au lieu de "activite"
                    })
                except Exception as e:
                    pass
                
                # B. Suppression Locale
                st.session_state.data_activites = df_act.drop(idx).reset_index(drop=True)
                st.success("Activité supprimée !")
                st.rerun()
        else:
            st.info("Aucune activité récente à supprimer.")

# --- B. HUMEUR ---
    st.subheader("2. Bilan de la journée")
    
    # ⚠️ CORRECTIF ICI : Tout le bloc d'enregistrement reste groupé
    with st.form("humeur_form"):
        date_humeur = st.date_input("Date du bilan", datetime.now(), key="date_bilan")
        humeur_globale = st.slider("🌈 Humeur globale du jour (0-10)", 0, 10, 5)
        
        # Le bouton Submit doit être ICI, DANS le with st.form
        submitted_humeur = st.form_submit_button("Enregistrer l'humeur")
        
        if submitted_humeur:
            # Local
            new_humeur = {"Date": str(date_humeur), "Humeur Globale (0-10)": humeur_globale}
            st.session_state.data_humeur_jour = pd.concat([st.session_state.data_humeur_jour, pd.DataFrame([new_humeur])], ignore_index=True)
            
            # Cloud
            try:
                from connect_db import save_data
                patient = st.session_state.get("patient_id", "Inconnu")
                save_data("Humeur", [patient, str(date_humeur), humeur_globale])
                st.success("Humeur enregistrée !")
            except:
                st.success("Humeur enregistrée (Local) !")

    # --- SUPPRESSION HUMEUR (HORS DU FORMULAIRE) ---
    # On sort de l'indentation du st.form pour placer l'outil de suppression
    st.write("") 
    with st.expander("🗑️ Supprimer un relevé d'humeur"):
        df_hum = st.session_state.data_humeur_jour
        if not df_hum.empty:
            df_hum_sorted = df_hum.sort_values(by=["Date"], ascending=False)
            options_hum = {f"{row['Date']} - Note: {row['Humeur Globale (0-10)']}/10": i for i, row in df_hum_sorted.iterrows()}
            
            choice_hum = st.selectbox("Choisir l'humeur à effacer :", list(options_hum.keys()), key="del_hum_tab1", index=None, placeholder="Sélectionnez...")
            
            if st.button("Confirmer suppression humeur", key="btn_del_hum_tab1") and choice_hum:
                idx = options_hum[choice_hum]
                row = df_hum_sorted.loc[idx]
                
                # Cloud
                try:
                    from connect_db import delete_data_flexible
                    pid = st.session_state.get("patient_id", "Inconnu")
                    delete_data_flexible("Humeur", {
                        "Patient": pid, 
                        "Date": str(row['Date']), 
                        "Humeur Globale (0-10)": row['Humeur Globale (0-10)']
                    })
                except: pass
                
                # Local
                st.session_state.data_humeur_jour = df_hum.drop(idx).reset_index(drop=True)
                st.success("Humeur supprimée !")
                st.rerun()
        else:
            st.info("Aucun relevé d'humeur récent.")

            
# ==============================================================================
# ONGLET 2 : HISTORIQUE COMPLET & ANALYSE
# ==============================================================================
with tab2:
    st.header("Historique & Analyse")
    
    # 1. Vérification qu'il y a des données
    if not st.session_state.data_activites.empty and "Date" in st.session_state.data_activites.columns:
        
        # Récupération et Tri
        df_global = st.session_state.data_activites.sort_values(by=["Date", "Heure"], ascending=False).reset_index(drop=True)
        
        st.info("💡 Tableau modifiable : double-cliquez sur une case pour corriger.")
        
        # 2. TABLEAU ÉDITABLE (TOUT L'HISTORIQUE)
        edited_df = st.data_editor(
            df_global,
            use_container_width=True,
            num_rows="dynamic",
            key="editor_activites"
        )
        
        # Mise à jour si modification manuelle
        if not edited_df.equals(df_global):
            st.session_state.data_activites = edited_df
            st.rerun()

        st.divider()

        # 3. GRAPHIQUE : MOYENNES GLOBALES PAR ACTIVITÉ
        st.subheader("📊 Bilan : Moyennes par Activité")
        st.caption("Ce graphique fait la moyenne de toutes les fois où vous avez réalisé une même activité.")

        # --- PRÉPARATION DES DONNÉES AGRÉGÉES ---
        df_stats = df_global.copy()
        
        # Conversion en numérique
        cols_score = ["Plaisir (0-10)", "Maîtrise (0-10)", "Satisfaction (0-10)"]
        for col in cols_score: 
            df_stats[col] = pd.to_numeric(df_stats[col], errors='coerce')
        
        # Nettoyage : On enlève les activités vides si jamais
        df_stats = df_stats[df_stats["Activité"].notna() & (df_stats["Activité"] != "")]

        if not df_stats.empty:
            # --- CALCUL DES MOYENNES (GROUPBY) ---
            # On regroupe par nom d'activité et on fait la moyenne des scores
            df_grouped = df_stats.groupby("Activité")[cols_score].mean().reset_index()
            
            # Transformation format long pour Altair
            df_long = df_grouped.melt(
                id_vars=["Activité"], 
                value_vars=cols_score, 
                var_name="Indicateur", 
                value_name="Moyenne"
            )

            # --- CRÉATION DU CHART ---
            chart = alt.Chart(df_long).mark_bar().encode(
                x=alt.X('Activité:N', axis=alt.Axis(labelAngle=-45, title=None)), # Labels inclinés pour lisibilité
                y=alt.Y('Moyenne:Q', title='Note Moyenne (0-10)', scale=alt.Scale(domain=[0, 10])),
                color=alt.Color('Indicateur:N', legend=alt.Legend(orient="bottom", title="Critères")),
                xOffset='Indicateur:N', # Décale les barres pour qu'elles soient côte à côte
                tooltip=['Activité', 'Indicateur', alt.Tooltip('Moyenne', format='.1f')]
            ).properties(height=400)
            
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("Pas assez de données valides pour générer le graphique.")

        st.divider()
        
        # 4. ZONE DE SUPPRESSION (GLOBALE)
        with st.expander("🗑️ Supprimer une activité spécifique"):
            options_dict = {
                f"{row['Date']} à {row['Heure']} - {row['Activité']}": idx 
                for idx, row in df_global.iterrows()
            }
            
            selected_label = st.selectbox("Choisir l'activité à supprimer :", list(options_dict.keys()), index=None, placeholder="Sélectionnez une ligne...")
            
            if st.button("❌ Supprimer définitivement") and selected_label:
                index_to_drop = options_dict[selected_label]
                row_to_delete = df_global.loc[index_to_drop]
                
                # Suppression Cloud (CORRIGÉ)
                try:
                    from connect_db import delete_data_flexible
                    pid = st.session_state.get("patient_id", "Inconnu")
                    
                    delete_data_flexible("Activites", {
                        "Patient": pid,
                        "Date": str(row_to_delete['Date']),
                        "Heure": str(row_to_delete['Heure']),
                        "Activité": row_to_delete['Activité']
                    })
                except:
                    pass
                
                # Suppression Locale... (la suite ne change pas)
                
                # Suppression Locale
                st.session_state.data_activites = df_global.drop(index_to_drop).reset_index(drop=True)
                st.success("Activité supprimée !")
                st.rerun()

    else:
        st.info("Aucune activité enregistrée pour le moment.")

# =========================================================
    # NOUVEAU : GRAPHIQUE D'ÉVOLUTION DE L'HUMEUR (CORRIGÉ)
    # =========================================================
    st.divider()
    st.subheader("🌈 Évolution de l'Humeur")
    
    # 1. Récupération sécurisée
    df_humeur = st.session_state.get("data_humeur_jour", pd.DataFrame())
    
    # On vérifie qu'on a bien les colonnes nécessaires
    if not df_humeur.empty and "Date" in df_humeur.columns and "Humeur Globale (0-10)" in df_humeur.columns:
        
        # 2. Nettoyage des données pour le graphique (Copie pour ne pas casser l'original)
        df_chart_humeur = df_humeur.copy()
        
        # Conversion Date (Indispensable pour l'axe X temporel)
        df_chart_humeur["Date"] = pd.to_datetime(df_chart_humeur["Date"], errors='coerce')
        
        # Conversion Humeur en nombre (Indispensable pour l'axe Y)
        df_chart_humeur["Humeur Globale (0-10)"] = pd.to_numeric(df_chart_humeur["Humeur Globale (0-10)"], errors='coerce')
        
        # On supprime les lignes où la date ou la note sont invalides (NaN)
        df_chart_humeur = df_chart_humeur.dropna(subset=["Date", "Humeur Globale (0-10)"])
        
        # Tri chronologique
        df_chart_humeur = df_chart_humeur.sort_values("Date")
        
        if not df_chart_humeur.empty:
            # 3. Création du graphique
            chart_humeur = alt.Chart(df_chart_humeur).mark_line(
                point=alt.OverlayMarkDef(size=100, filled=True, color="#FFA500"), # Points oranges
                color="#FFA500" # Ligne orange
            ).encode(
                # Axe X : Temps
                x=alt.X('Date:T', title='Date', axis=alt.Axis(format='%d/%m')),
                # Axe Y : Note de 0 à 10
                y=alt.Y('Humeur Globale (0-10):Q', title='Humeur (0-10)', scale=alt.Scale(domain=[0, 10])),
                # Tooltip au survol
                tooltip=[
                    alt.Tooltip('Date', format='%d/%m/%Y', title='Date'), 
                    alt.Tooltip('Humeur Globale (0-10)', title='Note')
                ]
            ).properties(
                height=300,
                title="Suivi de l'humeur quotidienne"
            ).interactive()
            
            st.altair_chart(chart_humeur, use_container_width=True)
        else:
            st.info("Données d'humeur présentes mais format invalide pour le graphique.")
            
    else:
        st.info("Pas encore de données d'humeur enregistrées pour afficher le graphique.")

    # --- AJOUT : ZONE DE SUPPRESSION HUMEUR (ONGLET 2) ---
    st.write("")
    with st.expander("🗑️ Supprimer un relevé d'humeur depuis l'historique"):
        # 1. On récupère les données
        df_hum_hist = st.session_state.get("data_humeur_jour", pd.DataFrame())
        
        if not df_hum_hist.empty:
            # 2. On trie pour afficher les plus récents en premier
            df_hum_sorted = df_hum_hist.sort_values(by="Date", ascending=False)
            
            # 3. Création du menu déroulant
            # On crée un dictionnaire : { "Texte à afficher" : index_du_dataframe }
            options_hum_hist = {
                f"📅 {row['Date']} : {row['Humeur Globale (0-10)']}/10": i 
                for i, row in df_hum_sorted.iterrows()
            }
            
            choice_hum_hist = st.selectbox(
                "Sélectionnez la date à corriger :", 
                list(options_hum_hist.keys()), 
                key="del_hum_tab2", # Clé unique pour éviter conflit avec l'onglet 1
                index=None,
                placeholder="Choisir une entrée..."
            )
            
            # 4. Bouton de suppression
            if st.button("❌ Supprimer définitivement", key="btn_del_hum_tab2"):
                if choice_hum_hist:
                    idx_to_drop = options_hum_hist[choice_hum_hist]
                    row_to_del = df_hum_sorted.loc[idx_to_drop]
                    
                    # A. Suppression Cloud
                    try:
                        from connect_db import delete_data_flexible
                        pid = st.session_state.get("patient_id", "Inconnu")
                        
                        delete_data_flexible("Humeur", {
                            "Patient": pid,
                            "Date": str(row_to_del['Date']),
                            "Humeur Globale (0-10)": row_to_del['Humeur Globale (0-10)']
                        })
                    except Exception as e:
                        # On continue même si erreur cloud (pour le local)
                        pass

                    # B. Suppression Locale
                    st.session_state.data_humeur_jour = df_hum_hist.drop(idx_to_drop).reset_index(drop=True)
                    
                    st.success("Entrée supprimée avec succès !")
                    st.rerun()
        else:
            st.info("Aucun historique d'humeur à supprimer.")

st.divider()
st.page_link("streamlit_app.py", label="Retour à l'accueil", icon="🏠")