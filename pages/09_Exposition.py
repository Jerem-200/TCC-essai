import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Exposition", page_icon="🧗")

# --- VIGILE DE SÉCURITÉ ---
if "authentifie" not in st.session_state or not st.session_state.authentifie:
    st.warning("⛔ Veuillez vous connecter sur la page d'accueil.")
    st.switch_page("streamlit_app.py")
    st.stop()

st.title("🧗 L'Exposition (Apprentissage Inhibiteur)")
st.info("L'objectif n'est pas de se calmer, mais de tester si vos peurs se réalisent vraiment (Maximiser la surprise).")

# --- INITIALISATION MÉMOIRE ---
if "data_crainte_centrale" not in st.session_state:
    st.session_state.data_crainte_centrale = {"Crainte": "", "Facteurs": []} # Liste de dicts

if "data_hierarchie" not in st.session_state:
    st.session_state.data_hierarchie = pd.DataFrame(columns=["Situation", "Conséquence Anticipée", "Inconfort (0-100)"])

if "data_planning_expo" not in st.session_state:
    st.session_state.data_planning_expo = pd.DataFrame(columns=["Date", "Heure", "Situation", "Type Exposition"])

if "data_logs_expo" not in st.session_state:
    st.session_state.data_logs_expo = pd.DataFrame(columns=[
        "Date", "Situation", "Pré-Croyance", "Durée", "Surprise", "Apprentissage", "Post-Croyance"
    ])

# --- LES 4 ONGLETS ---
tab1, tab2, tab3, tab4 = st.tabs(["1. Analyse Crainte", "2. Hiérarchie", "3. Planifier", "4. Consolider (Après)"])

# ==============================================================================
# ONGLET 1 : ANALYSE DE LA CRAINTE & FACTEURS
# ==============================================================================
with tab1:
    st.header("A. La Crainte Centrale")
    
    with st.expander("ℹ️ Lire : Comment définir sa crainte ?", expanded=True):
        st.info("""
        Il faut identifier la **conséquence ultime crainte** (ex: "Je vais faire une crise cardiaque" ou "Je vais être rejeté définitivement"), et non juste la sensation de peur. 
        Cela doit être **testable objectivement** (Vrai ou Faux ?).
        """)
        
    crainte_actuelle = st.session_state.data_crainte_centrale["Crainte"]
    nouvelle_crainte = st.text_area("Quelle est la conséquence terrible qui pourrait arriver ?", value=crainte_actuelle)
    
    if st.button("💾 Sauvegarder la définition"):
        st.session_state.data_crainte_centrale["Crainte"] = nouvelle_crainte
        st.success("Crainte définie.")

    st.divider()
    
    st.header("B. Analyse des Facteurs")
    st.write("Qu'est-ce qui modifie le risque ?")
    
    with st.form("ajout_facteur"):
        c1, c2 = st.columns([3, 1])
        with c1:
            desc_facteur = st.text_input("Description du facteur :")
        with c2:
            type_facteur = st.selectbox("Type", ["🔴 Risque (Aggravant)", "🟢 Protecteur (Sécurité)"])
        
        is_main_trigger = False
        if "Risque" in type_facteur:
            is_main_trigger = st.checkbox("Est-ce le déclencheur principal (CS) ?")
            
        if st.form_submit_button("Ajouter ce facteur"):
            nouveau = {
                "Description": desc_facteur,
                "Type": type_facteur,
                "Main": is_main_trigger
            }
            st.session_state.data_crainte_centrale["Facteurs"].append(nouveau)
            st.rerun()

    # Affichage de la liste
    if st.session_state.data_crainte_centrale["Facteurs"]:
        st.write("---")
        for i, f in enumerate(st.session_state.data_crainte_centrale["Facteurs"]):
            col_icon, col_txt, col_del = st.columns([1, 6, 1])
            with col_icon:
                if f["Main"]: st.write("🔥") # Déclencheur principal
                elif "Risque" in f["Type"]: st.write("🔴")
                else: st.write("🟢")
            with col_txt:
                prefix = "**[DÉCLENCHEUR PRINCIPAL]** " if f["Main"] else ""
                st.write(f"{prefix}{f['Description']}")
            with col_del:
                if st.button("🗑️", key=f"del_f_{i}"):
                    st.session_state.data_crainte_centrale["Facteurs"].pop(i)
                    st.rerun()

