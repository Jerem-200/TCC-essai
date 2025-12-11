import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, time 

st.set_page_config(page_title="Agenda Consos", page_icon="🍷")

# --- VIGILE DE SÉCURITÉ ---
if "authentifie" not in st.session_state or not st.session_state.authentifie:
    # st.warning("⛔ Veuillez vous connecter sur la page d'accueil.")
    # st.switch_page("streamlit_app.py")
    # st.stop()
    pass 

st.title("🍷 Agenda des Envies & Consommations")
st.info("Notez vos envies (craving) et vos consommations pour identifier les déclencheurs.")

# ==============================================================================
# 1. INITIALISATION
# ==============================================================================

# A. Liste des substances
if "liste_substances" not in st.session_state:
    st.session_state.liste_substances = []

# B. Liste des unités (NOUVEAU)
if "liste_unites" not in st.session_state:
    st.session_state.liste_unites = ["Verres", "Cigarettes", "Joints", "ml", "cl", "grammes", "Pintes", "Shots"]

# C. Chargement des données
if "data_addictions" not in st.session_state:
    cols_conso = ["Patient", "Date", "Heure", "Substance", "Type", "Intensité", "Pensées"]
    df_final = pd.DataFrame(columns=cols_conso)
    
    try:
        from connect_db import load_data
        data_cloud = load_data("Addictions") 
        
        if data_cloud:
            df_cloud = pd.DataFrame(data_cloud)
            for col in cols_conso:
                if col in df_cloud.columns:
                    df_final[col] = df_cloud[col]
                elif col.lower() in df_cloud.columns:
                    df_final[col] = df_cloud[col.lower()]
            
            if "Intensité" in df_final.columns:
                df_final["Intensité"] = df_final["Intensité"].astype(str).str.replace(',', '.')
                df_final["Intensité"] = pd.to_numeric(df_final["Intensité"], errors='coerce')

    except Exception as e:
        pass

    st.session_state.data_addictions = df_final

    # D. Remplissage intelligent des substances depuis l'historique
    if not df_final.empty and "Substance" in df_final.columns:
        subs_history = df_final["Substance"].dropna().unique().tolist()
        for s in subs_history:
            s_propre = str(s).strip()
            if s_propre and s_propre not in st.session_state.liste_substances:
                st.session_state.liste_substances.append(s_propre)

# --- MEMOIRE INTELLIGENTE ---
if "memoire_heure" not in st.session_state:
    st.session_state.memoire_heure = time(12, 00)
if "memoire_unite" not in st.session_state:
    st.session_state.memoire_unite = "Verres" # Valeur par défaut

# ==============================================================================
# ZONE DE SÉLECTION
# ==============================================================================
col_info, col_sel = st.columns([2, 2])
with col_info:
    st.write("**De quoi voulez-vous faire le suivi ?**")

with col_sel:
    with st.popover("➕ Nouvelle Substance/Comportement"):
        new_sub = st.text_input("Nom (ex: Alcool, Tabac, Jeux...)")
        if st.button("Créer") and new_sub:
            if new_sub not in st.session_state.liste_substances:
                st.session_state.liste_substances.append(new_sub)
                st.rerun()

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
    
    type_evt = st.radio(
        "Qu'est-ce qui s'est passé ?", 
        ["⚡ J'ai eu une ENVIE (Craving)", "🍷 J'ai CONSOMMÉ"], 
        horizontal=True
    )
    
    with st.form("form_addiction"):
        c_date, c_heure = st.columns(2)
        with c_date: 
            date_evt = st.date_input("Date", datetime.now())
        with c_heure: 
            heure_evt = st.time_input("Heure", value=st.session_state.memoire_heure)
            
        st.divider()
        
        valeur_numerique = 0.0
        
        if "ENVIE" in type_evt:
            st.markdown("#### Évaluation de l'envie")
            valeur_numerique = st.slider("Intensité du craving (0 = Nulle, 10 = Irrépressible)", 0, 10, 5)
            
            with st.expander("ℹ️ Aide : Les 3 types de pensées à repérer"):
                st.markdown("""
                * **🟢 Pensées Permissives :** Autorisations qu'on se donne.  
                *Ex: "Juste un seul, ça ne compte pas", "C'est l'occasion ou jamais".*
                * **🔵 Pensées Soulageantes :** Croyance que le produit est le seul remède.  
                *Ex: "Ça va me calmer", "J'ai besoin de décompresser", "Je ne tiendrai pas sans".*
                * **🟡 Attentes Positives :** Idéalisation des effets.  
                *Ex: "Je serai plus drôle", "Je dormirai mieux", "La soirée sera nulle sans ça".*
                """)

            pensees = st.text_area("Pensées associées / Contexte :", placeholder="J'étais stressé...")
            # Variable fictive pour le bloc submit
            unite_txt = "" 

        else: # CONSOMMATION
            st.markdown("#### Mesure de la consommation")
            st.write("Indiquez la quantité et l'unité.")

            # ON PASSE À 3 COLONNES pour plus de fluidité
            c_val, c_list, c_new = st.columns([1, 1, 1])
            
            with c_val:
                valeur_numerique = st.number_input("Quantité", min_value=0.0, step=0.5)
            
            with c_list:
                # Gestion de la mémoire : si l'unité en mémoire n'est pas dans la liste, on la rajoute temporairement
                if st.session_state.memoire_unite and st.session_state.memoire_unite not in st.session_state.liste_unites:
                    st.session_state.liste_unites.append(st.session_state.memoire_unite)
                
                # Index par défaut
                try:
                    idx_defaut = st.session_state.liste_unites.index(st.session_state.memoire_unite)
                except:
                    idx_defaut = 0

                # Menu déroulant classique
                choix_unite_liste = st.selectbox("Unité standard", st.session_state.liste_unites, index=idx_defaut)
            
            with c_new:
                # Champ permanent : s'il est rempli, il est prioritaire
                unite_custom = st.text_input("Ou Autre (Nouveau)", placeholder="ex: Litres")

            # LOGIQUE DE DÉCISION : Qui gagne ?
            if unite_custom:
                unite_finale = unite_custom
                # On marque qu'on a créé une nouvelle unité pour l'ajouter à la liste plus tard
                is_new_unit = True
            else:
                unite_finale = choix_unite_liste
                is_new_unit = False

            # Formatage pour l'historique
            pensees = f"Consommation : {valeur_numerique} {unite_finale}"

        st.divider()

        submitted = st.form_submit_button("💾 Enregistrer")
        
        if submitted:
            # 1. MISE A JOUR LISTE UNITÉS (Si on a utilisé le champ "Autre")
            # La variable 'unite_custom' vient du bloc ci-dessus
            if "CONSOMMÉ" in type_evt and unite_custom:
                if unite_custom not in st.session_state.liste_unites:
                    st.session_state.liste_unites.append(unite_custom)
            
            # 2. FORMATAGE
            heure_str = heure_evt.strftime("%H:%M")
            
            # 3. MISE A JOUR MÉMOIRES
            st.session_state.memoire_heure = heure_evt
            
            if "CONSOMMÉ" in type_evt:
                # On retient l'unité finale (qu'elle vienne de la liste ou du champ custom)
                st.session_state.memoire_unite = unite_finale
            
            # 4. SAUVEGARDE
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

