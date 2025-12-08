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

# --- 1. GESTION DES SUBSTANCES (MULTI-CIBLES) ---
if "liste_substances" not in st.session_state:
    st.session_state.liste_substances = []

# Initialisation des données locales
if "data_addictions" not in st.session_state:
    st.session_state.data_addictions = pd.DataFrame(columns=[
        "Date", "Heure", "Substance", "Type", "Intensité", "Pensées"
    ])

# --- MEMOIRE INTELLIGENTE (Session State) ---
# C'est ici qu'on définit les valeurs par défaut fixes (pas l'heure actuelle)
if "memoire_heure" not in st.session_state:
    st.session_state.memoire_heure = time(12, 00) # <--- Par défaut : 12h00
if "memoire_unite" not in st.session_state:
    st.session_state.memoire_unite = ""

# Zone de sélection
col_info, col_sel = st.columns([2, 2])
with col_info:
    st.write("**De quoi voulez-vous faire le suivi ?**")

with col_sel:
    # Création
    with st.popover("➕ Nouvelle Substance/Comportement"):
        new_sub = st.text_input("Nom (ex: Alcool, Tabac, Jeux...)")
        if st.button("Créer") and new_sub:
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
    
    # On sort le choix du type du formulaire pour que l'interface change instantanément
    type_evt = st.radio(
        "Qu'est-ce qui s'est passé ?", 
        ["⚡ J'ai eu une ENVIE (Craving)", "🍷 J'ai CONSOMMÉ"], 
        horizontal=True
    )
    
# Important : Pas de clear_on_submit ici
    with st.form("form_addiction"):
        c_date, c_heure = st.columns(2)
        with c_date: 
            date_evt = st.date_input("Date", datetime.now())
        with c_heure: 
            # --- MODIFIER CETTE LIGNE ---
            # On utilise la valeur en mémoire au lieu de datetime.now()
            heure_evt = st.time_input("Heure", value=st.session_state.memoire_heure)
            
        st.divider()
        
        # --- BLOC DYNAMIQUE ---
        valeur_numerique = 0.0
        info_unite = ""
        
        if "ENVIE" in type_evt:
            st.markdown("#### Évaluation de l'envie")
            valeur_numerique = st.slider("Intensité du craving (0 = Nulle, 10 = Irrépressible)", 0, 10, 5)
            # Info-bulle pédagogique (Expander pour ne pas prendre trop de place mais être lisible)
            with st.expander("ℹ️ Aide : Les 3 types de pensées à repérer"):
                st.markdown("""
                * **🟢 Pensées Permissives :** Autorisations qu'on se donne.  
                *Ex: "Juste un seul, ça ne compte pas", "C'est l'occasion ou jamais".*
                * **🔵 Pensées Soulageantes :** Croyance que le produit est le seul remède.  
                *Ex: "Ça va me calmer", "J'ai besoin de décompresser", "Je ne tiendrai pas sans".*
                * **🟡 Attentes Positives :** Idéalisation des effets.  
                *Ex: "Je serai plus drôle", "Je dormirai mieux", "La soirée sera nulle sans ça".*
                """)

            pensees = st.text_area("Pensées associées / Contexte / Déclencheurs :", placeholder="J'étais avec des amis, je me sentais stressé...")
            

        else: # CONSOMMATION
            st.markdown("#### Mesure de la consommation")
            st.write("Indiquez la quantité exacte.")

            c_val, c_unit = st.columns([1, 1])
            with c_val:
                valeur_numerique = st.number_input("Chiffre", min_value=0.0, step=0.5)
            with c_unit:
                placeholder_txt = "ex: Cigarettes, Verres, ml, cl, grammes"
                # --- MODIFIER CETTE LIGNE ---
                # On ajoute value=... pour pré-remplir avec la dernière unité utilisée
                unite_txt = st.text_input("Unité", value=st.session_state.memoire_unite, placeholder=placeholder_txt)

            # On prépare le texte de l'unité pour la sauvegarde
            if unite_txt:
                info_unite = f"[{valeur_numerique} {unite_txt}] "
            else:
                info_unite = f"[{valeur_numerique} ut.] "

            pensees = ""

        st.divider()

        submitted = st.form_submit_button("💾 Enregistrer")
        
        if submitted:
            # 1. CORRECTION BUG CLOUD : Ajout des secondes (:00) pour le format SQL
            heure_str = heure_evt.strftime("%H:%M")
            
            # 2. MÉMOIRE : On sauvegarde ce que l'utilisateur vient de mettre
            st.session_state.memoire_heure = heure_evt
            # On ne sauvegarde l'unité que si elle existe (cas consommation)
            if 'unite_txt' in locals():
                st.session_state.memoire_unite = unite_txt
            
            # Local
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
            from connect_db import save_data
            patient = st.session_state.get("patient_id", "Anonyme")
            
            # Ordre : Patient, Date, Heure, Substance, Type, Intensité, Pensées
            save_data("Addictions", [
                patient, str(date_evt), heure_str, substance_active, 
                type_evt, valeur_numerique, pensees
            ])
            
            st.success("Enregistré !")


        

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

        # --- PRÉPARATION DES DONNÉES ---
        df_chart = edited_df.copy()
        
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
        
    else:
        st.info(f"Aucune donnée enregistrée pour '{substance_active}'.")

st.divider()
st.page_link("streamlit_app.py", label="Retour à l'accueil", icon="🏠")