# ==============================================================================
# ONGLET 2 : HIÉRARCHIE & STRATÉGIES
# ==============================================================================
with tab2:
    st.header("Liste des situations évitées / redoutées")
    
    # Rappel des stratégies
    with st.expander("💡 Les 4 Stratégies Clés (À lire avant de lister)"):
        st.markdown("""
        1. **Jetez-le ("Throw it Out")** : Identifiez et éliminez les comportements de sécurité.  
           *Ex: "Laissez votre téléphone dans la voiture".*
        2. **Restez avec ("Stay with It")** : Maintenez l'attention sur le déclencheur (pas de distraction).  
           *Ex: "Concentrez-vous sur votre cœur qui bat vite".*
        3. **Combinez-le ("Combine It")** : Utilisez l'extinction approfondie (rendez la chose plus dure).  
           *Ex: "Faites l'exposition en étant fatigué" ou "dans le noir".*
        4. **Affrontez-le ("Face It")** : Occasionnellement, subir un échec réel pour apprendre à gérer.
        """)

    with st.form("form_hierarchie"):
        sit = st.text_input("Situation redoutée :")
        cons = st.text_input("Conséquence anticipée spécifique :")
        inc = st.slider("Inconfort / Attente de catastrophe (0-100%)", 0, 100, 60)
        
        if st.form_submit_button("Ajouter à la hiérarchie"):
            new_row = {"Situation": sit, "Conséquence Anticipée": cons, "Inconfort (0-100)": inc}
            st.session_state.data_hierarchie = pd.concat([st.session_state.data_hierarchie, pd.DataFrame([new_row])], ignore_index=True)
            
            # Sauvegarde Cloud
            from connect_db import save_data
            patient = st.session_state.get("patient_id", "Anonyme")
            save_data("Evitements", [patient, datetime.now().strftime("%Y-%m-%d"), sit, inc, cons, ""])
            st.success("Ajouté !")

    if not st.session_state.data_hierarchie.empty:
        st.divider()
        st.write("#### 📋 Votre Hiérarchie (Du plus difficile au plus facile)")
        
        # Tri décroissant
        df_sorted = st.session_state.data_hierarchie.sort_values(by="Inconfort (0-100)", ascending=False)
        st.dataframe(df_sorted, use_container_width=True)
        
        # Le Warning intelligent
        max_score = df_sorted["Inconfort (0-100)"].max()
        if max_score < 60:
            st.warning("⚠️ **Note :** Vos scores sont bas (<60%). Peu d'apprentissage se produit lorsque la probabilité du résultat redouté est faible. Essayez de trouver des situations plus difficiles ou de retirer plus de sécurités.")
        else:
            st.success("✅ Vous avez des situations > 60%. Ce sont d'excellentes opportunités pour créer une 'Erreur de prédiction' (surprise).")

# ==============================================================================
# ONGLET 3 : PLANIFICATION (EXPOSITION ULTIME)
# ==============================================================================
with tab3:
    st.header("Planifier 'L'Exposition Ultime'")
    
    st.info("""
    **La recette de l'exposition idéale :**
    1. Inclure le **Déclencheur Principal**.
    2. Ajouter les **Modulateurs Positifs** (ce qui aggrave).
    3. Supprimer tous les **Signaux de Sécurité**.
    
    *Objectif : Maximiser l'attente de la catastrophe pour maximiser la surprise quand elle n'arrive pas.*
    """)
    
    if st.session_state.data_hierarchie.empty:
        st.warning("Remplissez la hiérarchie en onglet 2 d'abord.")
    else:
        # Sélection
        choix_sit = st.selectbox("Quelle situation voulez-vous planifier ?", st.session_state.data_hierarchie["Situation"].unique())
        
        c1, c2 = st.columns(2)
        with c1:
            date_prevue = st.date_input("Date prévue", datetime.now())
        with c2:
            heure_prevue = st.time_input("Heure prévue", datetime.now().time())
            
        with st.expander("🛠️ Construire l'exercice (Checklist)", expanded=True):
            st.write("Pour cet exercice :")
            # On récupère les facteurs de l'onglet 1 pour aider
            facteurs = st.session_state.data_crainte_centrale["Facteurs"]
            aggravants = [f['Description'] for f in facteurs if "Risque" in f['Type']]
            protecteurs = [f['Description'] for f in facteurs if "Protecteur" in f['Type']]
            
            if aggravants:
                st.multiselect("Quels aggravants je combine ? (Combine it)", aggravants)
            if protecteurs:
                st.multiselect("Quels protecteurs je supprime ? (Throw it out)", protecteurs)
                
        if st.button("📅 Valider et Planifier"):
            new_plan = {
                "Date": str(date_prevue),
                "Heure": str(heure_prevue),
                "Situation": choix_sit,
                "Type Exposition": "In Vivo"
            }
            st.session_state.data_planning_expo = pd.concat([st.session_state.data_planning_expo, pd.DataFrame([new_plan])], ignore_index=True)
            
            # Cloud
            from connect_db import save_data
            patient = st.session_state.get("patient_id", "Anonyme")
            save_data("Expositions", [patient, str(date_prevue), choix_sit, "Planifié", "", ""])
            
            st.success("Exercice ajouté à votre agenda !")

    # Affichage du planning
    if not st.session_state.data_planning_expo.empty:
        st.write("---")
        st.write("#### 🗓️ Vos exercices à venir")
        st.dataframe(st.session_state.data_planning_expo, use_container_width=True)

