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
st.info("L'objectif est de tester si vos peurs se réalisent vraiment (Maximiser la surprise).")

# --- INITIALISATION MÉMOIRE ---
if "data_crainte_centrale" not in st.session_state:
    st.session_state.data_crainte_centrale = {"Crainte": "", "Facteurs": []}

if "data_hierarchie" not in st.session_state:
    # On change "Inconfort" par "Attente"
    st.session_state.data_hierarchie = pd.DataFrame(columns=["Situation", "Conséquence Anticipée", "Attente (0-100)"])

if "data_planning_expo" not in st.session_state:
    st.session_state.data_planning_expo = pd.DataFrame(columns=["Date", "Heure", "Situation", "Attente Pré-Expo"])

if "data_logs_expo" not in st.session_state:
    st.session_state.data_logs_expo = pd.DataFrame(columns=[
        "Date", "Situation", "Pré-Croyance", "Durée", "Surprise", "Apprentissage", "Post-Croyance"
    ])

# Variable pour valider l'étape 1 visuellement
if "step1_valide" not in st.session_state:
    st.session_state.step1_valide = False

# --- LES 4 ONGLETS ---
tab1, tab2, tab3, tab4 = st.tabs(["1. Analyse Crainte", "2. Hiérarchie", "3. Planifier", "4. Consolider"])

# ==============================================================================
# ONGLET 1 : ANALYSE (AVEC VALIDATION ET INFO ULTIME)
# ==============================================================================
with tab1:
    st.header("A. La Crainte Centrale")
    
    help_crainte = "Il faut identifier la conséquence ultime crainte (ex: 'Je vais faire une crise cardiaque' ou 'Je vais être rejeté'), et non juste la sensation de peur. Cela doit être testable objectivement."
    
    with st.expander("ℹ️ Aide : Comment définir sa crainte ?", expanded=False):
        st.info(help_crainte)
        
    crainte_actuelle = st.session_state.data_crainte_centrale["Crainte"]
    nouvelle_crainte = st.text_area("Quelle est la conséquence terrible qui pourrait arriver ?", value=crainte_actuelle, help=help_crainte)
    
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

    # Liste des facteurs
    if st.session_state.data_crainte_centrale["Facteurs"]:
        for i, f in enumerate(st.session_state.data_crainte_centrale["Facteurs"]):
            col_icon, col_txt, col_del = st.columns([1, 6, 1])
            with col_icon:
                if f["Main"]: st.write("🔥")
                elif "Risque" in f["Type"]: st.write("🔴")
                else: st.write("🟢")
            with col_txt:
                prefix = "**[DÉCLENCHEUR]** " if f["Main"] else ""
                st.write(f"{prefix}{f['Description']}")
            with col_del:
                if st.button("🗑️", key=f"del_f_{i}"):
                    st.session_state.data_crainte_centrale["Facteurs"].pop(i)
                    st.rerun()

    st.divider()
    
    # BOUTON DE VALIDATION DE L'ÉTAPE 1
    if st.button("✅ Valider l'étape 1 (Analyse terminée)"):
        st.session_state.step1_valide = True
    
    # APPARITION DE L'INFO "EXPOSITION ULTIME"
    if st.session_state.step1_valide:
        st.success("Étape 1 validée !")
        with st.container(border=True):
            st.markdown("### 🔥 Concept : L'Exposition Ultime")
            st.markdown("""
            Pour maximiser l'apprentissage (la surprise), l'exposition idéale doit :
            1. Inclure le **déclencheur principal** (CS).
            2. Ajouter les **modulateurs positifs** (ce qui rend la chose plus probable).
            3. Supprimer tous les **signaux de sécurité** (inhibiteurs).
            
            *L'objectif : Créer une situation où l'attente que la catastrophe se produise est maximale, afin que sa non-occurrence crée la plus grande "erreur de prédiction" possible.*
            """)

