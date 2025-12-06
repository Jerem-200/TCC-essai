import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Exposition", page_icon="🧗")

# --- VIGILE DE SÉCURITÉ ---
if "authentifie" not in st.session_state or not st.session_state.authentifie:
    st.warning("⛔ Veuillez vous connecter sur la page d'accueil.")
    st.switch_page("streamlit_app.py")
    st.stop()

st.title("🧗 L'Exposition Graduelle")
st.info("Affronter ses peurs petit à petit pour briser le cycle de l'évitement.")

# --- INITIALISATION MÉMOIRE ---
if "data_evitements" not in st.session_state:
    st.session_state.data_evitements = pd.DataFrame(columns=[
        "Situation", "Anxiété (0-100)", "Crainte (Scénario)", "Pire Situation",
        "Facteurs Aggravants", "Facteurs Protecteurs"
    ])

if "data_plans_expo" not in st.session_state:
    st.session_state.data_plans_expo = pd.DataFrame(columns=[
        "Date", "Situation Cible", "Abandonne", "Tolere", "Combine", "Affronte"
    ])

# NOUVEAU : Mémoire pour la liste temporaire des facteurs
if "temp_facteurs_expo" not in st.session_state:
    st.session_state.temp_facteurs_expo = []

# --- LES ONGLETS ---
tab1, tab2, tab3 = st.tabs(["1. Ma Hiérarchie (Liste)", "2. Planifier un exercice", "3. Mes Plans Enregistrés"])

# ==============================================================================
# ONGLET 1 : INVENTAIRE DÉTAILLÉ
# ==============================================================================
with tab1:
    st.header("1. Inventaire des situations")
    st.write("Définissez la situation, puis listez les facteurs associés un par un.")

    # --- PARTIE A : LA SITUATION ---
    st.subheader("A. La Situation")
    c1, c2 = st.columns([3, 1])
    with c1:
        # On utilise session_state pour garder le texte si la page recharge
        situation = st.text_input("Situation évitée :", placeholder="Ex: Prendre la parole...", key="input_sit")
    with c2:
        anxiete = st.number_input("Anxiété (0-100)", 0, 100, 50, step=5, key="input_anx")
    
    crainte = st.text_area("Scénario catastrophe :", height=60, placeholder="Qu'est-ce qui pourrait arriver de pire ?", key="input_crainte")
    pire_situation = st.checkbox("Ceci est la PIRE situation imaginable", key="input_pire")
    
    st.divider()

    # --- PARTIE B : LES FACTEURS (AJOUT UNITAIRE) ---
    st.subheader("B. Analyse des Facteurs")
    st.caption("Ajoutez les éléments qui aggravent la peur ou qui vous protègent.")

    with st.form("ajout_facteur_form", clear_on_submit=True):
        c_type, c_cat = st.columns(2)
        with c_type:
            type_facteur = st.selectbox("Type d'influence", ["🔴 Aggravant (Augmente le risque)", "🟢 Protecteur (Me rassure)"])
        with c_cat:
            categorie = st.selectbox("Catégorie", ["Lieu", "Situation", "Objet", "Pensée", "Image mentale", "Personne", "Autre"])
        
        desc_facteur = st.text_input("Description précise :", placeholder="Ex: S'il y a plus de 5 personnes...")
        
        if st.form_submit_button("Ajouter ce facteur"):
            if desc_facteur:
                # On ajoute un dictionnaire à la liste
                nouvel_item = {
                    "Type": type_facteur,
                    "Catégorie": categorie,
                    "Description": desc_facteur
                }
                st.session_state.temp_facteurs_expo.append(nouvel_item)
                st.rerun()
            else:
                st.warning("Veuillez écrire une description.")

    # --- AFFICHAGE DE LA LISTE DES FACTEURS ---
    if st.session_state.temp_facteurs_expo:
        st.write("---")
        st.write("**Facteurs listés pour cette situation :**")
        
        for i, item in enumerate(st.session_state.temp_facteurs_expo):
            col_icon, col_txt, col_del = st.columns([1, 6, 1])
            
            with col_icon:
                st.write("🔴" if "Aggravant" in item["Type"] else "🟢")
            
            with col_txt:
                # Affichage formaté : [Lieu] Description
                st.write(f"**[{item['Catégorie']}]** {item['Description']}")
            
            with col_del:
                if st.button("🗑️", key=f"del_fact_{i}"):
                    st.session_state.temp_facteurs_expo.pop(i)
                    st.rerun()
    else:
        st.info("Aucun facteur ajouté pour l'instant.")

    st.divider()

    # --- PARTIE C : VALIDATION FINALE ---
    if st.button("💾 Enregistrer la situation dans la liste"):
        if situation and crainte:
            # 1. On trie les facteurs pour créer les textes finaux
            aggravants_list = [f"[{f['Catégorie']}] {f['Description']}" for f in st.session_state.temp_facteurs_expo if "Aggravant" in f["Type"]]
            protecteurs_list = [f"[{f['Catégorie']}] {f['Description']}" for f in st.session_state.temp_facteurs_expo if "Protecteur" in f["Type"]]
            
            # On transforme en texte (un par ligne) pour Excel et l'affichage futur
            txt_agg = "\n".join(aggravants_list)
            txt_prot = "\n".join(protecteurs_list)
            
            new_row = {
                "Situation": situation,
                "Anxiété (0-100)": anxiete,
                "Crainte (Scénario)": crainte,
                "Pire Situation": "OUI" if pire_situation else "Non",
                "Facteurs Aggravants": txt_agg,
                "Facteurs Protecteurs": txt_prot
            }
            
            # Sauvegarde Locale
            st.session_state.data_evitements = pd.concat(
                [st.session_state.data_evitements, pd.DataFrame([new_row])], 
                ignore_index=True
            )
            
            # Sauvegarde Cloud
            from connect_db import save_data
            patient = st.session_state.get("patient_id", "Anonyme")
            save_data("Evitements", [patient, datetime.now().strftime("%Y-%m-%d"), situation, anxiete, crainte, "OUI" if pire_situation else "Non", txt_agg, txt_prot])
            
            # Nettoyage
            st.session_state.temp_facteurs_expo = [] # On vide la liste temporaire
            st.success("Situation enregistrée avec succès ! Vous pouvez la planifier dans l'onglet 2.")
        else:
            st.error("Veuillez au moins remplir la Situation et la Crainte.")

    # Affichage Récap
    if not st.session_state.data_evitements.empty:
        st.divider()
        st.subheader("Votre Hiérarchie")
        st.dataframe(st.session_state.data_evitements[["Situation", "Anxiété (0-100)", "Crainte (Scénario)"]].sort_values("Anxiété (0-100)"), use_container_width=True)

