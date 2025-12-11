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
                st.error("⚠️ Veuillez sélectionner une unité (utilisez la gestion des unités si la liste est vide).")
            else:
                # B. FORMATAGE & MÉMOIRE
                heure_str = heure_evt.strftime("%H:%M")
                st.session_state.memoire_heure = heure_evt
                
                if "CONSOMMÉ" in type_evt:
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
                    pid = st.session_state.get("patient_id", "Anonyme")
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
with tab2:
    st.header(f"Historique : {substance_active}")
    
    # 1. FILTRAGE ET PRÉPARATION
    df_global = st.session_state.data_addictions
    
    # On filtre pour la substance active
    df_filtre = df_global[df_global["Substance"] == substance_active].sort_values(by=["Date", "Heure"], ascending=False).reset_index(drop=True)
    
    if not df_filtre.empty:
        st.info("💡 Vous pouvez modifier les valeurs directement dans le tableau (sauf Patient et Substance).")
        
        # 2. TABLEAU ÉDITABLE COMPLET
        # On affiche toutes les colonnes demandées
        edited_df = st.data_editor(
            df_filtre, 
            column_order=["Patient", "Date", "Heure", "Substance", "Type", "Intensité", "Pensées"], 
            disabled=["Substance"], # On empêche de modifier ces 2 colonnes pour éviter les bugs de tri
            use_container_width=True, 
            num_rows="dynamic",
            key=f"editor_{substance_active}"
        )
        
        # MISE À JOUR DE LA MÉMOIRE SI CHANGEMENT
        if not edited_df.equals(df_filtre):
            # 1. On sépare ce qui n'a pas bougé (les autres substances)
            df_others = df_global[df_global["Substance"] != substance_active]
            
            # 2. On s'assure que la substance reste la bonne (sécurité)
            edited_df["Substance"] = substance_active
            
            # 3. On fusionne le tout
            st.session_state.data_addictions = pd.concat([df_others, edited_df], ignore_index=True)
            st.rerun()

        st.divider()
        st.write(f"### Évolution : {substance_active}")

        # --- PRÉPARATION DES DONNÉES POUR LE GRAPHIQUE ---
        df_chart = edited_df.copy()
        
        # 1. Conversion Date/Heure
        try:
            df_chart['Full_Date'] = pd.to_datetime(
                df_chart['Date'].astype(str) + ' ' + df_chart['Heure'].astype(str), 
                format="%Y-%m-%d %H:%M", errors='coerce'
            )
            # Fallback si erreur
            mask_error = df_chart['Full_Date'].isna()
            if mask_error.any():
                 df_chart.loc[mask_error, 'Full_Date'] = pd.to_datetime(df_chart.loc[mask_error, 'Date'], errors='coerce')
        except:
            df_chart['Full_Date'] = pd.to_datetime(df_chart['Date'], errors='coerce')

        # 2. Conversion Chiffres
        if "Intensité" in df_chart.columns:
            df_chart['Intensité'] = df_chart['Intensité'].astype(str).str.replace(',', '.')
            df_chart['Intensité'] = pd.to_numeric(df_chart['Intensité'], errors='coerce')
        
        # 3. SÉPARATION DES TYPES
        df_envie = df_chart[df_chart["Type"].str.contains("ENVIE", na=False)]
        df_conso = df_chart[df_chart["Type"].str.contains("CONSOMMÉ", na=False)]

        # --- GRAPHIQUE 1 : LES ENVIES ---
        if not df_envie.empty:
            st.subheader("⚡ Évolution des Envies (Craving)")
            chart_envie = alt.Chart(df_envie).mark_line(
                point=alt.OverlayMarkDef(size=100, filled=True, color="#9B59B6")
            ).encode(
                x=alt.X('Full_Date:T', title='Temps', axis=alt.Axis(format='%d/%m %H:%M')),
                y=alt.Y('Intensité:Q', title='Intensité (0-10)', scale=alt.Scale(domain=[0, 10])),
                color=alt.value("#9B59B6"),
                tooltip=['Date', 'Heure', 'Intensité', 'Pensées']
            ).interactive()
            st.altair_chart(chart_envie, use_container_width=True)
        
        # --- GRAPHIQUE 2 : LES CONSOMMATIONS ---
        if not df_conso.empty:
            st.subheader("🍷 Quantités Consommées")
            chart_conso = alt.Chart(df_conso).mark_bar(
                color="#E74C3C", size=15
            ).encode(
                x=alt.X('Full_Date:T', title='Temps', axis=alt.Axis(format='%d/%m %H:%M')),
                y=alt.Y('Intensité:Q', title='Quantité'),
                tooltip=['Date', 'Heure', 'Intensité', 'Pensées']
            ).interactive()
            st.altair_chart(chart_conso, use_container_width=True)

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
                        pid = st.session_state.get("patient_id", "Anonyme")
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

