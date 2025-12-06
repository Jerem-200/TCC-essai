import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Exposition", page_icon="🧗")

# --- VIGILE DE SÉCURITÉ ---
if "authentifie" not in st.session_state or not st.session_state.authentifie:
    st.warning("⛔ Veuillez vous connecter sur la page d'accueil.")
    st.switch_page("streamlit_app.py")
    st.stop()

st.title("🧗 Exercice d'exposition")

# --- INITIALISATION MÉMOIRE ---
if "data_crainte_centrale" not in st.session_state:
    st.session_state.data_crainte_centrale = {"Crainte": "", "Facteurs": []}

if "data_hierarchie" not in st.session_state:
    # Ajout colonne Anxiété
    st.session_state.data_hierarchie = pd.DataFrame(columns=["Situation", "Conséquence Anticipée", "Attente (0-100)", "Anxiété (0-100)"])

if "data_planning_expo" not in st.session_state:
    st.session_state.data_planning_expo = pd.DataFrame(columns=["Date", "Heure", "Situation", "Attente Pré-Expo", "Anxiété Pré-Expo"])

if "data_logs_expo" not in st.session_state:
    st.session_state.data_logs_expo = pd.DataFrame(columns=[
        "Date", "Situation", "Planif-Attente", "Avant-Attente", "Après-Attente", "Apprentissage"
    ])

# Variable pour valider l'étape 1
if "step1_valide" not in st.session_state:
    st.session_state.step1_valide = False

# --- LES 4 ONGLETS ---
tab1, tab2, tab3, tab4 = st.tabs(["1. Analyse Crainte", "2. Hiérarchie", "3. Planifier", "4. Consolider"])

# ==============================================================================
# ONGLET 1 : ANALYSE (INCHANGÉ MAIS AVEC LE BOUTON)
# ==============================================================================
with tab1:
    st.header("A. La Crainte Centrale")
    help_crainte = "Il faut identifier la conséquence ultime crainte (ex: 'Je vais faire une crise cardiaque'), et non juste la sensation de peur. Cela doit être testable objectivement."
    with st.expander("ℹ️ Aide : Comment définir sa crainte ?", expanded=False):
        st.info(help_crainte)
    
    crainte_actuelle = st.session_state.data_crainte_centrale["Crainte"]
    nouvelle_crainte = st.text_area("Quelle est la conséquence terrible qui pourrait arriver ?", value=crainte_actuelle, help=help_crainte)
    
    if st.button("💾 Sauvegarder la définition"):
        st.session_state.data_crainte_centrale["Crainte"] = nouvelle_crainte
        st.success("Crainte définie.")

    st.divider()
    st.header("B. Analyse des Facteurs")
    
    with st.form("ajout_facteur"):
        c1, c2 = st.columns([3, 1])
        with c1: desc_facteur = st.text_input("Description du facteur :")
        with c2: type_facteur = st.selectbox("Type", ["🔴 Risque (Aggravant)", "🟢 Protecteur (Sécurité)"])
        
        is_main_trigger = False
        if "Risque" in type_facteur: is_main_trigger = st.checkbox("Est-ce le déclencheur principal (CS) ?")
            
        if st.form_submit_button("Ajouter ce facteur"):
            nouveau = {"Description": desc_facteur, "Type": type_facteur, "Main": is_main_trigger}
            st.session_state.data_crainte_centrale["Facteurs"].append(nouveau)
            st.rerun()

    if st.session_state.data_crainte_centrale["Facteurs"]:
        for i, f in enumerate(st.session_state.data_crainte_centrale["Facteurs"]):
            col_icon, col_txt, col_del = st.columns([1, 6, 1])
            with col_icon: st.write("🔥" if f["Main"] else ("🔴" if "Risque" in f["Type"] else "🟢"))
            with col_txt: st.write(f"{'**[DÉCLENCHEUR]** ' if f['Main'] else ''}{f['Description']}")
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

