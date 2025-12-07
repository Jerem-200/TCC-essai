import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Exposition", page_icon="🧗")

# --- VIGILE ---
if "authentifie" not in st.session_state or not st.session_state.authentifie:
    st.warning("⛔ Veuillez vous connecter sur la page d'accueil.")
    st.switch_page("streamlit_app.py")
    st.stop()

st.title("🧗 L'Exposition (Apprentissage Inhibiteur)")

# --- 1. GESTION DES CRAINTES (FILTRAGE INTELLIGENT) ---
if "liste_craintes" not in st.session_state:
    st.session_state.liste_craintes = []

col_info, col_sel = st.columns([2, 2])
with col_info:
    st.info("Sur quelle thématique travaillez-vous ?")
with col_sel:
    with st.popover("➕ Nouvelle Crainte"):
        new_name = st.text_input("Nom (ex: Jugement, Mort...)")
        if st.button("Créer") and new_name:
            st.session_state.liste_craintes.append({"Nom": new_name, "Facteurs": []})
            st.rerun()

    if st.session_state.liste_craintes:
        options = [c["Nom"] for c in st.session_state.liste_craintes]
        choix_crainte = st.selectbox("Crainte active :", options, label_visibility="collapsed")
        crainte_active = next((c for c in st.session_state.liste_craintes if c["Nom"] == choix_crainte), None)
    else:
        st.warning("Créez d'abord une crainte ci-dessus pour commencer.")
        st.stop()

# --- INITIALISATION DATA ---
if "data_hierarchie" not in st.session_state:
    st.session_state.data_hierarchie = pd.DataFrame(columns=["Crainte", "Situation", "Conséquence", "Attente", "Anxiété"])
if "data_planning_expo" not in st.session_state:
    st.session_state.data_planning_expo = pd.DataFrame(columns=["Crainte", "Date", "Situation", "Attente"])
if "data_logs_expo" not in st.session_state:
    st.session_state.data_logs_expo = pd.DataFrame(columns=["Crainte", "Date", "Situation", "Planif-Attente", "Avant-Attente", "Après-Attente", "Apprentissage"])

# --- ONGLETS ---
tab1, tab2, tab3, tab4 = st.tabs(["1. Analyse", "2. Hiérarchie", "3. Planifier", "4. Consolider"])

# ==============================================================================
# ONGLET 1 : ANALYSE (Liée à la crainte active)
# ==============================================================================
with tab1:
    st.header(f"Analyse : {crainte_active['Nom']}")
    
    # 1.A DEFINITION
    help_crainte = "Identifiez la conséquence ultime (ex: 'Je vais faire une crise cardiaque'), pas juste la sensation."
    with st.expander("ℹ️ Aide : Définir la conséquence ultime"):
        st.info(help_crainte)
    
    # On stocke la définition dans le dictionnaire de la crainte
    current_def = crainte_active.get("Definition", "")
    new_def = st.text_area("Quelle est la catastrophe redoutée ?", value=current_def, help=help_crainte)
    if st.button("💾 Sauvegarder la définition"):
        crainte_active["Definition"] = new_def
        st.success("Définition enregistrée.")

    st.divider()

    # 1.B FACTEURS
    st.subheader("Facteurs aggravants & protecteurs")
    
    with st.form("ajout_facteur", clear_on_submit=True):
        c1, c2 = st.columns([3, 1])
        with c1: desc = st.text_input("Description :")
        with c2: type_f = st.selectbox("Type", ["🔴 Risque (Aggravant)", "🟢 Protecteur (Sécurité)"])
        
        is_main = False
        if "Risque" in type_f: is_main = st.checkbox("Déclencheur principal ?")
            
        if st.form_submit_button("Ajouter"):
            crainte_active["Facteurs"].append({"Description": desc, "Type": type_f, "Main": is_main})
            st.rerun()

    # Liste avec suppression
    if crainte_active["Facteurs"]:
        st.write("---")
        for i, f in enumerate(crainte_active["Facteurs"]):
            c_icon, c_txt, c_del = st.columns([1, 6, 1])
            with c_icon: st.write("🔥" if f.get("Main") else ("🔴" if "Risque" in f["Type"] else "🟢"))
            with c_txt: st.write(f"{'**[PRINCIPAL]** ' if f.get('Main') else ''}{f['Description']}")
            with c_del:
                if st.button("🗑️", key=f"del_fact_{i}"):
                    crainte_active["Facteurs"].pop(i)
                    st.rerun()

    st.divider()
    if st.button("✅ Valider l'Analyse et passer à l'étape suivante"):
        st.success("Analyse terminée ! Cliquez sur l'onglet **'2. Hiérarchie'** en haut.")
        with st.container(border=True):
            st.markdown("### 🔥 Concept : L'Exposition Ultime")
            st.markdown("Inclure le déclencheur + Ajouter les modulateurs + Supprimer les sécurités.")