# --- ZONE DE SUPPRESSION (ONGLET 1) ---
    with st.expander("🗑️ Supprimer une entrée (Derniers ajouts)"):
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
                except Exception as e:
                    pass
                
                st.session_state.data_addictions = st.session_state.data_addictions.drop(idx_to_drop).reset_index(drop=True)
                st.success("Entrée supprimée !")
                st.rerun()
        else:
            st.info("Aucune donnée récente.")

# ==============================================================================
# ONGLET 2 : BILAN
# ==============================================================================
with tab2:
    st.header(f"Historique : {substance_active}")
    
    df_global = st.session_state.data_addictions
    df_filtre = df_global[df_global["Substance"] == substance_active].sort_values(by=["Date", "Heure"], ascending=False).reset_index(drop=True)
    
    if not df_filtre.empty:
        st.info("💡 Vous pouvez modifier les valeurs directement dans le tableau.")
        
        edited_df = st.data_editor(
            df_filtre, 
            column_order=["Date", "Heure", "Type", "Intensité", "Pensées"], 
            use_container_width=True, 
            num_rows="dynamic",
            key=f"editor_{substance_active}"
        )
        
        if not edited_df.equals(df_filtre):
            df_others = df_global[df_global["Substance"] != substance_active]
            edited_df["Substance"] = substance_active
            st.session_state.data_addictions = pd.concat([df_others, edited_df], ignore_index=True)
            st.rerun()

        st.divider()
        st.write(f"### Évolution : {substance_active}")

        # --- PRÉPARATION GRAPHIQUE ---
        df_chart = edited_df.copy()
        
        try:
            df_chart['Full_Date'] = pd.to_datetime(df_chart['Date'].astype(str) + ' ' + df_chart['Heure'].astype(str), errors='coerce')
        except:
            df_chart['Full_Date'] = pd.to_datetime(df_chart['Date'])

        df_chart['Intensité'] = pd.to_numeric(df_chart['Intensité'], errors='coerce')

        df_envie = df_chart[df_chart["Type"].str.contains("ENVIE", na=False)]
        df_conso = df_chart[df_chart["Type"].str.contains("CONSOMMÉ", na=False)]

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

        # --- SUPPRESSION HISTORIQUE ---
        st.divider()
        with st.expander("🗑️ Supprimer une entrée depuis l'historique"):
            df_history = st.session_state.data_addictions.sort_values(by=["Date", "Heure"], ascending=False)
            if not df_history.empty:
                # Ajout ID pour doublons
                options_history = {}
                for idx, row in df_history.iterrows():
                    label = f"{row['Date']} - {row['Heure']} : {row['Substance']} ({row['Type']}) [ID:{idx}]"
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
                    except:
                        pass

                    st.session_state.data_addictions = st.session_state.data_addictions.drop(idx_to_drop).reset_index(drop=True)
                    st.success("Entrée supprimée !")
                    st.rerun()
            else:
                st.info("Historique vide.")

    else:
        st.info(f"Aucune donnée pour '{substance_active}'.")

st.divider()
st.page_link("streamlit_app.py", label="Retour à l'accueil", icon="🏠")