# Texte explicatif demandé
    st.info("Dressez une liste aussi complète que possible de toutes les situations que vous évitez ou que vous redoutez en raison de la crainte qu’elles provoquent. L'objectif est de vous exposer à certaines de ces situations dans le futur.")

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
     
        cons = st.text_area("Conséquence anticipée spécifique :", height=80, help="Pour chacune des situations identifiées dans votre liste, essayez de décrire le plus précisément et concrètement possible ce que vous craignez qu’il survienne si vous l’affrontez. Si possible décrivez votre crainte d’une façon telle qu’il sera possible de savoir clairement si ça s’est produit ou pas. Par exemple, une personne souffrant d’anxiété sociale qui a écrit : « J’ai peur que mon anxiété paraisse beaucoup » aurait intérêt à la décrire plus spécifiquement : « Je vais trembler de façon très apparente, je vais bafouiller à un point tel que les gens ne comprendront pas ce que je dis… ».")
        
        # Double curseur (Attente + Anxiété)
        c1, c2 = st.columns(2)
        with c1:
            attente = st.slider("Probabilité que la catastrophe arrive (0-100% - 0% : Pas du tout, 25% : possible, 50% : 50/50, 75% : probable, 100% : c'est certain)", 0, 100, 60, step=5, key="h_attente")
        with c2:
            anxiete = st.slider("Niveau d'Anxiété (0-100)", 0, 100, 60, step=5, key="h_anxiete")
        
        if st.form_submit_button("Ajouter à la hiérarchie"):
            new_row = {"Situation": sit, "Conséquence Anticipée": cons, "Attente (0-100)": attente, "Anxiété (0-100)": anxiete}
            st.session_state.data_hierarchie = pd.concat([st.session_state.data_hierarchie, pd.DataFrame([new_row])], ignore_index=True)
            
            from connect_db import save_data
            patient = st.session_state.get("patient_id", "Anonyme")
            save_data("Evitements", [patient, datetime.now().strftime("%Y-%m-%d"), sit, attente, cons, f"Anxiété:{anxiete}"])
            st.success("Ajouté !")

    if not st.session_state.data_hierarchie.empty:
        st.divider()
        st.write("#### 📋 Votre Hiérarchie")
        df_sorted = st.session_state.data_hierarchie.sort_values(by="Attente (0-100)", ascending=False)
        st.dataframe(df_sorted, use_container_width=True)
        
        if df_sorted["Attente (0-100)"].max() < 60:
            st.warning("⚠️ Vos scores d'attente sont bas (<60%).")
    
    st.divider()
    if st.button("✅ Valider l'Étape 2"):
        st.success("Hiérarchie validée !")