# ==============================================================================
# ONGLET 2 : HIÉRARCHIE (Filtrée)
# ==============================================================================
with tab2:
    st.header(f"Hiérarchie ({crainte_active['Nom']})")
    st.info("Listez les situations évitées, de la moins pire à la pire.")

    with st.expander("📚 Bonnes pratiques"):
        st.write("**Faire :** Prolongé, Répété, Rapproché. **Ne pas faire :** Éviter, Fuir.")

    with st.form("form_hierarchie", clear_on_submit=True):
        sit = st.text_input("Situation :")
        cons = st.text_area("Crainte précise (Si je le fais, il va arriver...):", height=60)
        
        c1, c2 = st.columns(2)
        with c1: att = st.slider("Probabilité catastrophe (Attente 0-100%)", 0, 100, 60, step=5)
        with c2: anx = st.slider("Niveau Anxiété (0-100)", 0, 100, 60, step=5)
        
        if st.form_submit_button("Ajouter"):
            new = {"Crainte": crainte_active['Nom'], "Situation": sit, "Conséquence": cons, "Attente": att, "Anxiété": anx}
            st.session_state.data_hierarchie = pd.concat([st.session_state.data_hierarchie, pd.DataFrame([new])], ignore_index=True)
            
            # Cloud
            from connect_db import save_data
            patient = st.session_state.get("patient_id", "Anonyme")
            save_data("Evitements", [patient, datetime.now().strftime("%Y-%m-%d"), crainte_active['Nom'], sit, att, cons, f"Anx:{anx}"])
            st.success("Ajouté !")

    # FILTRAGE INTELLIGENT
    df = st.session_state.data_hierarchie
    df_filtre = df[df["Crainte"] == crainte_active['Nom']].sort_values(by="Attente", ascending=False)

    if not df_filtre.empty:
        st.divider()
        st.write("#### 📋 Votre échelle")
        for idx, row in df_filtre.iterrows():
            c_sc, c_tx, c_dl = st.columns([2, 5, 1])
            with c_sc: st.metric("Attente", f"{row['Attente']}%", f"Anx: {row['Anxiété']}")
            with c_tx: 
                st.markdown(f"**{row['Situation']}**")
                st.caption(row['Conséquence'])
            with c_dl:
                if st.button("🗑️", key=f"del_h_{idx}"):
                    st.session_state.data_hierarchie = df.drop(idx).reset_index(drop=True)
                    st.rerun()
    else:
        st.info("Liste vide pour cette crainte.")

    st.divider()
    if st.button("✅ Valider la Hiérarchie et passer à la Planification"):
        st.success("Hiérarchie validée ! Cliquez sur l'onglet **'3. Planifier'**.")

