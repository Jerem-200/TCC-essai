import streamlit as st
import pandas as pd
import altair as alt # NOUVEAU : Nécessaire pour les points
from datetime import datetime, timedelta, time

st.set_page_config(page_title="Agenda du Sommeil", page_icon="🌙")

# --- VIGILE ---
if "authentifie" not in st.session_state or not st.session_state.authentifie:
    st.warning("⛔ Veuillez vous connecter sur la page d'accueil.")
    st.switch_page("streamlit_app.py")
    st.stop()

st.title("🌙 Agenda du Sommeil")
st.info("Remplissez ce formulaire chaque matin pour analyser la qualité de votre sommeil.")

# --- INITIALISATION ---
if "data_sommeil" not in st.session_state:
    st.session_state.data_sommeil = pd.DataFrame(columns=[
        "Date", "Sieste", "Medicaments", "Heure Coucher", "Latence", "Eveil Nocturne", 
        "Heure Lever", "TTE", "TAL", "TTS", "Forme", "Qualité", "Efficacité"
    ])

# --- FONCTIONS DE CALCUL ---
def calculer_duree_minutes(heure_debut, heure_fin):
    h_deb = heure_debut.hour * 60 + heure_debut.minute
    h_fin = heure_fin.hour * 60 + heure_fin.minute
    
    if h_fin < h_deb:
        return (24 * 60 - h_deb) + h_fin
    else:
        return h_fin - h_deb

def format_minutes_en_h_m(minutes):
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
        st.write("**Habitudes**")
        c1, c2 = st.columns(2)
        with c1: sieste = st.text_input("1. Siestes hier", placeholder="Non ou heures")
        with c2: medics = st.text_input("2. Médicaments / Alcool", placeholder="Non ou détails")

        st.write("---")
        
        # 3 à 6 : Horaires
        st.write("**Profil de sommeil**")
        col_coucher, col_lever = st.columns(2)
        with col_coucher:
            h_coucher = st.time_input("3. Heure de coucher", time(23, 0))
            latence = st.number_input("4. Latence (min)", 0, 300, 15, step=5)
        
        with col_lever:
            h_lever = st.time_input("6. Heure de lever", time(7, 0))
            eveil_nocturne = st.number_input("5. Éveils nocturnes (min)", 0, 300, 0, step=5)

        st.write("---")
        
        # 10 & 11 : Ressenti
        st.write("**Ressenti**")
        c_forme, c_qualite = st.columns(2)
        with c_forme: forme = st.slider("10. Forme (1=Épuisé, 5=Reposé)", 1, 5, 3)
        with c_qualite: qualite = st.slider("11. Qualité (1=Agité, 5=Profond)", 1, 5, 3)

        submitted = st.form_submit_button("Calculer et Enregistrer")

        if submitted:
            # Calculs
            tal_minutes = calculer_duree_minutes(h_coucher, h_lever)
            tte_minutes = latence + eveil_nocturne
            tts_minutes = tal_minutes - tte_minutes
            if tal_minutes > 0: efficacite = round((tts_minutes / tal_minutes) * 100, 1)
            else: efficacite = 0

            st.success("✅ Données enregistrées !")
            
            r1, r2, r3, r4 = st.columns(4)
            r1.metric("Au lit", format_minutes_en_h_m(tal_minutes))
            r2.metric("Sommeil", format_minutes_en_h_m(tts_minutes))
            r3.metric("Éveil", format_minutes_en_h_m(tte_minutes))
            r4.metric("Efficacité", f"{efficacite} %", delta_color="normal" if efficacite > 85 else "inverse")

            # Sauvegarde Locale
            new_row = {
                "Date": str(date_nuit),
                "Sieste": sieste, "Medicaments": medics,
                "Heure Coucher": str(h_coucher)[:5], "Heure Lever": str(h_lever)[:5],
                "Latence": latence, "Eveil Nocturne": eveil_nocturne,
                "TTE": format_minutes_en_h_m(tte_minutes),
                "TAL": format_minutes_en_h_m(tal_minutes),
                "TTS": format_minutes_en_h_m(tts_minutes),
                "Forme": forme, "Qualité": qualite, "Efficacité": efficacite
            }
            st.session_state.data_sommeil = pd.concat([st.session_state.data_sommeil, pd.DataFrame([new_row])], ignore_index=True)
            
            # Sauvegarde Cloud
            from connect_db import save_data
            patient = st.session_state.get("patient_id", "Anonyme")
            
            save_data("Sommeil", [
                patient, str(date_nuit), sieste, medics, 
                str(h_coucher)[:5], latence, eveil_nocturne, str(h_lever)[:5],
                format_minutes_en_h_m(tte_minutes),
                format_minutes_en_h_m(tal_minutes),
                format_minutes_en_h_m(tts_minutes),
                forme, qualite, f"{efficacite}%"
            ])

# --- ONGLET 2 : ANALYSE ---
with tab2:
    st.header("📊 Tableau de bord du sommeil")
    
    if not st.session_state.data_sommeil.empty:
        # Affichage du tableau brut
        st.dataframe(st.session_state.data_sommeil, use_container_width=True)
        st.divider()
        
        # --- PRÉPARATION DES DONNÉES POUR LE GRAPHIQUE ---
        # On crée une copie pour ne pas abîmer l'original
        df = st.session_state.data_sommeil.copy()
        
        # 1. NETTOYAGE : On enlève le '%' et on transforme en nombre
        # On force la conversion en string d'abord pour éviter les bugs, puis on remplace, puis on convertit en float
        try:
            df["Efficacité_Num"] = df["Efficacité"].astype(str).str.replace('%', '').astype(float)
            df["Forme_Num"] = pd.to_numeric(df["Forme"], errors='coerce')
        except:
            st.error("Erreur de conversion des données. Vérifiez le format.")
            st.stop()

        # 2. CALCUL DES MOYENNES
        avg_eff = df["Efficacité_Num"].mean()
        avg_forme = df["Forme_Num"].mean()
        
        c1, c2 = st.columns(2)
        c1.metric("Efficacité Moyenne", f"{avg_eff:.1f} %")
        c2.metric("Forme Moyenne", f"{avg_forme:.1f} / 5")
        
        st.write("### Évolution de l'efficacité du sommeil")
        
        # 3. GRAPHIQUE ALTAIR (Utilise la colonne nettoyée "Efficacité_Num")
        chart_sommeil = alt.Chart(df).mark_line(
            point=alt.OverlayMarkDef(size=150, filled=True, color="red") 
        ).encode(
            x=alt.X('Date:T', title='Date', axis=alt.Axis(format='%d/%m')),
            y=alt.Y('Efficacité_Num:Q', title='Efficacité (%)', scale=alt.Scale(domain=[0, 100])),
            tooltip=[
                alt.Tooltip('Date', title='Date', format='%d/%m/%Y'),
                alt.Tooltip('Efficacité_Num', title='Efficacité', format='.1f'),
                alt.Tooltip('Forme', title='Forme'),
                alt.Tooltip('Qualité', title='Qualité')
            ]
        ).interactive()
        
        st.altair_chart(chart_sommeil, use_container_width=True)
        
        st.caption("ℹ️ Une efficacité > 85% est considérée comme normale.")
        
    else:
        st.info("Remplissez l'agenda pour voir vos statistiques.")

st.divider()
st.page_link("streamlit_app.py", label="Retour à l'accueil", icon="🏠")