# ==============================================================================
# ONGLET 3 : PLANIFICATION (AVEC HEURE PROPRE ET DOUBLE CURSEUR)
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
        choix_sit = st.selectbox("Quelle situation voulez-vous planifier ?", st.session_state.data_hierarchie["Situation"].unique())
        
        # Récupération des scores initiaux
        row_sit = st.session_state.data_hierarchie[st.session_state.data_hierarchie["Situation"] == choix_sit].iloc[0]
        score_init = row_sit["Attente (0-100)"]
        anx_init = row_sit.get("Anxiété (0-100)", 0) # .get au cas où la colonne n'existait pas avant
        
        st.caption(f"Score initial (dans la liste) : Attente {score_init}% | Anxiété {anx_init}/100")
        
        st.write("---")
        
        c1, c2 = st.columns(2)
        with c1: date_prevue = st.date_input("Date prévue", datetime.now())
        with c2: heure_prevue = st.time_input("Heure prévue", datetime.now().time())
            
        with st.container(border=True):
            st.write("**Configuration (Modulateurs)**")
            facteurs = st.session_state.data_crainte_centrale["Facteurs"]
            aggravants = [f['Description'] for f in facteurs if "Risque" in f['Type']]
            protecteurs = [f['Description'] for f in facteurs if "Protecteur" in f['Type']]
            
            c_a, c_b = st.columns(2)
            with c_a: 
                sel_agg = st.multiselect("➕ Je combine (Aggravants) :", aggravants) if aggravants else []
            with c_b: 
                sel_prot = st.multiselect("❌ Je jette (Protecteurs) :", protecteurs) if protecteurs else []
        
        st.write("---")
        st.markdown("#### Ré-évaluation de l'attente avec ces conditions")
        st.write(f"Si vous faites l'exercice **{choix_sit}** en ajoutant **{len(sel_agg)} facteurs aggravants** et en retirant **{len(sel_prot)} sécurités**...")
        
        # DOUBLE CURSEUR ICI AUSSI
        col_att, col_anx = st.columns(2)
        with col_att:
            nouvelle_attente = st.slider("Probabilité catastrophe (0-100%)", 0, 100, int(score_init), step=5, key="p_attente")
        with col_anx:
            nouvelle_anxiete = st.slider("Niveau d'Anxiété (0-100)", 0, 100, int(anx_init), step=5, key="p_anxiete")
        
        if nouvelle_attente < score_init:
            st.warning("⚠️ Attention : Vous devriez essayer de rendre l'exercice PLUS difficile (plus d'attente de catastrophe), pour pouvoir créer un apprentissage.")
        elif nouvelle_attente > 80:
            st.success("🔥 Excellent ! C'est une situation à fort potentiel d'apprentissage (maximisation de la surprise).")

        if st.button("📅 Valider et Planifier"):
            heure_propre = str(heure_prevue)[:5] 
            resume_contexte = f"Aggravants: {', '.join(sel_agg)} | Sans: {', '.join(sel_prot)}"
            
            new_plan = {
                "Date": str(date_prevue), 
                "Heure": heure_propre, 
                "Situation": choix_sit,
                "Attente Pré-Expo": nouvelle_attente, 
                "Anxiété Pré-Expo": nouvelle_anxiete
            }
            st.session_state.data_planning_expo = pd.concat([st.session_state.data_planning_expo, pd.DataFrame([new_plan])], ignore_index=True)
            
            # --- CORRECTION ICI ---
            from connect_db import save_data
            patient = st.session_state.get("patient_id", "Anonyme")
            
            # On envoie une chaîne vide "" à la fin car 'affronte_txt' n'existe plus ici
            save_data("Expositions", [
                patient, 
                str(date_prevue), 
                choix_sit, 
                "PLANIFIÉ", 
                resume_contexte,    # Colonne E
                nouvelle_attente,   # Colonne F
                nouvelle_anxiete,   # Colonne G
                "",                 # Colonne H (Vide)
                ""                  # Colonne I (Vide, remplace l'erreur)
            ])
            
            st.success(f"Exercice ajouté pour le {date_prevue} à {heure_propre} !")
            
    if not st.session_state.data_planning_expo.empty:
        st.write("---")
        st.write("#### 🗓️ Vos exercices à venir")
        st.dataframe(st.session_state.data_planning_expo, use_container_width=True)

