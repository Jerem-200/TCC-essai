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

# --- 1. GESTION DES CRAINTES (MULTI-CRAINTES) ---
if "liste_craintes" not in st.session_state:
    st.session_state.liste_craintes = []

col_info, col_sel = st.columns([2, 2])
with col_info:
    st.info("Sur quelle thématique travaillez-vous aujourd'hui ?")

with col_sel:
    with st.popover("➕ Nouvelle Crainte"):
        new_name = st.text_input("Nom de la peur (ex: Jugement, Mort...)")
        if st.button("Créer") and new_name:
            st.session_state.liste_craintes.append({"Nom": new_name, "Facteurs": []})
            st.rerun()

    if st.session_state.liste_craintes:
        options = [c["Nom"] for c in st.session_state.liste_craintes]
        choix_crainte = st.selectbox("Crainte active :", options, label_visibility="collapsed")
        crainte_active = next((c for c in st.session_state.liste_craintes if c["Nom"] == choix_crainte), None)
    else:
        st.warning("Créez d'abord une crainte ci-dessus.")
        st.stop()

# --- INITIALISATION MÉMOIRE ---
if "data_hierarchie" not in st.session_state:
    st.session_state.data_hierarchie = pd.DataFrame(columns=["Crainte", "Situation", "Conséquence Anticipée", "Attente (0-100)", "Anxiété (0-100)"])
if "data_planning_expo" not in st.session_state:
    st.session_state.data_planning_expo = pd.DataFrame(columns=["Crainte", "Date", "Heure", "Situation", "Attente Pré-Expo", "Anxiété Pré-Expo"])
if "data_logs_expo" not in st.session_state:
    st.session_state.data_logs_expo = pd.DataFrame(columns=["Crainte", "Date", "Situation", "Planif-Attente", "Avant-Attente", "Après-Attente", "Apprentissage"])
if "step1_valide" not in st.session_state:
    st.session_state.step1_valide = False

# --- LES 4 ONGLETS ---
tab1, tab2, tab3, tab4 = st.tabs(["1. Analyse Crainte", "2. Hiérarchie", "3. Planifier", "4. Consolider"])

# ==============================================================================
# ONGLET 1 : ANALYSE
# ==============================================================================
with tab1:
    st.header(f"Analyse : {crainte_active['Nom']}")
    
    help_crainte = "Il faut identifier la conséquence ultime crainte (ex: 'Je vais faire une crise cardiaque'), et non juste la sensation de peur. Cela doit être testable objectivement."
    with st.expander("ℹ️ Aide : Comment définir sa crainte ?", expanded=False):
        st.info(help_crainte)
    
    current_def = crainte_active.get("Definition", "")
    new_def = st.text_area("Quelle est la conséquence terrible qui pourrait arriver ?", value=current_def, help=help_crainte)
    
    if st.button("💾 Sauvegarder la définition"):
        crainte_active["Definition"] = new_def
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
            crainte_active["Facteurs"].append(nouveau)
            st.rerun()

    if crainte_active["Facteurs"]:
        st.write("---")
        for i, f in enumerate(crainte_active["Facteurs"]):
            col_icon, col_txt, col_del = st.columns([1, 6, 1])
            with col_icon: st.write("🔥" if f.get("Main") else ("🔴" if "Risque" in f["Type"] else "🟢"))
            with col_txt: st.write(f"{'**[PRINCIPAL]** ' if f.get('Main') else ''}{f['Description']}")
            with col_del:
                if st.button("🗑️", key=f"del_fact_{i}"):
                    crainte_active["Facteurs"].pop(i)
                    st.rerun()

    st.divider()
    if st.button("✅ Valider l'Analyse et passer à l'étape suivante"):
        st.session_state.step1_valide = True
    
    if st.session_state.step1_valide:
        st.success("Analyse enregistrée ! Cliquez maintenant sur l'onglet **'2. Hiérarchie'** en haut.")
        with st.container(border=True):
            st.markdown("### 🔥 Concept : L'Exposition Ultime")
            st.markdown("Pour maximiser l'apprentissage (la surprise), l'exposition idéale doit : 1. Inclure le **déclencheur principal**. 2. Ajouter les **modulateurs positifs**. 3. Supprimer les **signaux de sécurité**.")

