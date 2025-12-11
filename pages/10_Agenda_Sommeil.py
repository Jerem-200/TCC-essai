import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, time

st.set_page_config(page_title="Agenda du Sommeil", page_icon="🌙")

# --- VIGILE ---
if "authentifie" not in st.session_state or not st.session_state.authentifie:
    # st.warning("⛔ Veuillez vous connecter sur la page d'accueil.")
    # st.switch_page("streamlit_app.py")
    # st.stop()
    pass

st.title("🌙 Agenda du Sommeil")
st.info("Remplissez ce formulaire chaque matin pour analyser la qualité de votre sommeil.")

# --- INITIALISATION ET CHARGEMENT ---
if "data_sommeil" not in st.session_state:
    # Colonnes officielles (Version Simple)
    cols_sommeil = [
        "Patient", "Date", "Sieste", "Medicaments", "Heure Coucher", "Latence", "Eveil", 
        "Heure Lever", "TTE", "TAL", "TTS", "Forme", "Qualité", "Efficacité"
    ]
    
    # Tentative de chargement Cloud
    try:
        from connect_db import load_data
        data_cloud = load_data("Sommeil") # Nom de l'onglet dans Google Sheet
    except:
        data_cloud = []

    if data_cloud:
        # On charge et on ne garde que les bonnes colonnes pour éviter les bugs
        df_cloud = pd.DataFrame(data_cloud)
        # On filtre pour ne garder que les colonnes qui existent dans le DF et qu'on attend
        cols_to_keep = [c for c in cols_sommeil if c in df_cloud.columns]
        st.session_state.data_sommeil = df_cloud[cols_to_keep]
    else:
        # Sinon vide
        st.session_state.data_sommeil = pd.DataFrame(columns=cols_sommeil)

# --- FONCTIONS DE CALCUL (Le cerveau mathématique) ---
def calculer_duree_minutes(heure_debut, heure_fin):
    """Calcule la différence en minutes entre deux heures, en gérant le passage à minuit"""
    h_deb = heure_debut.hour * 60 + heure_debut.minute
    h_fin = heure_fin.hour * 60 + heure_fin.minute
    
    if h_fin < h_deb: # Si on se lève le lendemain (ex: couché 23h, levé 7h)
        return (24 * 60 - h_deb) + h_fin
    else:
        return h_fin - h_deb