# ==============================================================================
# ONGLET 4 : CONSOLIDATION (NOUVELLES QUESTIONS + COMPARATIF 3 TEMPS)
# ==============================================================================
with tab4:
    st.header("Grille d'auto-observation (Après l'exercice)")
    
    if st.session_state.data_planning_expo.empty:
        st.warning("Planifiez d'abord un exercice dans l'onglet 3.")
    else:
        # Liste pour choisir l'exercice
        liste_prevus = [f"{row['Date']} {row['Heure']} : {row['Situation']}" for i, row in st.session_state.data_planning_expo.iterrows()]
        choix_exo_str = st.selectbox("Quel exercice avez-vous fait ?", liste_prevus)
        
        # On retrouve les données planifiées pour faire le comparatif
        # (On triche un peu en cherchant par l'index dans la liste, supposant que l'ordre n'a pas changé)
        index_exo = liste_prevus.index(choix_exo_str)
        donnees_planif = st.session_state.data_planning_expo.iloc[index_exo]
        attente_planif = donnees_planif.get("Attente Pré-Expo", "?")
        
        st.divider()
        
        with st.form("form_consolidation"):
            
            # TEMPS 2 : JUSTE AVANT / PENDANT
            st.subheader("1. Juste avant / Pendant l'exercice")
            c1, c2 = st.columns(2)
            with c1:
                pre_attente = st.slider("Probabilité catastrophe (0-100%)", 0, 100, 80, step=5, key="c_attente_pre")
            with c2:
                pre_anxiete = st.slider("Niveau d'Anxiété (0-100)", 0, 100, 80, step=5, key="c_anxiete_pre")
            
            st.divider()
            
            # TEMPS 3 : APRÈS (RÉALITÉ)
            st.subheader("2. Après (Réalité)")
            duree = st.number_input("Durée (minutes)", 0, 240, 20)


            # Nouvelles questions demandées
            st.markdown("**Analyse de l'expérience :**")

            st.write("**Est-ce que la catastrophe redoutée s'est produite ?**")
            resultat_reel = st.radio("", ["Oui, exactement comme prévu", "Oui, mais moins grave", "Non, pas du tout"], label_visibility="collapsed")
            
            q1 = st.text_area("Comment je sais que ma crainte ne s'est pas réalisée ?", height=70)
            q2 = st.text_area("À quoi je m'attendais suite à cette expérience ?", height=70)
            q3 = st.text_area("Que s'est-il passé ? Cela m'a-t-il surpris ?", height=70)
            q4 = st.text_area("Qu'en ai-je appris ?", height=70)
            
            # Compilation du texte d'apprentissage
            appr_complet = f"Preuves: {q1} | Attentes: {q2} | Réalité: {q3} | Leçon: {q4}"
            
            st.divider()
            
            # TEMPS 4 : FUTUR (RÉÉVALUATION)
            st.subheader("3. Ré-évaluation (Futur)")
            c3, c4 = st.columns(2)
            with c3:
                post_attente = st.slider("Si je recommençais maintenant, quelle serait la probabilité que la catastrophe arrive ? (0-100% - 0% : Pas du tout, 25% : possible, 50% : 50/50, 75% : probable, 100% : c'est certain)", 0, 100, 40, step=5, key="c_attente_post")
            with c4:
                post_anxiete = st.slider("Si je recommençais, Si je recommençais maintenant, quelle serait mon niveau d'anxiété ? (0-100)", 0, 100, 40, step=5, key="c_anxiete_post")
            
            submit_log = st.form_submit_button("Enregistrer le Bilan")
            
            if submit_log:
                new_log = {
                    "Date": datetime.now().strftime("%Y-%m-%d"),
                    "Situation": choix_exo_str, # <--- Variable corrigée
                    "Planif-Attente": attente_planif,
                    "Avant-Attente": pre_attente,
                    "Après-Attente": post_attente,
                    "Apprentissage": q4
                }
                st.session_state.data_logs_expo = pd.concat([st.session_state.data_logs_expo, pd.DataFrame([new_log])], ignore_index=True)
                
                # SAUVEGARDE CLOUD CORRIGÉE
                from connect_db import save_data
                patient = st.session_state.get("patient_id", "Anonyme")
                
                # Ordre : [Patient, Date, Situation, TYPE, Durée, AttenteAvant, AttenteApres, Anxiete(H), Apprentissage(I)]
                save_data("Expositions", [
                    patient, 
                    datetime.now().strftime("%Y-%m-%d"), 
                    choix_exo_str,  # <--- Variable corrigée
                    "BILAN", 
                    f"{duree} min", 
                    pre_attente,    # Colonne F
                    post_attente,   # Colonne G
                    pre_anxiete,    # Colonne H (On met l'anxiété ici car 'surprise' n'existe plus)
                    post_anxiete,   # Colonne I
                    appr_complet    
                ])
                
                st.success("Bilan enregistré ! Bravo.")

    # Historique Visuel des 3 Temps
    if not st.session_state.data_logs_expo.empty:
        st.divider()
        st.write("#### 🧠 Évolution de vos croyances (Comparatif)")
        for i, row in st.session_state.data_logs_expo.iterrows():
            with st.expander(f"{row['Date']} - {row['Situation']}"):
                # Affichage des 3 temps en colonnes
                k1, k2, k3 = st.columns(3)
                with k1: st.metric("1. À la planification", f"{row['Planif-Attente']}%")
                with k2: st.metric("2. Juste avant", f"{row['Avant-Attente']}%")
                with k3: st.metric("3. Après", f"{row['Après-Attente']}%", delta=f"{int(row['Après-Attente']) - int(row['Avant-Attente'])}%")
                
                st.info(f"**Apprentissage :** {row['Apprentissage']}")

st.divider()
st.page_link("streamlit_app.py", label="Retour à l'accueil", icon="🏠")