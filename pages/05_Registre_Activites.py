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
# ONGLET 2 : HISTORIQUE COMPLET (Tableau Global)
# ==============================================================================
with tab2:
    st.header("Historique de toutes les activités")
    
    # 1. Récupération de TOUT le dataframe
    if not st.session_state.data_activites.empty and "Date" in st.session_state.data_activites.columns:
        
        # Tri : Du plus récent au plus ancien
        df_global = st.session_state.data_activites.sort_values(by=["Date", "Heure"], ascending=False).reset_index(drop=True)
        
        st.info("💡 Vous pouvez modifier les valeurs directement dans le tableau ci-dessous.")
        
        # 2. Tableau Éditable (Toutes les données)
        edited_df = st.data_editor(
            df_global,
            use_container_width=True,
            num_rows="dynamic",
            key="editor_activites"
        )
        
        # Mise à jour si modification manuelle dans le tableau
        if not edited_df.equals(df_global):
            st.session_state.data_activites = edited_df
            st.rerun()

        st.divider()
        
        # 3. Zone de Suppression (Globale)
        with st.expander("🗑️ Supprimer une activité spécifique"):
            # Création d'une liste lisible pour la suppression
            # On inclut la date pour différencier les jours
            options_dict = {
                f"{row['Date']} à {row['Heure']} - {row['Activité']}": idx 
                for idx, row in df_global.iterrows()
            }
            
            selected_label = st.selectbox("Choisir l'activité à supprimer :", list(options_dict.keys()), index=None, placeholder="Sélectionnez une ligne...")
            
            if st.button("❌ Supprimer définitivement") and selected_label:
                # Retrouver l'index dans le DF édité
                index_to_drop = options_dict[selected_label]
                row_to_delete = df_global.loc[index_to_drop]
                
                # A. Suppression Cloud
                try:
                    from connect_db import delete_data
                    patient_id = st.session_state.get("patient_id", "Inconnu")
                    # On suppose que delete_data est configuré pour gérer aussi la table "Activites"
                    # Il faudra peut-être adapter delete_data pour accepter 'Activité' comme critère si ce n'est pas fait
                    # Ici on envoie les clés principales
                    # Attention : Assurez-vous que votre delete_data gère la table Activites
                    # Sinon, il faudra l'adapter.
                    pass 
                except:
                    pass
                
                # B. Suppression Locale
                # On supprime la ligne correspondante
                st.session_state.data_activites = df_global.drop(index_to_drop).reset_index(drop=True)
                st.success("Activité supprimée !")
                st.rerun()

        # 4. Petit bonus : Graphique sur une journée spécifique (Optionnel mais pratique)
        st.divider()
        st.subheader("🔎 Zoom sur une journée")
        date_zoom = st.date_input("Voir les stats du :", datetime.now())
        
        df_zoom = df_global[df_global["Date"] == str(date_zoom)]
        
        if not df_zoom.empty:
            df_chart = df_zoom.copy()
            cols_score = ["Plaisir (0-10)", "Maîtrise (0-10)", "Satisfaction (0-10)"]
            for col in cols_score: df_chart[col] = pd.to_numeric(df_chart[col], errors='coerce')

            df_grouped = df_chart.groupby("Activité")[cols_score].mean().reset_index()
            df_long = df_grouped.melt(id_vars=["Activité"], value_vars=cols_score, var_name="Indicateur", value_name="Score")

            chart = alt.Chart(df_long).mark_bar().encode(
                x=alt.X('Activité:N', title=None, axis=alt.Axis(labelAngle=0)), 
                y=alt.Y('Score:Q', title='Note (0-10)', scale=alt.Scale(domain=[0, 10])),
                color=alt.Color('Indicateur:N', legend=alt.Legend(orient="bottom")),
                xOffset='Indicateur:N',
                tooltip=['Activité', 'Indicateur', alt.Tooltip('Score', format='.1f')]
            ).properties(height=350)
            st.altair_chart(chart, use_container_width=True)
        else:
            st.caption(f"Pas de données pour le {date_zoom.strftime('%d/%m/%Y')}.")

    else:
        st.info("Aucune activité enregistrée pour le moment.")

st.divider()
st.page_link("streamlit_app.py", label="Retour à l'accueil", icon="🏠")