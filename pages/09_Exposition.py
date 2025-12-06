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
        "Situation", "Anxiété (0-100)", "Crainte (Scénario)", "Pire Situation"
    ])

if "data_plans_expo" not in st.session_state:
    st.session_state.data_plans_expo = pd.DataFrame(columns=[
        "Date", "Situation Cible", "Facteurs", "Sécurités", "Plan Détaillé"
    ])

# --- LES ONGLETS ---
tab1, tab2, tab3 = st.tabs(["1. Ma Hiérarchie (Liste)", "2. Planifier un exercice", "3. Mes Plans Enregistrés"])

# ==============================================================================
# ONGLET 1 : LA LISTE DES ÉVITEMENTS (HIÉRARCHIE)
# ==============================================================================
with tab1:
    st.header("1. Liste des évitements")
    st.write("Dressez la liste de tout ce que vous évitez par peur. Soyez précis.")
    
    with st.expander("ℹ️ Aide : Comment décrire sa crainte ?"):
        st.write("""
        Décrivez concrètement ce que vous craignez qu'il arrive.
        * *Vague :* "J'ai peur que ça se passe mal."
        * *Précis :* "Je vais trembler, bafouiller et les gens vont se moquer de moi."
        """)

    with st.form("form_hierarchie", clear_on_submit=True):
        c1, c2 = st.columns([3, 1])
        with c1:
            situation = st.text_input("Situation évitée :", placeholder="Ex: Prendre la parole en réunion")
        with c2:
            anxiete = st.number_input("Anxiété anticipée (0-100)", 0, 100, 50, step=5)
        
        crainte = st.text_area("Scénario catastrophe (Qu'est-ce qui pourrait arriver de pire ?) :", height=80)
        
        pire_situation = st.checkbox("Ceci est la PIRE situation imaginable pour moi")
        
        if st.form_submit_button("Ajouter à la liste"):
            new_row = {
                "Situation": situation,
                "Anxiété (0-100)": anxiete,
                "Crainte (Scénario)": crainte,
                "Pire Situation": "OUI" if pire_situation else "Non"
            }
            st.session_state.data_evitements = pd.concat(
                [st.session_state.data_evitements, pd.DataFrame([new_row])], 
                ignore_index=True
            )
            
            # Sauvegarde Cloud (Optionnel à ce stade, mais conseillé)
            from connect_db import save_data
            patient = st.session_state.get("patient_id", "Anonyme")
            save_data("Evitements", [patient, datetime.now().strftime("%Y-%m-%d"), situation, anxiete, crainte, "OUI" if pire_situation else "Non"])
            
            st.success("Situation ajoutée !")

    # Affichage de la hiérarchie triée
    if not st.session_state.data_evitements.empty:
        st.divider()
        st.subheader("Votre échelle de la peur (Du moins au plus angoissant)")
        
        # Tri automatique par score d'anxiété
        df_sorted = st.session_state.data_evitements.sort_values(by="Anxiété (0-100)", ascending=True)
        st.dataframe(df_sorted, use_container_width=True)
    else:
        st.info("Votre liste est vide. Commencez par ajouter des situations ci-dessus.")

# ==============================================================================
# ONGLET 2 : PRÉPARATION ET PLANIFICATION
# ==============================================================================
with tab2:
    st.header("2. Préparer une exposition")
    
    if st.session_state.data_evitements.empty:
        st.warning("Veuillez d'abord remplir votre liste dans l'onglet 1.")
    else:
        # Sélection de la situation à travailler
        liste_situations = st.session_state.data_evitements["Situation"].unique()
        choix_sit = st.selectbox("Quelle situation voulez-vous affronter ?", liste_situations)
        
        # On récupère les infos de cette situation
        infos_sit = st.session_state.data_evitements[st.session_state.data_evitements["Situation"] == choix_sit].iloc[0]
        
        st.info(f"**Crainte associée :** {infos_sit['Crainte (Scénario)']}")
        
        st.divider()
        
        with st.form("form_plan_expo"):
            st.markdown("### Analyse des facteurs")
            
            # 4. Facteurs aggravants
            facteurs = st.text_area("4. Facteurs aggravants", help="Lieux, objets, personnes qui augmentent le risque (selon vous).")
            
            # 5. Comportements de sécurité
            securites = st.text_area("5. Comportements de sécurité / Évitements subtils", help="Objets, pensées ou gestes qui vous rassurent (ex: avoir son téléphone, ne pas regarder dans les yeux...).")
            
            st.markdown("---")
            st.markdown("### 6. Fiche de planification")
            st.write("En affrontant la situation sans vos sécurités, vous vérifiez si la catastrophe se produit vraiment.")
            
            q1 = st.text_input("Comment vais-je tester ma crainte ? (Quoi faire ?)")
            
            c1, c2 = st.columns(2)
            with c1:
                q2 = st.text_area("o Qu'est-ce que j'abandonne ? (Sécurités)")
                q3 = st.text_area("o Qu'est-ce que je tolère ? (Sensations)")
            with c2:
                q4 = st.text_area("o Qu'est-ce que je combine ? (Contexte)")
                q5 = st.text_area("o Qu'est-ce que j'affronte ? (Situation)")
            
            # Compilation du résumé
            submit_plan = st.form_submit_button("💾 Enregistrer le Plan d'Exposition")
            
            if submit_plan:
                resume_plan = f"ACTION: {q1}\n\nSANS: {q2}\nAVEC: {q3}\nCONTEXTE: {q4}\nCIBLE: {q5}"
                
                new_plan = {
                    "Date": datetime.now().strftime("%Y-%m-%d"),
                    "Situation Cible": choix_sit,
                    "Facteurs": facteurs,
                    "Sécurités": securites,
                    "Plan Détaillé": resume_plan
                }
                
                st.session_state.data_plans_expo = pd.concat(
                    [st.session_state.data_plans_expo, pd.DataFrame([new_plan])], 
                    ignore_index=True
                )
                
                # Sauvegarde Cloud
                from connect_db import save_data
                patient = st.session_state.get("patient_id", "Anonyme")
                save_data("Expositions", [patient, datetime.now().strftime("%Y-%m-%d"), choix_sit, facteurs, securites, resume_plan])
                
                st.success("Exercice planifié ! Allez dans l'onglet 3 pour le consulter.")

# ==============================================================================
# ONGLET 3 : HISTORIQUE DES PLANS
# ==============================================================================
with tab3:
    st.header("3. Vos exercices d'exposition")
    
    if not st.session_state.data_plans_expo.empty:
        for i, row in st.session_state.data_plans_expo.iterrows():
            with st.expander(f"📅 {row['Date']} - {row['Situation Cible']}"):
                st.markdown(f"**Facteurs aggravants :** {row['Facteurs']}")
                st.markdown(f"**Comportements de sécurité à bannir :** {row['Sécurités']}")
                st.divider()
                st.markdown("#### 🔥 Le Plan :")
                st.text(row['Plan Détaillé'])
    else:
        st.info("Aucun plan d'exposition enregistré pour l'instant.")

st.divider()
st.page_link("streamlit_app.py", label="Retour à l'accueil", icon="🏠")