def format_minutes_en_h_m(minutes):
    """Transforme 90 minutes en '1h30'"""
    h = int(minutes // 60)
    m = int(minutes % 60)
    return f"{h}h{m:02d}"

# ==============================================================================
# ONGLETS : SAISIE vs ANALYSE
# ==============================================================================
tab1, tab2 = st.tabs(["📝 Saisie du jour", "📊 Analyse & Moyennes"])

# --- ONGLET 1 : FORMULAIRE ---
with tab1:
    st.subheader("Saisie de la nuit dernière")
    
    with st.form("form_sommeil"):
        col_date, col_vide = st.columns([1, 1])
        with col_date:
            date_nuit = st.date_input("Date du lever (Ce matin)", datetime.now())

        st.write("---")
        
        # 1 & 2 : Comportements
        st.write("**Habitudes de la veille**")
        c1, c2 = st.columns(2)
        with c1:
            sieste = st.text_input("1. Siestes hier (ex: 13h30 à 14h00)", placeholder="Heures")
        with c2:
            medics = st.text_input("2. Médicaments / Alcool (mg/verres)", placeholder="Détails")

        st.write("---")
        
        # 3 & 4 & 5 & 6 : Les Heures
        st.write("**Profil de sommeil**")
        
        col_coucher, col_lever = st.columns(2)
        with col_coucher:
            h_coucher = st.time_input("3. Heure de coucher (au lit)", time(23, 0))
            latence = st.number_input("4. Temps pour s'endormir (Latence) en minutes", 0, 300, 15, step=5, help="Combien de temps avez-vous mis à dormir après avoir éteint ?")
        
        with col_lever:
            h_lever = st.time_input("6. Heure de lever (sortie du lit)", time(7, 0))
            eveil_nocturne = st.number_input("5. Temps d'éveil au milieu de la nuit (Minutes totales)", 0, 300, 0, step=5, help="Si vous vous êtes réveillé, combien de temps au total ?")

        st.write("---")
        
        # 10 & 11 : Ressenti
        st.write("**Ressenti**")
        c_forme, c_qualite = st.columns(2)
        with c_forme:
            forme = st.slider("10. Forme au lever (1=Épuisé, 5=Reposé)", 1, 5, 3)
        with c_qualite:
            qualite = st.slider("11. Qualité du sommeil (1=Agité, 5=Profond)", 1, 5, 3)

        # BOUTON CALCUL & ENREGISTREMENT
        submitted = st.form_submit_button("Calculer et Enregistrer")

        if submitted:
            # --- CALCULS AUTOMATIQUES ---
            
            # 8. Temps au Lit (TAL) = Lever - Coucher
            tal_minutes = calculer_duree_minutes(h_coucher, h_lever)
            
            # 7. Temps Total Éveil (TTE) = Latence + Éveils nocturnes
            tte_minutes = latence + eveil_nocturne
            
            # 9. Temps Total Sommeil (TTS) = Au lit - Éveil
            tts_minutes = tal_minutes - tte_minutes
            
            # 12. Efficacité (ES) = (Sommeil / Lit) * 100
            if tal_minutes > 0:
                efficacite = round((tts_minutes / tal_minutes) * 100, 1)
            else:
                efficacite = 0

            # Affichage immédiat des résultats pour le patient
            st.success("✅ Données enregistrées !")
            
            res1, res2, res3, res4 = st.columns(4)
            res1.metric("Temps au lit", format_minutes_en_h_m(tal_minutes))
            res2.metric("Temps Sommeil", format_minutes_en_h_m(tts_minutes))
            res3.metric("Temps Éveil", format_minutes_en_h_m(tte_minutes))
            res4.metric("Efficacité", f"{efficacite} %", delta_color="normal" if efficacite > 85 else "inverse")

            # --- SAUVEGARDE ---
            
            # Local
            new_row = {
                "Date": str(date_nuit),
                "Sieste": sieste, "Medicaments": medics,
                "Heure Coucher": str(h_coucher)[:5], "Heure Lever": str(h_lever)[:5],
                "Latence": latence, "Eveil": eveil_nocturne,
                "TTE": format_minutes_en_h_m(tte_minutes),
                "TAL": format_minutes_en_h_m(tal_minutes),
                "TTS": format_minutes_en_h_m(tts_minutes),
                "Forme": forme, "Qualité": qualite, "Efficacité": efficacite
            }
            st.session_state.data_sommeil = pd.concat([st.session_state.data_sommeil, pd.DataFrame([new_row])], ignore_index=True)
            
            # Cloud
            try:
                from connect_db import save_data
                patient = st.session_state.get("patient_id", "Anonyme")
                
                # Ordre pour Excel : Patient, Date, Sieste, Meds, Coucher, Latence, EveilNoc, Lever, TTE, TAL, TTS, Forme, Qualite, Efficacite
                save_data("Sommeil", [
                    patient, str(date_nuit), sieste, medics, 
                    str(h_coucher)[:5], latence, eveil_nocturne, str(h_lever)[:5],
                    format_minutes_en_h_m(tte_minutes),
                    format_minutes_en_h_m(tal_minutes),
                    format_minutes_en_h_m(tts_minutes),
                    forme, qualite, f"{efficacite}%"
                ])
            except Exception as e:
                st.error(f"Erreur sauvegarde Cloud : {e}")

# --- ONGLET 2 : ANALYSE ---
with tab2:
    st.header("📊 Tableau de bord du sommeil")
    
    if not st.session_state.data_sommeil.empty:
        # On travaille sur une copie pour éviter les erreurs de modification
        df = st.session_state.data_sommeil.copy()
        
        # Affichage du tableau
        st.dataframe(df, use_container_width=True)
        
        st.divider()
        
        # Calcul des Moyennes (Sécurisé)
        try:
            eff_clean = pd.to_numeric(df["Efficacité"], errors='coerce')
            forme_clean = pd.to_numeric(df["Forme"], errors='coerce')
            
            avg_eff = eff_clean.mean()
            avg_forme = forme_clean.mean()
            
            if pd.notna(avg_eff) and pd.notna(avg_forme):
                c1, c2 = st.columns(2)
                c1.metric("Efficacité Moyenne", f"{avg_eff:.1f} %")
                c2.metric("Forme Moyenne", f"{avg_forme:.1f} / 5")
            else:
                st.info("Pas assez de données numériques valides pour les moyennes.")
                
        except Exception as e:
            st.warning(f"Impossible de calculer les moyennes : {e}")

        st.write("### Évolution de l'efficacité du sommeil")
        
        import altair as alt
        
        chart = alt.Chart(df).mark_line(point=True).encode(
            x='Date',
            y='Efficacité',
            tooltip=['Date', 'Efficacité', 'Forme']
        ).interactive()
        
        st.altair_chart(chart, use_container_width=True)

        # ZONE DE SUPPRESSION
        st.divider()
        with st.expander("🗑️ Supprimer une entrée depuis l'historique"):
            df_history = st.session_state.data_sommeil.sort_values(by="Date", ascending=False)
            
            options_history = {f"{row['Date']} (Eff: {row['Efficacité']}%)": i for i, row in df_history.iterrows()}
            
            choice_history = st.selectbox("Sélectionnez la nuit à supprimer :", list(options_history.keys()), key="del_tab2", index=None)
            
            if st.button("Confirmer la suppression", key="btn_del_tab2") and choice_history:
                idx_to_drop = options_history[choice_history]
                row_to_delete = df_history.loc[idx_to_drop]

                try:
                    from connect_db import delete_data_flexible
                    pid = st.session_state.get("patient_id", "Anonyme")
                    
                    success = delete_data_flexible("Sommeil", {
                        "Patient": pid,
                        "Date": str(row_to_delete['Date'])  
                    })
                    
                    if not success:
                        st.warning("⚠️ Ligne introuvable Cloud.")
                        
                except Exception as e:
                    st.warning(f"Erreur Cloud : {e}")

                st.session_state.data_sommeil = st.session_state.data_sommeil.drop(idx_to_drop).reset_index(drop=True)
                st.success("Entrée supprimée avec succès !")
                st.rerun()

    else:
        st.info("Remplissez l'agenda pour voir vos statistiques.")

st.divider()
st.page_link("streamlit_app.py", label="Retour à l'accueil", icon="🏠")