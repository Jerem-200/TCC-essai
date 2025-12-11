import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, time

st.set_page_config(page_title="Agenda du Sommeil", page_icon="🌙")

# --- VIGILE ---
if "authentifie" not in st.session_state or not st.session_state.authentifie:
    st.warning("⛔ Veuillez vous connecter sur la page d'accueil.")
    st.switch_page("streamlit_app.py")
    st.stop()

st.title("🌙 Agenda du Sommeil")
st.info("Remplissez ce formulaire chaque matin pour analyser la qualité de votre sommeil.")

# --- INITIALISATION ET CHARGEMENT ---
if "data_sommeil" not in st.session_state:
    # MISE À JOUR DES COLONNES
    cols_sommeil = [
        "Patient", "Date", "Sieste", 
        "Sport", "Cafeine", "Alcool", "Medic_Sommeil",
        "Heure Coucher", "Latence", "Eveil", 
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

if "sommeil_units" not in st.session_state:
    st.session_state.sommeil_units = ["Tasses", "Verres", "mg", "Comprimés", "ml", "Pintes"]

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
    st.subheader("📝 Saisie de la nuit dernière")
    
    # --- A. GESTION DES UNITÉS (HORS FORMULAIRE) ---
    with st.expander("⚙️ Gérer les unités (Verres, Tasses, mg...)"):
        st.caption("Ajoutez des unités pour vos consommations (ex: 'Bol', 'Gélule').")
        c_add, c_del = st.columns(2)
        
        with c_add:
            new_u = st.text_input("Nouvelle unité :", placeholder="ex: Bol", label_visibility="collapsed")
            if st.button("➕ Ajouter", key="btn_add_u_sommeil"):
                if new_u and new_u not in st.session_state.sommeil_units:
                    st.session_state.sommeil_units.append(new_u)
                    st.success(f"'{new_u}' ajouté !")
                    st.rerun()

        with c_del:
            if st.session_state.sommeil_units:
                del_u = st.selectbox("Supprimer :", st.session_state.sommeil_units, label_visibility="collapsed")
                if st.button("🗑️ Supprimer", key="btn_del_u_sommeil"):
                    if del_u in st.session_state.sommeil_units:
                        st.session_state.sommeil_units.remove(del_u)
                        st.rerun()

    # --- B. LE FORMULAIRE ---
    with st.form("form_sommeil"):
        # -- EN-TÊTE : DATE --
        c_date, _ = st.columns([1, 2])
        with c_date:
            date_nuit = st.date_input("Date du lever (Ce matin)", datetime.now())

        st.divider()
        
        # Listes horaires
        liste_heures_activites = ["Non"] + [f"{h}h{m:02d}" for h in range(24) for m in (0, 15, 30, 45)]
        liste_durees = ["15 min", "30 min", "45 min", "1h00", "1h30", "2h00", "3h+"]

        # =========================================================
        # 1. SIESTE & SPORT (Heure + Durée)
        # =========================================================
        st.markdown("### 🌞 Activités Physiques & Repos")
        
        # --- SIESTE ---
        col_s1, col_s2, col_s3 = st.columns([2, 1, 1])
        with col_s1:
            h_sieste = st.selectbox("💤 Sieste (Heure début)", liste_heures_activites, help="Heure de début")
        with col_s2:
            d_sieste = st.selectbox("Durée", liste_durees, key="d_sieste")
        with col_s3:
            st.empty() # Espace vide

        # --- SPORT ---
        col_sp1, col_sp2, col_sp3 = st.columns([2, 1, 1])
        with col_sp1:
            h_sport = st.selectbox("🏋️ Sport (Heure début)", liste_heures_activites, help="Heure de début de séance")
        with col_sp2:
            d_sport = st.selectbox("Durée", liste_durees, key="d_sport")
        with col_sp3:
            st.empty()

        st.write("") 
        
        # =========================================================
        # 2. CONSOMMATIONS (Heure + Qté + Unité)
        # =========================================================
        st.markdown("### 🍷 Consommations (Dernière prise)")
        
        # Fonction helper pour créer une ligne de consommation
        def ligne_conso(label, icon, key_prefix, default_unit_idx=0):
            c_h, c_qty, c_u = st.columns([2, 1, 1])
            with c_h:
                heure = st.selectbox(f"{icon} {label} (Heure)", liste_heures_activites, key=f"{key_prefix}_h")
            with c_qty:
                qty = st.number_input("Qté", min_value=0.0, step=0.5, key=f"{key_prefix}_q", label_visibility="visible")
            with c_u:
                # Sécurité si liste vide
                if not st.session_state.sommeil_units:
                    st.session_state.sommeil_units = ["Unités"]
                
                # Gestion index par défaut sécurisé
                safe_idx = default_unit_idx if default_unit_idx < len(st.session_state.sommeil_units) else 0
                unit = st.selectbox("Unité", st.session_state.sommeil_units, index=safe_idx, key=f"{key_prefix}_u", label_visibility="visible")
            return heure, qty, unit

        # Génération des 3 lignes
        h_cafe, q_cafe, u_cafe = ligne_conso("Caféine", "☕", "cafe", 0) # Index 0 = Tasses souvent
        h_alcool, q_alcool, u_alcool = ligne_conso("Alcool", "🍷", "alcool", 1) # Index 1 = Verres
        h_med, q_med, u_med = ligne_conso("Médicament", "💊", "med", 2) # Index 2 = mg/cp

        st.divider()

        # =========================================================
        # 3. LA NUIT (Reste inchangé mais propre)
        # =========================================================
        st.markdown("### 🌙 Votre Nuit")
        
        col_coucher, col_lever = st.columns(2)
        with col_coucher:
            st.info("**Au Coucher**")
            h_coucher = st.time_input("Heure au lit", time(23, 0))
            latence = st.number_input("Temps pour s'endormir (min)", 0, 300, 15, step=5)
        
        with col_lever:
            st.success("**Au Lever**")
            h_lever = st.time_input("Heure de sortie du lit", time(7, 0))
            eveil_nocturne = st.number_input("Temps d'éveil nocturne (min)", 0, 300, 0, step=5)

        st.write("")
        
        # =========================================================
        # 4. RESSENTI
        # =========================================================
        st.markdown("### ⭐ Bilan")
        c_forme, c_qualite = st.columns(2)
        with c_forme:
            forme = st.slider("🔋 Forme (1=HS, 5=Top)", 1, 5, 3)
        with c_qualite:
            qualite = st.slider("✨ Qualité Sommeil (1=Mauvais, 5=Top)", 1, 5, 3)

        st.write("")
        
        # BOUTON
        _, c_btn, _ = st.columns([1, 2, 1])
        with c_btn:
            submitted = st.form_submit_button("💾 Enregistrer ma nuit", use_container_width=True, type="primary")

        if submitted:
            # --- FORMATAGE DES DONNÉES EN TEXTE ---
            # Pour stocker proprement dans Excel sans multiplier les colonnes à l'infini
            
            # Sieste
            sieste_final = "Non" if h_sieste == "Non" else f"{h_sieste} ({d_sieste})"
            
            # Sport
            sport_final = "Non" if h_sport == "Non" else f"{h_sport} ({d_sport})"
            
            # Consos (Format: "14h00 - 2 Tasses")
            cafe_final = "Non" if h_cafe == "Non" else f"{h_cafe} - {q_cafe} {u_cafe}"
            alcool_final = "Non" if h_alcool == "Non" else f"{h_alcool} - {q_alcool} {u_alcool}"
            med_final = "Non" if h_med == "Non" else f"{h_med} - {q_med} {u_med}"

            # --- CALCULS ---
            tal_minutes = calculer_duree_minutes(h_coucher, h_lever)
            tte_minutes = latence + eveil_nocturne
            tts_minutes = tal_minutes - tte_minutes
            
            efficacite = round((tts_minutes / tal_minutes) * 100, 1) if tal_minutes > 0 else 0

            st.success("✅ Données enregistrées !")
            
            # Affichage rapide
            res1, res2, res3, res4 = st.columns(4)
            res1.metric("Au lit", format_minutes_en_h_m(tal_minutes))
            res2.metric("Sommeil", format_minutes_en_h_m(tts_minutes))
            res3.metric("Éveil", format_minutes_en_h_m(tte_minutes))
            res4.metric("Efficacité", f"{efficacite} %")

            # --- SAUVEGARDE ---
            new_row = {
                "Date": str(date_nuit),
                "Sieste": sieste_final,
                "Sport": sport_final, 
                "Cafeine": cafe_final, 
                "Alcool": alcool_final, 
                "Medic_Sommeil": med_final,
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
                
                save_data("Sommeil", [
                    patient, str(date_nuit), 
                    sieste_final, sport_final, cafe_final, alcool_final, med_final,
                    str(h_coucher)[:5], latence, eveil_nocturne, str(h_lever)[:5],
                    format_minutes_en_h_m(tte_minutes),
                    format_minutes_en_h_m(tal_minutes),
                    format_minutes_en_h_m(tts_minutes),
                    forme, qualite, f"{efficacite}%"
                ])
            except Exception as e:
                st.error(f"Erreur de sauvegarde Cloud : {e}")

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
        # On vérifie qu'il y a bien des chiffres avant de calculer
        try:
            # On revérifie la conversion au cas où
            eff_clean = pd.to_numeric(df["Efficacité"], errors='coerce')
            forme_clean = pd.to_numeric(df["Forme"], errors='coerce')
            
            avg_eff = eff_clean.mean()
            avg_forme = forme_clean.mean()
            
            # Affichage si les calculs ont réussi (pas de NaN)
            if pd.notna(avg_eff) and pd.notna(avg_forme):
                c1, c2 = st.columns(2)
                c1.metric("Efficacité Moyenne", f"{avg_eff:.1f} %")
                c2.metric("Forme Moyenne", f"{avg_forme:.1f} / 5")
            else:
                st.info("Pas assez de données numériques valides pour les moyennes.")
                
        except Exception as e:
            st.warning(f"Impossible de calculer les moyennes : {e}")

        st.write("### Évolution de l'efficacité du sommeil")
        
        # --- GRAPHIQUE AVEC POINTS ---
        import altair as alt
        
        # Le graphique simple mais avec des points (mark_point) sur la ligne (mark_line)
        chart = alt.Chart(df).mark_line(point=True).encode(
            x='Date',
            y='Efficacité',
            tooltip=['Date', 'Efficacité', 'Forme']
        ).interactive()
        
        st.altair_chart(chart, use_container_width=True)

# --- ZONE DE SUPPRESSION (ONGLET 2) ---
        st.divider()
        with st.expander("🗑️ Supprimer une entrée depuis l'historique"):
            # 1. On trie les données (les plus récentes en haut)
            df_history = st.session_state.data_sommeil.sort_values(by="Date", ascending=False)
            
            # 2. On crée les options pour le menu déroulant
            options_history = {f"{row['Date']} (Eff: {row['Efficacité']}%)": i for i, row in df_history.iterrows()}
            
            # 3. Le menu de sélection
            choice_history = st.selectbox("Sélectionnez la nuit à supprimer :", list(options_history.keys()), key="del_tab2", index=None)
            
            # 4. Le bouton de confirmation
            if st.button("Confirmer la suppression", key="btn_del_tab2") and choice_history:
                # Retrouver la ligne à supprimer
                idx_to_drop = options_history[choice_history]
                row_to_delete = df_history.loc[idx_to_drop]

                # --- A. SUPPRESSION CLOUD (Google Sheets) ---
                try:
                    from connect_db import delete_data_flexible
                    pid = st.session_state.get("patient_id", "Anonyme")
                    
                    # On appelle votre fonction avec les critères Patient + Date
                    # Les clés "Patient" et "Date" doivent correspondre aux titres de votre Excel
                    success = delete_data_flexible("Sommeil", {
                        "Patient": pid,
                        "Date": str(row_to_delete['Date'])  
                    })
                    
                    if not success:
                        st.warning("⚠️ Ligne introuvable dans le Cloud (Vérifiez les titres colonnes A et B dans Excel). Suppression locale effectuée.")
                        
                except Exception as e:
                    st.warning(f"Erreur Cloud : {e}")

                # --- B. SUPPRESSION LOCALE ---
                st.session_state.data_sommeil = st.session_state.data_sommeil.drop(idx_to_drop).reset_index(drop=True)
                
                st.success("Entrée supprimée avec succès !")
                st.rerun()

    else:
        st.info("Remplissez l'agenda pour voir vos statistiques.")

st.divider()
st.page_link("streamlit_app.py", label="Retour à l'accueil", icon="🏠")