# ==============================================================================
# ONGLET 3 : PLANIFICATION (Filtrée)
# ==============================================================================
with tab3:
    st.header("Planifier un exercice")
    
    # On ne propose QUE les situations de la crainte active
    df_source = st.session_state.data_hierarchie
    situations_dispo = df_source[df_source["Crainte"] == crainte_active['Nom']]["Situation"].unique()
    
    if len(situations_dispo) == 0:
        st.warning("Remplissez la hiérarchie (Onglet 2) d'abord.")
    else:
        choix_sit = st.selectbox("Situation à affronter :", situations_dispo)
        
        # Récup score initial
        row_sit = df_source[(df_source["Crainte"] == crainte_active['Nom']) & (df_source["Situation"] == choix_sit)].iloc[0]
        st.caption(f"Score de base : Attente {row_sit['Attente']}%")
        
        c1, c2 = st.columns(2)
        with c1: date_p = st.date_input("Date")
        with c2: heure_p = st.time_input("Heure")
            
        with st.container(border=True):
            st.write("**Configuration**")
            aggs = [f['Description'] for f in crainte_active["Facteurs"] if "Risque" in f['Type']]
            prots = [f['Description'] for f in crainte_active["Facteurs"] if "Protecteur" in f['Type']]
            
            c_a, c_b = st.columns(2)
            with c_a: sel_agg = st.multiselect("➕ Je combine (Aggravants)", aggs)
            with c_b: sel_prot = st.multiselect("❌ Je jette (Protecteurs)", prots)
        
        st.markdown("#### Ré-évaluation")
        c3, c4 = st.columns(2)
        with c3: new_att = st.slider("Probabilité catastrophe ?", 0, 100, int(row_sit['Attente']), step=5, key="new_att")
        with c4: new_anx = st.slider("Niveau Anxiété ?", 0, 100, int(row_sit['Anxiété']), step=5, key="new_anx")

        if st.button("📅 Valider et Planifier"):
            resume = f"Aggravants: {', '.join(sel_agg)} | Sans: {', '.join(sel_prot)}"
            new_plan = {
                "Crainte": crainte_active['Nom'],
                "Date": str(date_p), "Heure": str(heure_p)[:5], "Situation": choix_sit,
                "Attente": new_att
            }
            st.session_state.data_planning_expo = pd.concat([st.session_state.data_planning_expo, pd.DataFrame([new_plan])], ignore_index=True)
            
            # Cloud
            from connect_db import save_data
            patient = st.session_state.get("patient_id", "Anonyme")
            # [Patient, Date, Crainte, Situation, Type, Details, Score1, Score2, Vide, Vide]
            save_data("Expositions", [
                patient, str(date_p), crainte_active['Nom'], choix_sit, 
                "PLANIFIÉ", resume, new_att, new_anx, "", ""
            ])
            st.success("Planifié !")

    # Planning Filtré
    df_plan = st.session_state.data_planning_expo
    df_plan_filtre = df_plan[df_plan["Crainte"] == crainte_active['Nom']]
    
    if not df_plan_filtre.empty:
        st.write("---")
        st.write("#### 🗓️ Vos exercices prévus")
        for idx, row in df_plan_filtre.iterrows():
            c_d, c_s, c_x = st.columns([2, 4, 1])
            with c_d: st.write(f"📅 {row['Date']} {row['Heure']}")
            with c_s: st.write(f"**{row['Situation']}** (Attente: {row['Attente']}%)")
            with c_x:
                if st.button("🗑️", key=f"del_plan_{idx}"):
                    st.session_state.data_planning_expo = df_plan.drop(idx).reset_index(drop=True)
                    st.rerun()