# ==============================================================================
# ONGLET 2 : HIÉRARCHIE (Filtrée)
# ==============================================================================
with tab2:
    st.header(f"Hiérarchie ({crainte_active['Nom']})")
    st.info("Dressez une liste aussi complète que possible de toutes les situations que vous évitez ou que vous redoutez.")

    with st.expander("📚 Les caractéristiques de bons exercices"):
        st.markdown("**À faire :** Prolongés, Répétés, Rapprochés.\n**À ne pas faire :** Éviter, Fuir, Neutraliser.")

    with st.form("form_hierarchie"):
        sit = st.text_input("Situation redoutée :")
        cons = st.text_area("Conséquence anticipée spécifique :", height=80, help="Décrivez précisément ce que vous craignez (ex: bafouiller, trembler...).")
        
        c1, c2 = st.columns(2)
        with c1: attente = st.slider("Probabilité que la catastrophe arrive (0-100%)", 0, 100, 60, step=5, key="h_attente")
        with c2: anxiete = st.slider("Niveau d'Anxiété (0-100)", 0, 100, 60, step=5, key="h_anxiete")
        
        if st.form_submit_button("Ajouter à la hiérarchie"):
            new_row = {"Crainte": crainte_active['Nom'], "Situation": sit, "Conséquence Anticipée": cons, "Attente (0-100)": attente, "Anxiété (0-100)": anxiete}
            st.session_state.data_hierarchie = pd.concat([st.session_state.data_hierarchie, pd.DataFrame([new_row])], ignore_index=True)
            
            from connect_db import save_data
            patient = st.session_state.get("patient_id", "Anonyme")
            save_data("Evitements", [patient, datetime.now().strftime("%Y-%m-%d"), crainte_active['Nom'], sit, attente, cons, f"Anx:{anxiete}"])
            st.success("Ajouté !")

    # Affichage filtré
    df = st.session_state.data_hierarchie
    df_filtre = df[df["Crainte"] == crainte_active['Nom']].sort_values(by="Attente (0-100)", ascending=False)

    if not df_filtre.empty:
        st.divider()
        st.write("#### 📋 Votre Hiérarchie")
        for idx, row in df_filtre.iterrows():
            c_sc, c_tx, c_dl = st.columns([2, 5, 1])
            with c_sc: st.metric("Attente", f"{row['Attente (0-100)']}%", f"Anx: {row['Anxiété (0-100)']}")
            with c_tx: 
                st.markdown(f"**{row['Situation']}**")
                st.caption(row['Conséquence Anticipée'])
            with c_dl:
                if st.button("🗑️", key=f"del_h_{idx}"):
                    st.session_state.data_hierarchie = df.drop(idx).reset_index(drop=True)
                    st.rerun()
        
        if df_filtre["Attente (0-100)"].max() < 60:
            st.warning("⚠️ Vos scores d'attente sont bas (<60%).")
    
    st.divider()
    if st.button("✅ Valider l'Étape 2"):
        st.success("Hiérarchie validée !")