# ==============================================================================
# ONGLET 4 : CONSOLIDATION (POST-EXPOSITION)
# ==============================================================================
with tab4:
    st.header("Grille d'auto-observation (Après l'exercice)")
    st.write("L'apprentissage ne s'arrête pas à la fin de l'exercice. La consolidation est cruciale.")
    
    # Choix de l'exercice réalisé
    if st.session_state.data_planning_expo.empty:
        st.warning("Planifiez d'abord un exercice dans l'onglet 3.")
    else:
        # On crée une liste lisible "Date - Situation"
        liste_prevus = [f"{row['Date']} : {row['Situation']}" for i, row in st.session_state.data_planning_expo.iterrows()]
        exo_realise = st.selectbox("Quel exercice avez-vous fait ?", liste_prevus)
        
        st.divider()
        
        with st.form("form_consolidation"):
            st.subheader("1. Juste avant (Attentes)")
            pre_croyance = st.slider("À quel point étiez-vous sûr que la catastrophe allait arriver ? (0-100%)", 0, 100, 80)
            
            st.subheader("2. Juste après (Réalité)")
            duree = st.number_input("Durée de l'exposition (minutes)", 0, 240, 20)
            
            st.markdown("**Surprise / Erreur de prédiction :**")
            surprise = st.radio("Le résultat vous a-t-il surpris ?", ["Non, c'était horrible comme prévu", "Un peu", "Oui, c'était moins pire que prévu", "Oui, rien ne s'est passé"], index=2)
            
            appr = st.text_area("Qu'est-ce que j'ai appris ? (Quelles preuves ai-je accumulées ?)")
            
            st.subheader("3. Ré-évaluation")
            post_croyance = st.slider("Si je recommençais maintenant, quelle est la probabilité que la catastrophe arrive ? (0-100%)", 0, 100, 40)
            
            submit_log = st.form_submit_button("Enregistrer le Bilan")
            
            if submit_log:
                new_log = {
                    "Date": datetime.now().strftime("%Y-%m-%d"),
                    "Situation": exo_realise,
                    "Pré-Croyance": pre_croyance,
                    "Durée": duree,
                    "Surprise": surprise,
                    "Apprentissage": appr,
                    "Post-Croyance": post_croyance
                }
                st.session_state.data_logs_expo = pd.concat([st.session_state.data_logs_expo, pd.DataFrame([new_log])], ignore_index=True)
                
                # Cloud (On utilise une structure générique pour stocker ça dans 'Expositions' ou un nouvel onglet)
                # Ici on va écrire dans 'Expositions' en précisant que c'est un BILAN
                from connect_db import save_data
                patient = st.session_state.get("patient_id", "Anonyme")
                texte_bilan = f"AVANT:{pre_croyance}% | APRES:{post_croyance}% | SURPRISE:{surprise} | APPRIS:{appr}"
                save_data("Expositions", [patient, datetime.now().strftime("%Y-%m-%d"), exo_realise, "BILAN FAIT", str(duree), texte_bilan])
                
                st.success("Bilan enregistré ! C'est ainsi que le cerveau recâble la peur. Bravo.")
                st.balloons()

    # Historique des logs
    if not st.session_state.data_logs_expo.empty:
        st.divider()
        st.write("#### 🧠 Vos apprentissages")
        for i, row in st.session_state.data_logs_expo.iterrows():
            with st.expander(f"{row['Date']} - {row['Situation']}"):
                c1, c2 = st.columns(2)
                with c1: 
                    st.metric("Croyance Avant", f"{row['Pré-Croyance']}%")
                with c2: 
                    st.metric("Croyance Après", f"{row['Post-Croyance']}%", delta=f"{row['Post-Croyance']-row['Pré-Croyance']}%")
                st.write(f"**J'ai appris :** {row['Apprentissage']}")

st.divider()
st.page_link("streamlit_app.py", label="Retour à l'accueil", icon="🏠")