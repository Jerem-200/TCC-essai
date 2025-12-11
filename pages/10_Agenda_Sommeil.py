import streamlit as st
import pandas as pd
from datetime import datetime, time

st.set_page_config(page_title="Agenda du Sommeil", page_icon="🌙")

# --- VIGILE DE SÉCURITÉ ---
if "authentifie" not in st.session_state or not st.session_state.authentifie:
    # st.warning("⛔ Veuillez vous connecter sur la page d'accueil.")
    # st.switch_page("streamlit_app.py")
    # st.stop()
    pass 

st.title("🌙 Agenda du Sommeil")
st.info("Remplissez ce formulaire chaque matin pour analyser la qualité de votre sommeil.")

# ==============================================================================
# 1. INITIALISATION ET CHARGEMENT CLOUD SÉCURISÉ
# ==============================================================================
if "data_sommeil" not in st.session_state:
    # Les colonnes de la version "Simple"
    cols_sommeil = [
        "Patient", "Date", "Sieste", "Medicaments", "Heure Coucher", "Latence", "Eveil", 
        "Heure Lever", "TTE", "TAL", "TTS", "Forme", "Qualité", "Efficacité"
    ]
    
    # 1. Création d'un tableau vide propre (pour éviter les erreurs si le cloud est vide)
    df_final = pd.DataFrame(columns=cols_sommeil)
    
    # 2. Chargement depuis le Cloud
    try:
        from connect_db import load_data
        data_cloud = load_data("Sommeil") # Assurez-vous que l'onglet Google Sheet s'appelle "Sommeil"
        
        if data_cloud:
            df_cloud = pd.DataFrame(data_cloud)
            
            # 3. Fusion Intelligente : On ne remplit que les colonnes qui existent
            for col in cols_sommeil:
                if col in df_cloud.columns:
                    df_final[col] = df_cloud[col]
                    
    except Exception as e:
        st.warning(f"Info connexion : {e}")

    # 4. Enregistrement en mémoire session
    st.session_state.data_sommeil = df_final


# --- FONCTIONS DE CALCUL ---
def calculer_duree_minutes(heure_debut, heure_fin):
    """Calcule la durée en minutes entre deux heures (gère minuit)"""
    h_deb = heure_debut.hour * 60 + heure_debut.minute
    h_fin = heure_fin.hour * 60 + heure_fin.minute
    
    if h_fin < h_deb: # Si nuit à cheval sur deux jours
        return (24 * 60 - h_deb) + h_fin
    else:
        return h_fin - h_deb