# ==============================================================================
# ONGLET 3 : PLANIFICATION (Filtrée)
# ==============================================================================
with tab3:
    st.header("Planifier une activité")
    
    df_source = st.session_state.data_hierarchie
    situations_dispo = df_source[df_source["Crainte"] == crainte_active['Nom']]["Situation"].unique()
    
    if len(situations_dispo) == 0:
        st.warning("Remplissez la hiérarchie en onglet 2 d'abord.")
    else:
        choix_sit = st.selectbox("Quelle situation voulez-vous planifier ?", situations_dispo)
        row_sit = df_source[(df_source["Crainte"] == crainte_active['Nom']) & (df_source["Situation"] == choix_sit)].iloc[0]
        score_init = row_sit["Attente (0-100)"]
        anx_init = row_sit.get("Anxiété (0-100)", 0)
        
        st.caption(f"Score initial : Attente {score_init}% | Anxiété {anx_init}/100")
        st.write("---")
        
        c1, c2 = st.columns(2)
        with c1: date_prevue = st.date_input("Date prévue", datetime.now())
        with c2: heure_prevue = st.time_input("Heure prévue", datetime.now().time())
            
        with st.container(border=True):
            st.write("**Configuration (Modulateurs)**")
            aggravants = [f['Description'] for f in crainte_active["Facteurs"] if "Risque" in f['Type']]
            protecteurs = [f['Description'] for f in crainte_active["Facteurs"] if "Protecteur" in f['Type']]
            
            c_a, c_b = st.columns(2)
            with c_a: sel_agg = st.multiselect("➕ Je combine (Aggravants) :", aggravants) if aggravants else []
            with c_b: sel_prot = st.multiselect("❌ Je jette (Protecteurs) :", protecteurs) if protecteurs else []
        
        st.write("---")
        st.markdown("#### Ré-évaluation de l'attente avec ces conditions")
        c3, c4 = st.columns(2)
        with c3: nouvelle_attente = st.slider("Probabilité catastrophe (0-100%)", 0, 100, int(score_init), step=5, key="p_attente")
        with c4: nouvelle_anxiete = st.slider("Niveau d'Anxiété (0-100)", 0, 100, int(anx_init), step=5, key="p_anxiete")

        if st.button("📅 Valider et Planifier"):
            heure_propre = str(heure_prevue)[:5] 
            resume_contexte = f"Aggravants: {', '.join(sel_agg)} | Sans: {', '.join(sel_prot)}"
            
            new_plan = {
                "Crainte": crainte_active['Nom'], "Date": str(date_prevue), "Heure": heure_propre, 
                "Situation": choix_sit, "Attente Pré-Expo": nouvelle_attente, "Anxiété Pré-Expo": nouvelle_anxiete
            }
            st.session_state.data_planning_expo = pd.concat([st.session_state.data_planning_expo, pd.DataFrame([new_plan])], ignore_index=True)
            
            from connect_db import save_data
            patient = st.session_state.get("patient_id", "Anonyme")
            save_data("Expositions", [patient, str(date_prevue), crainte_active['Nom'], choix_sit, "PLANIFIÉ", resume_contexte, nouvelle_attente, nouvelle_anxiete, "", ""])
            st.success(f"Exercice ajouté pour le {date_prevue} à {heure_propre} !")

    df_plan = st.session_state.data_planning_expo
    df_plan_filtre = df_plan[df_plan["Crainte"] == crainte_active['Nom']]
    
    if not df_plan_filtre.empty:
        st.write("---")
        st.write("#### 🗓️ Vos exercices à venir")
        for idx, row in df_plan_filtre.iterrows():
            c_d, c_s, c_x = st.columns([2, 4, 1])
            with c_d: st.write(f"📅 {row['Date']} {row['Heure']}")
            with c_s: st.write(f"**{row['Situation']}** (Attente: {row['Attente Pré-Expo']}%)")
            with c_x:
                if st.button("🗑️", key=f"del_plan_{idx}"):
                    st.session_state.data_planning_expo = df_plan.drop(idx).reset_index(drop=True)
                    st.rerun()

