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

# --- LES ONGLETS ---
tab1, tab2, tab3 = st.tabs(["1. Ma Hiérarchie (Liste)", "2. Planifier un exercice", "3. Mes Plans Enregistrés"])

# ==============================================================================
# ONGLET 1 : LA LISTE DES ÉVITEMENTS & ANALYSE FACTEURS
# ==============================================================================
with tab1:
    st.header("1. Inventaire des situations")
    st.write("Décrivez la situation et listez les facteurs associés.")

    with st.form("form_hierarchie", clear_on_submit=True):
        st.subheader("La Situation")
        c1, c2 = st.columns([3, 1])
        with c1:
            situation = st.text_input("Situation évitée :", placeholder="Ex: Prendre la parole en réunion")
        with c2:
            anxiete = st.number_input("Anxiété (0-100)", 0, 100, 50, step=5)
        
        crainte = st.text_area("Scénario catastrophe (Crainte précise) :", height=60, placeholder="Qu'est-ce qui pourrait arriver de pire ?")
        pire_situation = st.checkbox("Ceci est la PIRE situation imaginable")
        
        st.divider()
        st.subheader("Les Facteurs (Une liste pour plus tard)")
        
        c_agg, c_prot = st.columns(2)
        with c_agg:
            st.markdown("**🔴 Facteurs Aggravants**")
            st.caption("Ce qui augmente le risque (Lieux, objets, pensées...)")
            aggravants_txt = st.text_area("Listez-les (un par ligne) :", key="agg_input", height=150)
            
        with c_prot:
            st.markdown("**🟢 Facteurs Protecteurs**")
            st.caption("Vos sécurités (Objets, comportements, fuites...)")
            protecteurs_txt = st.text_area("Listez-les (un par ligne) :", key="prot_input", height=150)
        
        if st.form_submit_button("Ajouter à la liste"):
            new_row = {
                "Situation": situation,
                "Anxiété (0-100)": anxiete,
                "Crainte (Scénario)": crainte,
                "Pire Situation": "OUI" if pire_situation else "Non",
                "Facteurs Aggravants": aggravants_txt,
                "Facteurs Protecteurs": protecteurs_txt
            }
            st.session_state.data_evitements = pd.concat(
                [st.session_state.data_evitements, pd.DataFrame([new_row])], 
                ignore_index=True
            )
            
            # Sauvegarde Cloud
            from connect_db import save_data
            patient = st.session_state.get("patient_id", "Anonyme")
            save_data("Evitements", [patient, datetime.now().strftime("%Y-%m-%d"), situation, anxiete, crainte, "OUI" if pire_situation else "Non", aggravants_txt, protecteurs_txt])
            
            st.success("Situation et facteurs enregistrés !")

    # Affichage
    if not st.session_state.data_evitements.empty:
        st.divider()
        st.write("### Votre Hiérarchie")
        st.dataframe(st.session_state.data_evitements[["Situation", "Anxiété (0-100)", "Crainte (Scénario)"]].sort_values("Anxiété (0-100)"), use_container_width=True)

# ==============================================================================
# ONGLET 2 : PRÉPARATION ET PLANIFICATION (SÉLECTEUR INTELLIGENT)
# ==============================================================================
with tab2:
    st.header("2. Planifier un exercice")
    
    if st.session_state.data_evitements.empty:
        st.warning("Votre liste est vide. Remplissez l'onglet 1 d'abord.")
    else:
        # 1. Choisir la situation
        liste_situations = st.session_state.data_evitements["Situation"].unique()
        choix_sit = st.selectbox("Quelle situation voulez-vous affronter ?", liste_situations)
        
        # 2. Récupérer les données de cette situation
        infos_sit = st.session_state.data_evitements[st.session_state.data_evitements["Situation"] == choix_sit].iloc[0]
        
        # On transforme les textes en listes pour les cases à cocher
        # (On coupe le texte à chaque saut de ligne \n)
        list_aggravants = [x.strip() for x in str(infos_sit["Facteurs Aggravants"]).split('\n') if x.strip()]
        list_protecteurs = [x.strip() for x in str(infos_sit["Facteurs Protecteurs"]).split('\n') if x.strip()]
        
        st.info(f"**Crainte à tester :** {infos_sit['Crainte (Scénario)']}")
        
        st.divider()
        
        with st.form("form_plan_expo"):
            st.write("Cochez les éléments pour construire votre exercice :")
            
            # Question 1 : ABANDONNER (Protecteurs)
            st.markdown("##### ❌ Quels facteurs protecteurs j’abandonne ?")
            if list_protecteurs:
                abandonne_select = st.multiselect("Sélectionnez dans votre liste :", list_protecteurs)
            else:
                st.caption("(Aucun facteur protecteur listé dans l'onglet 1)")
                abandonne_select = []
            
            # Question 2 : TOLÉRER (Aggravants)
            st.markdown("##### ⚠️ Quels facteurs de risques je tolère ?")
            if list_aggravants:
                tolere_select = st.multiselect("Je vais supporter :", list_aggravants, key="tolere")
            else:
                st.caption("(Aucun facteur aggravant listé)")
                tolere_select = []

            # Question 3 : COMBINER (Aggravants)
            st.markdown("##### ➕ Quels facteurs de risques je combine ?")
            if list_aggravants:
                combine_select = st.multiselect("Je vais ajouter pour corser l'exercice :", list_aggravants, key="combine")
            else:
                st.caption("(Aucun facteur aggravant listé)")
                combine_select = []
                
            # Question 4 : AFFRONTER
            st.markdown("##### 🎯 Qu’est-ce que j’affronte ?")
            affronte_txt = st.text_area("Décrivez l'action concrète :", height=80, placeholder="Ex: Je vais entrer dans la salle et dire bonjour...")
            
            # Validation
            submit_plan = st.form_submit_button("💾 Enregistrer ce Plan d'Exposition")
            
            if submit_plan:
                # On transforme les listes cochées en texte propre
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
                
                st.session_state.data_plans_expo = pd.concat(
                    [st.session_state.data_plans_expo, pd.DataFrame([new_plan])], 
                    ignore_index=True
                )
                
                # Cloud
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
                    st.write(row['Abandonne'] if row['Abandonne'] else "-")
                with c2:
                    st.markdown("**⚠️ Je tolère :**")
                    st.write(row['Tolere'] if row['Tolere'] else "-")
                with c3:
                    st.markdown("**➕ Je combine :**")
                    st.write(row['Combine'] if row['Combine'] else "-")
    else:
        st.info("Aucun plan d'exposition enregistré pour l'instant.")

st.divider()
st.page_link("streamlit_app.py", label="Retour à l'accueil", icon="🏠")