def format_minutes_en_h_m(minutes):
    """Affiche '1h30' au lieu de 90 min"""
    h = int(minutes // 60)
    m = int(minutes % 60)
    return f"{h}h{m:02d}"

# ==============================================================================
# ONGLETS : SAISIE vs ANALYSE
# ==============================================================================
tab1, tab2 = st.tabs(["📝 Saisie du jour", "📊 Analyse & Moyennes"])

# --- ONGLET 1 : FORMULAIRE SIMPLE ---
with tab1:
    st.subheader("Saisie de la nuit dernière")
    
    with st.form("form_sommeil"):
        col_date, col_vide = st.columns([1, 1])
        with col_date:
            date_nuit = st.date_input("Date du lever (Ce matin)", datetime.now())

        st.write("---")
        
        # BLOC 1 : Habitudes
        st.write("**Habitudes de la veille**")
        c1, c2 = st.columns(2)
        with c1:
            sieste = st.text_input("1. Siestes hier (ex: 13h30 - 20min)", placeholder="Heures / Durée")
        with c2:
            medics = st.text_input("2. Médicaments / Alcool", placeholder="ex: 1 verre de vin, 1 somnifère")

        st.write("---")
        
        # BLOC 2 : Horaires
        st.write("**Profil de sommeil**")
        
        col_coucher, col_lever = st.columns(2)
        with col_coucher:
            h_coucher = st.time_input("3. Heure de coucher (au lit)", time(23, 0))
            latence = st.number_input("4. Temps pour s'endormir (Latence) en minutes", 0, 300, 15, step=5)
        
        with col_lever:
            h_lever = st.time_input("6. Heure de lever (sortie du lit)", time(7, 0))
            eveil_nocturne = st.number_input("5. Temps d'éveil nocturne (Minutes totales)", 0, 300, 0, step=5)

        st.write("---")
        
        # BLOC 3 : Ressenti
        st.write("**Ressenti**")
        c_forme, c_qualite = st.columns(2)
        with c_forme:
            forme = st.slider("10. Forme au lever (1=HS, 5=Top)", 1, 5, 3)
        with c_qualite:
            qualite = st.slider("11. Qualité du sommeil (1=Mauvais, 5=Bon)", 1, 5, 3)

        # BOUTON ENREGISTRER
        submitted = st.form_submit_button("Calculer et Enregistrer")

        if submitted:
            # --- CALCULS ---
            tal_minutes = calculer_duree_minutes(h_coucher, h_lever) # Temps au Lit
            tte_minutes = latence + eveil_nocturne # Temps Éveillé
            tts_minutes = tal_minutes - tte_minutes # Temps Sommeil
            
            # Efficacité
            if tal_minutes > 0:
                efficacite = round((tts_minutes / tal_minutes) * 100, 1)
            else:
                efficacite = 0

            st.success("✅ Données enregistrées !")
            
            # Affichage rapide résultats
            res1, res2, res3, res4 = st.columns(4)
            res1.metric("Temps au lit", format_minutes_en_h_m(tal_minutes))
            res2.metric("Temps Sommeil", format_minutes_en_h_m(tts_minutes))
            res3.metric("Temps Éveil", format_minutes_en_h_m(tte_minutes))
            res4.metric("Efficacité", f"{efficacite} %", delta_color="normal" if efficacite > 85 else "inverse")

            # --- SAUVEGARDE LOCALE ET CLOUD ---
            
            # 1. Mise à jour Locale
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
            
            # 2. Envoi Cloud
            try:
                from connect_db import save_data
                patient = st.session_state.get("patient_id", "Anonyme")
                
                # Ordre strict pour Excel
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
        df = st.session_state.data_sommeil.copy()
        
        # Tableau
        st.dataframe(df, use_container_width=True)
        st.divider()
        
        # Moyennes
        try:
            eff_clean = pd.to_numeric(df["Efficacité"], errors='coerce')
            forme_clean = pd.to_numeric(df["Forme"], errors='coerce')
            
            avg_eff = eff_clean.mean()
            avg_forme = forme_clean.mean()
            
            if pd.notna(avg_eff):
                c1, c2 = st.columns(2)
                c1.metric("Efficacité Moyenne", f"{avg_eff:.1f} %")
                c2.metric("Forme Moyenne", f"{avg_forme:.1f} / 5")
        except:
            pass

        # Graphique
        st.write("### Évolution de l'efficacité")
        import altair as alt
        chart = alt.Chart(df).mark_line(point=True).encode(
            x='Date', y='Efficacité', tooltip=['Date', 'Efficacité', 'Forme']
        ).interactive()
        st.altair_chart(chart, use_container_width=True)

        # Suppression
        st.divider()
        with st.expander("🗑️ Supprimer une entrée"):
            df_hist = st.session_state.data_sommeil.sort_values(by="Date", ascending=False)
            opt_hist = {f"{row['Date']} (Eff: {row['Efficacité']}%)": i for i, row in df_hist.iterrows()}
            
            choix = st.selectbox("Sélectionnez la nuit :", list(opt_hist.keys()), key="del_tab2", index=None)
            
            if st.button("Confirmer suppression", key="btn_del"):
                idx = opt_hist[choix]
                row = df_hist.loc[idx]
                
                try:
                    from connect_db import delete_data_flexible
                    pid = st.session_state.get("patient_id", "Anonyme")
                    delete_data_flexible("Sommeil", {"Patient": pid, "Date": str(row['Date'])})
                except: pass
                
                st.session_state.data_sommeil = st.session_state.data_sommeil.drop(idx).reset_index(drop=True)
                st.success("Supprimé !")
                st.rerun()
    else:
        st.info("Aucune donnée pour le moment.")

st.divider()
st.page_link("streamlit_app.py", label="Retour à l'accueil", icon="🏠")