# ==============================================================================
# ONGLET 4 : CONSOLIDATION (Filtrée)
# ==============================================================================
with tab4:
    st.header("Grille d'auto-observation (Après l'exercice)")
    
    df_plan = st.session_state.data_planning_expo
    df_plan_filtre = df_plan[df_plan["Crainte"] == crainte_active['Nom']]
    
    if df_plan_filtre.empty:
        st.warning("Planifiez d'abord un exercice dans l'onglet 3.")
    else:
        opts = [f"{r['Date']} {r['Heure']} : {r['Situation']}" for i, r in df_plan_filtre.iterrows()]
        choix_exo_str = st.selectbox("Quel exercice avez-vous fait ?", opts)
        
        # Retrouver les infos
        idx_match = df_plan_filtre[df_plan_filtre.apply(lambda r: f"{r['Date']} {r['Heure']} : {r['Situation']}" == choix_exo_str, axis=1)].index[0]
        donnees_planif = st.session_state.data_planning_expo.iloc[idx_match]
        attente_planif = donnees_planif.get("Attente Pré-Expo", "?")
        
        st.divider()
        with st.form("form_consolidation"):
            st.subheader("1. Juste avant / Pendant")
            c1, c2 = st.columns(2)
            with c1: pre_att = st.slider("Probabilité catastrophe (0-100%)", 0, 100, 80, step=5, key="c_att_pre")
            with c2: pre_anx = st.slider("Niveau d'Anxiété (0-100)", 0, 100, 80, step=5, key="c_anx_pre")
            
            st.divider()
            st.subheader("2. Après (Réalité)")
            duree = st.number_input("Durée (minutes)", 0, 240, 20)
            
            st.markdown("**Analyse de l'expérience :**")
            st.write("**Est-ce que la catastrophe redoutée s'est produite ?**")
            resultat_reel = st.radio("", ["Oui, exactement comme prévu", "Oui, mais moins grave", "Non, pas du tout"], label_visibility="collapsed")
            
            q1 = st.text_area("Comment je sais que ma crainte ne s'est pas réalisée ?", height=70)
            q2 = st.text_area("À quoi je m'attendais suite à cette expérience ?", height=70)
            q3 = st.text_area("Que s'est-il passé ? Cela m'a-t-il surpris ?", height=70)
            q4 = st.text_area("Qu'en ai-je appris ?", height=70)
            appr_complet = f"Preuves: {q1} | Attentes: {q2} | Réalité: {q3} | Leçon: {q4}"
            
            st.divider()
            st.subheader("3. Ré-évaluation (Futur)")
            c3, c4 = st.columns(2)
            with c3: post_att = st.slider("Si je recommence, probabilité catastrophe ?", 0, 100, 40, step=5, key="c_att_post")
            with c4: post_anx = st.slider("Si je recommence, anxiété ?", 0, 100, 40, step=5, key="c_anx_post")
            
            if st.form_submit_button("Enregistrer Bilan"):
                new_log = {
                    "Crainte": crainte_active['Nom'], "Date": datetime.now().strftime("%Y-%m-%d"),
                    "Situation": donnees_planif['Situation'], "Planif-Attente": attente_planif,
                    "Avant-Attente": pre_att, "Après-Attente": post_att, "Apprentissage": q4
                }
                st.session_state.data_logs_expo = pd.concat([st.session_state.data_logs_expo, pd.DataFrame([new_log])], ignore_index=True)
                
                from connect_db import save_data
                patient = st.session_state.get("patient_id", "Anonyme")
                save_data("Expositions", [
                    patient, datetime.now().strftime("%Y-%m-%d"), crainte_active['Nom'],
                    donnees_planif['Situation'], "BILAN", f"{duree} min", pre_att, post_att, pre_anx, post_anx, appr_complet
                ])
                st.success("Bilan enregistré ! Bravo.")

    # Historique Filtré
    df_logs = st.session_state.data_logs_expo
    df_logs_filtre = df_logs[df_logs["Crainte"] == crainte_active['Nom']]
    
    if not df_logs_filtre.empty:
        st.divider()
        st.write(f"#### 🧠 Apprentissages ({crainte_active['Nom']})")
        for idx, row in df_logs_filtre.iterrows():
            with st.expander(f"{row['Date']} - {row['Situation']}"):
                k1, k2, k3 = st.columns(3)
                with k1: st.metric("Planif", f"{row['Planif-Attente']}%")
                with k2: st.metric("Avant", f"{row['Avant-Attente']}%")
                with k3: st.metric("Après", f"{row['Après-Attente']}%", delta=f"{int(row['Après-Attente']) - int(row['Avant-Attente'])}%")
                st.info(row['Apprentissage'])

st.divider()
st.page_link("streamlit_app.py", label="Retour à l'accueil", icon="🏠")