# ==============================================================================
# ONGLET 2 : HIÉRARCHIE (AVEC NOTE D'ATTENTE /100)
# ==============================================================================
with tab2:
    st.header("Liste des situations évitées / redoutées")
    st.caption("Hiérarchisation des situations selon votre croyance que le pire va arriver.")
    
    with st.expander("📚 Les caractéristiques de bons exercices d’exposition"):
        st.markdown("""
        **3 choses à faire :**
        * Exercices prolongés
        * Répétés
        * Rapprochés
        
        **3 choses à ne pas faire :**
        * Éviter
        * Fuir
        * Neutraliser
        """)

    with st.form("form_hierarchie"):
        sit = st.text_input("Situation redoutée :")
        
        # Bulle Info Spécifique demandée
        help_consequence_specifique = """Pour chacune des situations identifiées, essayez de décrire le plus précisément et concrètement possible ce que vous craignez qu’il survienne si vous l’affrontez. Si possible décrivez votre crainte d’une façon telle qu’il sera possible de savoir clairement si ça s’est produit ou pas.\n\nExemple : au lieu de « J’ai peur que mon anxiété paraisse », dites : « Je vais trembler de façon très apparente, je vais bafouiller à un point tel que les gens ne comprendront pas ce que je dis… »"""
        
        cons = st.text_area("Conséquence anticipée spécifique :", help=help_consequence_specifique, height=80)
        
        # Slider de 5 en 5, titre changé
        inc = st.slider("Probabilité que le scénario catastrophe se produise (0-100%)", 0, 100, 60, step=5)
        
        if st.form_submit_button("Ajouter à la hiérarchie"):
            new_row = {"Situation": sit, "Conséquence Anticipée": cons, "Attente (0-100)": inc}
            st.session_state.data_hierarchie = pd.concat([st.session_state.data_hierarchie, pd.DataFrame([new_row])], ignore_index=True)
            
            # Cloud
            from connect_db import save_data
            patient = st.session_state.get("patient_id", "Anonyme")
            # Note: J'utilise toujours l'onglet "Evitements" mais avec la nouvelle métrique
            save_data("Evitements", [patient, datetime.now().strftime("%Y-%m-%d"), sit, inc, cons, ""])
            st.success("Ajouté !")

    if not st.session_state.data_hierarchie.empty:
        st.divider()
        st.write("#### 📋 Votre Hiérarchie (Du plus redouté au moins redouté)")
        
        # Tri décroissant sur la colonne "Attente"
        df_sorted = st.session_state.data_hierarchie.sort_values(by="Attente (0-100)", ascending=False)
        st.dataframe(df_sorted, use_container_width=True)
        
        max_score = df_sorted["Attente (0-100)"].max()
        if max_score < 60:
            st.warning("⚠️ Vos scores d'attente sont bas (<60%). Peu d'apprentissage se produit si vous pensez déjà qu'il y a peu de chances que ça arrive.")
    
    st.divider()
    if st.button("✅ Valider l'Étape 2 (Hiérarchie terminée)"):
        st.balloons()
        st.success("Hiérarchie validée ! Passez à l'onglet 3 pour planifier.")

