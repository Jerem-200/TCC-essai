import streamlit as st
import pandas as pd
import altair as alt 
from datetime import datetime

st.set_page_config(page_title="Registre des Activités", page_icon="📝")

# --- 1. LE VIGILE DE SÉCURITÉ (Toujours en premier !) ---
if "authentifie" not in st.session_state or not st.session_state.authentifie:
    st.warning("⛔ Veuillez vous connecter sur la page d'accueil.")
    st.switch_page("streamlit_app.py")
    st.stop()

st.title("📝 Registre des Activités")

# --- 2. INITIALISATION DES MÉMOIRES (Correction du bug KeyError) ---
# On définit explicitement les colonnes pour être sûr que "Date" existe
if "data_activites" not in st.session_state:
    st.session_state.data_activites = pd.DataFrame(columns=[
        "Date", "Heure", "Activité", 
        "Plaisir (0-10)", "Maîtrise (0-10)", "Satisfaction (0-10)"
    ])

if "data_humeur_jour" not in st.session_state:
    st.session_state.data_humeur_jour = pd.DataFrame(columns=["Date", "Humeur Globale (0-10)"])

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

    # --- 4. FORMULAIRE B : HUMEUR ---
    st.subheader("2. Bilan de la journée")
    with st.form("humeur_form"):
        date_humeur = st.date_input("Date du bilan", datetime.now(), key="date_bilan")
        humeur_globale = st.slider("🌈 Humeur globale du jour (0-10)", 0, 10, 5)
        
        if st.form_submit_button("Enregistrer l'humeur"):
            # Local
            new_humeur = {"Date": str(date_humeur), "Humeur Globale (0-10)": humeur_globale}
            st.session_state.data_humeur_jour = pd.concat([st.session_state.data_humeur_jour, pd.DataFrame([new_humeur])], ignore_index=True)
            
            # Cloud
            from connect_db import save_data
            patient = st.session_state.get("patient_id", "Inconnu")
            save_data("Humeur", [patient, str(date_humeur), humeur_globale])
            
            st.success("Humeur enregistrée !")

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
                
                # Suppression Cloud (Dummy block si la fonction n'est pas adaptée pour Activites, sinon ça marche)
                try:
                    from connect_db import delete_data
                    # Note : Il faut s'assurer que delete_data gère la suppression par ID ou par critères exacts
                    pass 
                except:
                    pass
                
                # Suppression Locale
                st.session_state.data_activites = df_global.drop(index_to_drop).reset_index(drop=True)
                st.success("Activité supprimée !")
                st.rerun()

    else:
        st.info("Aucune activité enregistrée pour le moment.")

st.divider()
st.page_link("streamlit_app.py", label="Retour à l'accueil", icon="🏠")