# ==============================================================================
# ONGLET 4 : CONSOLIDATION (Filtrée)
# ==============================================================================
with tab4:
    st.header("Consolidation")
    
    # On ne propose que les plans de la crainte active
    df_plan = st.session_state.data_planning_expo
    df_plan_filtre = df_plan[df_plan["Crainte"] == crainte_active['Nom']]
    
    if df_plan_filtre.empty:
        st.warning("Aucun exercice planifié pour cette crainte.")
    else:
        opts = [f"{r['Date']} : {r['Situation']}" for i, r in df_plan_filtre.iterrows()]
        choix_exo = st.selectbox("Exercice réalisé :", opts)
        
        # Retrouver les infos (Attente Planifiée)
        idx_match = df_plan_filtre[df_plan_filtre.apply(lambda r: f"{r['Date']} : {r['Situation']}" == choix_exo, axis=1)].index[0]
        attente_prevue = df_plan_filtre.loc[idx_match, "Attente"]
        
        st.divider()
        with st.form("form_bilan"):
            st.subheader("1. Juste avant")
            c1, c2 = st.columns(2)
            with c1: pre_att = st.slider("Probabilité catastrophe ?", 0, 100, 80, step=5, key="bilan_att")
            with c2: pre_anx = st.slider("Anxiété ?", 0, 100, 80, step=5, key="bilan_anx")
            
            st.subheader("2. Après")
            duree = st.number_input("Durée (min)", 0, 240, 20)
            q1 = st.text_area("Preuves que la catastrophe n'a pas eu lieu ?", height=70)
            q2 = st.text_area("Mes attentes vs Réalité ?", height=70)
            q3 = st.text_area("Surprise ?", height=70)
            q4 = st.text_area("Apprentissage ?", height=70)
            
            st.subheader("3. Futur")
            c3, c4 = st.columns(2)
            with c3: post_att = st.slider("Si je recommence, probabilité ?", 0, 100, 40, step=5, key="futur_att")
            with c4: post_anx = st.slider("Si je recommence, anxiété ?", 0, 100, 40, step=5, key="futur_anx")
            
            if st.form_submit_button("Enregistrer Bilan"):
                new_log = {
                    "Crainte": crainte_active['Nom'],
                    "Date": datetime.now().strftime("%Y-%m-%d"),
                    "Situation": choix_exo.split(" : ")[1],
                    "Planif-Attente": attente_prevue,
                    "Avant-Attente": pre_att,
                    "Après-Attente": post_att,
                    "Apprentissage": q4
                }
                st.session_state.data_logs_expo = pd.concat([st.session_state.data_logs_expo, pd.DataFrame([new_log])], ignore_index=True)
                
                # Cloud
                from connect_db import save_data
                patient = st.session_state.get("patient_id", "Anonyme")
                full_txt = f"Preuves:{q1}|Attente:{q2}|Surprise:{q3}|Leçon:{q4}"
                # [Patient, Date, Crainte, Situation, Type, Details, Score1, Score2, Score3, Texte]
                save_data("Expositions", [
                    patient, datetime.now().strftime("%Y-%m-%d"), 
                    crainte_active['Nom'], 
                    choix_exo.split(" : ")[1], 
                    "BILAN", f"{duree} min", pre_att, post_att, pre_anx, full_txt
                ])
                st.success("Bilan enregistré !")

    # Historique Filtré
    df_logs = st.session_state.data_logs_expo
    df_logs_filtre = df_logs[df_logs["Crainte"] == crainte_active['Nom']]
    
    if not df_logs_filtre.empty:
        st.divider()
        st.write("#### 🧠 Apprentissages (Cette crainte)")
        for idx, row in df_logs_filtre.iterrows():
            with st.expander(f"{row['Date']} - {row['Situation']}"):
                k1, k2, k3 = st.columns(3)
                with k1: st.metric("Planif", f"{row['Planif-Attente']}%")
                with k2: st.metric("Avant", f"{row['Avant-Attente']}%")
                with k3: st.metric("Après", f"{row['Après-Attente']}%", delta=f"{int(row['Après-Attente']) - int(row['Avant-Attente'])}%")
                st.info(row['Apprentissage'])

st.divider()
st.page_link("streamlit_app.py", label="Retour à l'accueil", icon="🏠")