# ==============================================================================
# ONGLET 3 : PLANIFICATION (AVEC RÉÉVALUATION DE L'ATTENTE)
# ==============================================================================
with tab3:
    st.header("Planifier une activité")
    st.write("Choisissez une situation et ajustez les conditions (Facteurs).")
    
    # Info sur les 4 stratégies
    with st.expander("💡 Les 4 Stratégies Clés (Pour durcir l'exercice)"):
        st.markdown("""
        1. **Jetez-le ("Throw it Out")** : Éliminez les comportements de sécurité.
        2. **Restez avec ("Stay with It")** : Maintenez l'attention sur le déclencheur.
        3. **Combinez-le ("Combine It")** : Utilisez l'extinction approfondie (ajoutez des facteurs aggravants).
        4. **Affrontez-le ("Face It")** : Acceptez un échec réel occasionnel.
        """)
    
    if st.session_state.data_hierarchie.empty:
        st.warning("Remplissez la hiérarchie en onglet 2 d'abord.")
    else:
        # Sélection
        choix_sit = st.selectbox("Quelle situation voulez-vous planifier ?", st.session_state.data_hierarchie["Situation"].unique())
        
        # On récupère le score initial pour info
        row_sit = st.session_state.data_hierarchie[st.session_state.data_hierarchie["Situation"] == choix_sit].iloc[0]
        score_init = row_sit["Attente (0-100)"]
        
        st.info(f"Probabilité initiale que la catastrophe arrive (sans moduler) : **{score_init}%**")
        
        st.write("---")
        
        c1, c2 = st.columns(2)
        with c1:
            date_prevue = st.date_input("Date prévue", datetime.now())
        with c2:
            heure_prevue = st.time_input("Heure prévue", datetime.now().time())
            
        with st.container(border=True):
            st.write("**Configuration de l'exercice (Modulateurs)**")
            # On récupère les facteurs de l'onglet 1
            facteurs = st.session_state.data_crainte_centrale["Facteurs"]
            aggravants = [f['Description'] for f in facteurs if "Risque" in f['Type']]
            protecteurs = [f['Description'] for f in facteurs if "Protecteur" in f['Type']]
            
            sel_agg = []
            sel_prot = []
            
            col_a, col_b = st.columns(2)
            with col_a:
                if aggravants:
                    sel_agg = st.multiselect("➕ Je combine (Aggravants) :", aggravants)
            with col_b:
                if protecteurs:
                    sel_prot = st.multiselect("❌ Je jette (Protecteurs) :", protecteurs)
        
        st.write("---")
        st.markdown("#### Nouvelle évaluation de l'attente")
        st.write(f"Si vous faites l'exercice **{choix_sit}** en ajoutant **{len(sel_agg)} facteurs aggravants** et en retirant **{len(sel_prot)} sécurités**...")
        
        # LE NOUVEAU SLIDER DEMANDÉ
        nouvelle_attente = st.slider("À quel point êtes-vous sûr que la catastrophe va arriver DANS CES CONDITIONS ? (0-100%)", 0, 100, int(score_init), step=5)
        
        if nouvelle_attente < score_init:
            st.warning("⚠️ Attention : Vous devriez essayer de rendre l'exercice PLUS difficile (plus d'attente de catastrophe), pas moins.")
        elif nouvelle_attente > 80:
            st.success("🔥 Excellent ! C'est une situation à fort potentiel d'apprentissage (maximisation de la surprise).")

        if st.button("📅 Valider et Planifier"):
            resume_contexte = f"Aggravants: {', '.join(sel_agg)} | Sans: {', '.join(sel_prot)}"
            new_plan = {
                "Date": str(date_prevue),
                "Heure": str(heure_prevue),
                "Situation": choix_sit,
                "Attente Pré-Expo": nouvelle_attente
            }
            st.session_state.data_planning_expo = pd.concat([st.session_state.data_planning_expo, pd.DataFrame([new_plan])], ignore_index=True)
            
            # Cloud
            from connect_db import save_data
            patient = st.session_state.get("patient_id", "Anonyme")
            save_data("Expositions", [patient, str(date_prevue), choix_sit, resume_contexte, f"Attente:{nouvelle_attente}%", "PLANIFIÉ"])
            
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
    st.caption("Figure 3 : Consolidation de l'apprentissage inhibiteur.")
    
    if st.session_state.data_planning_expo.empty:
        st.warning("Planifiez d'abord un exercice dans l'onglet 3.")
    else:
        liste_prevus = [f"{row['Date']} : {row['Situation']}" for i, row in st.session_state.data_planning_expo.iterrows()]
        exo_realise = st.selectbox("Quel exercice avez-vous fait ?", liste_prevus)
        
        st.divider()
        
        with st.form("form_consolidation"):
            st.subheader("1. Avant / Pendant")
            # On demande à nouveau pour confirmer le souvenir
            pre_croyance = st.slider("Juste avant, à quel point étiez-vous sûr que la catastrophe allait arriver ? (0-100)", 0, 100, 80, step=5)
            
            st.subheader("2. Après (Réalité)")
            duree = st.number_input("Durée de l'exposition (minutes)", 0, 240, 20)
            
            st.write("**Est-ce que la catastrophe redoutée s'est produite ?**")
            resultat_reel = st.radio("", ["Oui, exactement comme prévu", "Oui, mais moins grave", "Non, pas du tout"], label_visibility="collapsed")
            
            st.write("**Niveau de Surprise (Erreur de prédiction)**")
            surprise = st.slider("À quel point le résultat vous a-t-il surpris ? (0 = Pas surpris, 100 = Totalement surpris)", 0, 100, 50, step=5)
            
            appr = st.text_area("Qu'avez-vous appris ? (Preuves accumulées)")
            
            st.subheader("3. Futur")
            post_croyance = st.slider("Si je recommençais maintenant, quelle est la probabilité que la catastrophe arrive ? (0-100)", 0, 100, 40, step=5)
            
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
                
                from connect_db import save_data
                patient = st.session_state.get("patient_id", "Anonyme")
                texte_bilan = f"PRE:{pre_croyance}% | POST:{post_croyance}% | SURPRISE:{surprise} | APPRIS:{appr}"
                save_data("Expositions", [patient, datetime.now().strftime("%Y-%m-%d"), exo_realise, "BILAN", str(duree), texte_bilan])
                
                st.success("Bilan enregistré ! C'est ainsi que le cerveau recâble la peur. Bravo.")
                st.balloons()

    if not st.session_state.data_logs_expo.empty:
        st.divider()
        st.write("#### 🧠 Vos apprentissages")
        st.dataframe(st.session_state.data_logs_expo[["Date", "Situation", "Pré-Croyance", "Post-Croyance", "Apprentissage"]], use_container_width=True)

st.divider()
st.page_link("streamlit_app.py", label="Retour à l'accueil", icon="🏠")