# ==============================================================================
# ONGLET 2 : PRÉPARATION ET PLANIFICATION
# ==============================================================================
with tab2:
    st.header("2. Planifier un exercice")
    
    if st.session_state.data_evitements.empty:
        st.warning("Votre liste est vide. Remplissez l'onglet 1 d'abord.")
    else:
        # 1. Choisir la situation
        liste_situations = st.session_state.data_evitements["Situation"].unique()
        choix_sit = st.selectbox("Quelle situation voulez-vous affronter ?", liste_situations)
        
        # 2. Récupérer les données
        infos_sit = st.session_state.data_evitements[st.session_state.data_evitements["Situation"] == choix_sit].iloc[0]
        
        # On re-transforme les textes sauvegardés en listes pour les cases à cocher
        list_aggravants = [x.strip() for x in str(infos_sit["Facteurs Aggravants"]).split('\n') if x.strip()]
        list_protecteurs = [x.strip() for x in str(infos_sit["Facteurs Protecteurs"]).split('\n') if x.strip()]
        
        st.info(f"**Crainte à tester :** {infos_sit['Crainte (Scénario)']}")
        
        st.divider()
        
        with st.form("form_plan_expo"):
            st.write("Cochez les éléments pour construire votre exercice :")
            
            st.markdown("##### ❌ Quels facteurs protecteurs j’abandonne ?")
            if list_protecteurs:
                abandonne_select = st.multiselect("Sélectionnez :", list_protecteurs)
            else:
                st.caption("(Aucun facteur protecteur enregistré)")
                abandonne_select = []
            
            st.markdown("##### ⚠️ Quels facteurs de risques je tolère ?")
            if list_aggravants:
                tolere_select = st.multiselect("Je vais supporter :", list_aggravants, key="tolere")
            else:
                st.caption("(Aucun facteur aggravant enregistré)")
                tolere_select = []

            st.markdown("##### ➕ Quels facteurs de risques je combine ?")
            if list_aggravants:
                combine_select = st.multiselect("Je vais ajouter pour corser l'exercice :", list_aggravants, key="combine")
            else:
                st.caption("(Aucun facteur aggravant enregistré)")
                combine_select = []
                
            st.markdown("##### 🎯 Qu’est-ce que j’affronte ?")
            affronte_txt = st.text_area("Décrivez l'action concrète :", height=80, placeholder="Ex: Je vais entrer dans la salle...")
            
            submit_plan = st.form_submit_button("💾 Enregistrer ce Plan d'Exposition")
            
            if submit_plan:
                str_abandonne = ", ".join(abandonne_select)
                str_tolere = ", ".join(tolere_select)
                str_combine = ", ".join(combine_select)
                
                new_plan = {
                    "Date": datetime.now().strftime("%Y-%m-%d"),
                    "Situation Cible": choix_sit,
                    "Abandonne": str_abandonne,
                    "Tolere": str_tolere,
                    "Combine": str_combine,
                    "Affronte": affronte_txt
                }
                
                st.session_state.data_plans_expo = pd.concat([st.session_state.data_plans_expo, pd.DataFrame([new_plan])], ignore_index=True)
                
                from connect_db import save_data
                patient = st.session_state.get("patient_id", "Anonyme")
                save_data("Expositions", [patient, datetime.now().strftime("%Y-%m-%d"), choix_sit, str_abandonne, str_tolere, str_combine, affronte_txt])
                
                st.success("Exercice planifié ! Allez dans l'onglet 3 pour le consulter.")

# ==============================================================================
# ONGLET 3 : HISTORIQUE DES PLANS
# ==============================================================================
with tab3:
    st.header("3. Vos exercices d'exposition")
    
    if not st.session_state.data_plans_expo.empty:
        for i, row in st.session_state.data_plans_expo.iterrows():
            with st.expander(f"📅 {row['Date']} - {row['Situation Cible']}"):
                st.markdown(f"**🎯 Action :** {row['Affronte']}")
                st.write("---")
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.markdown("**❌ J'abandonne :**")
                    st.info(row['Abandonne'] if row['Abandonne'] else "-")
                with c2:
                    st.markdown("**⚠️ Je tolère :**")
                    st.warning(row['Tolere'] if row['Tolere'] else "-")
                with c3:
                    st.markdown("**➕ Je combine :**")
                    st.error(row['Combine'] if row['Combine'] else "-")
    else:
        st.info("Aucun plan d'exposition enregistré pour l'instant.")

st.divider()
st.page_link("streamlit_app.py", label="Retour à l'accueil", icon="🏠")