import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Exposition", page_icon="🧗")

# ==============================================================================
# 0. SÉCURITÉ, NETTOYAGE & PERMISSIONS
# ==============================================================================

# A. AUTHENTIFICATION
if "authentifie" not in st.session_state or not st.session_state.authentifie:
    st.warning("🔒 Accès restreint. Veuillez entrer votre Code Patient sur l'accueil.")
    st.page_link("streamlit_app.py", label="Retourner à l'accueil", icon="🏠")
    st.stop()

# B. RÉCUPÉRATION ID
CURRENT_USER_ID = st.session_state.get("user_id", "")
if not CURRENT_USER_ID:
    st.error("Session expirée. Veuillez vous reconnecter.")
    st.stop()

# C. ANTI-FUITE (Spécifique à la page Exposition)
if "expo_owner" not in st.session_state or st.session_state.expo_owner != CURRENT_USER_ID:
    # On supprime les données en cache si on change de patient
    if "data_exposition" in st.session_state: del st.session_state.data_exposition
    st.session_state.expo_owner = CURRENT_USER_ID

# D. LE VIGILE (PERMISSIONS)
CLE_PAGE = "expo"  # <--- Clé spécifique pour l'Exposition

if st.session_state.get("user_type") == "patient":
    try:
        from connect_db import load_data
        perms = load_data("Permissions")
        if perms:
            df_perm = pd.DataFrame(perms)
            row = df_perm[df_perm["Patient"] == CURRENT_USER_ID]
            if not row.empty:
                bloques = str(row.iloc[0]["Bloques"]).split(",")
                if CLE_PAGE in [b.strip() for b in bloques]:
                    st.error("🔒 Cette fonctionnalité n'est pas activée dans votre programme.")
                    st.info("Voyez avec votre thérapeute si vous pensez qu'il s'agit d'une erreur.")
                    if st.button("Retour à l'accueil"):
                        st.switch_page("streamlit_app.py")
                    st.stop()
    except Exception as e:
        pass 

# ==============================================================================
# CONTENU PRINCIPAL
# ==============================================================================
st.title("🧗 L'Exposition (Apprentissage Inhibiteur)")

# --- 1. GESTION DES CRAINTES (MULTI-CRAINTES) ---
if "liste_craintes" not in st.session_state:
    st.session_state.liste_craintes = []

col_info, col_new = st.columns([3, 1])
with col_info:
    st.info("Sur quelle thématique travaillez-vous aujourd'hui ?")

with col_new:
    # Bouton pour créer une nouvelle crainte
    with st.popover("➕ Nouvelle Crainte"):
        new_crainte_name = st.text_input("Nom de la peur (ex: Jugement)")
        if st.button("Créer"):
            if new_crainte_name:
                st.session_state.liste_craintes.append({"Nom": new_crainte_name, "Facteurs": []})
                st.rerun()

# --- SÉLECTEUR AVEC SUPPRESSION ---
if st.session_state.liste_craintes:
    c_sel, c_del = st.columns([5, 1])
    
    with c_sel:
        options_craintes = [c["Nom"] for c in st.session_state.liste_craintes]
        choix_crainte = st.selectbox("Crainte active :", options_craintes, label_visibility="collapsed")
    
    with c_del:
        if st.button("🗑️", help="Supprimer cette thématique"):
            # On supprime la crainte de la liste
            st.session_state.liste_craintes = [c for c in st.session_state.liste_craintes if c["Nom"] != choix_crainte]
            st.rerun()
            
    # On récupère l'objet crainte complet (s'il existe encore après suppression)
    crainte_active = next((c for c in st.session_state.liste_craintes if c["Nom"] == choix_crainte), None)
    
    if not crainte_active:
        st.stop() # Sécurité si on vient de tout supprimer
else:
    st.warning("Commencez par créer une thématique de peur (ex: 'Peur de mourir', 'Peur sociale').")
    st.stop()

    
# --- INITIALISATION DES DONNÉES ---
if "data_hierarchie" not in st.session_state:
    # Ajout colonne Crainte
    st.session_state.data_hierarchie = pd.DataFrame(columns=["Crainte", "Situation", "Conséquence Anticipée", "Attente (0-100)", "Anxiété (0-100)"])

if "data_planning_expo" not in st.session_state:
    st.session_state.data_planning_expo = pd.DataFrame(columns=["Crainte", "Date", "Heure", "Situation", "Attente Pré-Expo", "Anxiété Pré-Expo"])

if "data_logs_expo" not in st.session_state:
    st.session_state.data_logs_expo = pd.DataFrame(columns=["Crainte", "Date", "Situation", "Planif-Attente", "Avant-Attente", "Après-Attente", "Apprentissage"])

if "step1_valide" not in st.session_state:
    st.session_state.step1_valide = False

# --- ONGLETS ---
tab1, tab2, tab3, tab4 = st.tabs(["1. Analyse", "2. Hiérarchie", "3. Planifier", "4. Consolider"])

# ==============================================================================
# ONGLET 1 : ANALYSE (Liée à la crainte active)
# ==============================================================================
with tab1:
    st.header(f"Analyse : {crainte_active['Nom']}")
    
    st.caption("Définissez les facteurs spécifiques à CETTE peur.")
    
# --- BLOC AJOUTÉ : DÉFINITION DE LA CRAINTE ULTIME ---
    help_crainte = "Il faut identifier la conséquence ultime crainte (ex: 'Je vais faire une crise cardiaque'), et non juste la sensation de peur. Cela doit être testable objectivement."
    with st.expander("ℹ️ Aide : Comment définir sa crainte ?", expanded=False):
        st.info(help_crainte)
    
    # On récupère la définition existante (si elle a déjà été sauvée) ou vide
    current_def = crainte_active.get("Definition", "")
    
    new_def = st.text_area("Quelle est la conséquence ultime qui pourrait arriver ?", value=current_def, help=help_crainte)
    
    if st.button("💾 Sauvegarder la définition"):
        # On sauvegarde DANS l'objet crainte spécifique
        crainte_active["Definition"] = new_def
        st.success("Définition enregistrée pour cette peur.")

    st.divider()

    # Gestion des facteurs pour CETTE crainte uniquement
    st.subheader("Facteurs aggravants & protecteurs")
    
    with st.form("ajout_facteur"):
        c1, c2 = st.columns([3, 1])
        with c1: desc_facteur = st.text_input("Description :")
        with c2: type_facteur = st.selectbox("Type", ["🔴 Risque (Aggravant)", "🟢 Protecteur (Sécurité)"])
        
        is_main_trigger = False
        if "Risque" in type_facteur: is_main_trigger = st.checkbox("Est-ce le déclencheur principal ?")
            
        if st.form_submit_button("Ajouter ce facteur"):
            nouveau = {"Description": desc_facteur, "Type": type_facteur, "Main": is_main_trigger}
            crainte_active["Facteurs"].append(nouveau)
            st.rerun()

    # Affichage
    if crainte_active["Facteurs"]:
        for i, f in enumerate(crainte_active["Facteurs"]):
            col_icon, col_txt, col_del = st.columns([1, 6, 1])
            with col_icon: st.write("🔥" if f.get("Main") else ("🔴" if "Risque" in f["Type"] else "🟢"))
            with col_txt: st.write(f"{'**[PRINCIPAL]** ' if f.get('Main') else ''}{f['Description']}")
            with col_del:
                if st.button("🗑️", key=f"del_fact_{i}"):
                    crainte_active["Facteurs"].pop(i)
                    st.rerun()

    st.divider()
    if st.button("✅ Valider l'étape 1"):
        st.session_state.step1_valide = True
        st.success("Analyse validée !")

# ==============================================================================
# ONGLET 2 : HIÉRARCHIE (Filtrée par crainte)
# ==============================================================================
with tab2:
    st.header(f"Hiérarchie pour : {crainte_active['Nom']}")
    
    with st.form("form_hierarchie"):
        sit = st.text_input("Situation redoutée :")
        cons = st.text_area("Conséquence anticipée précise :", height=60, help="Qu'est-ce qui va se passer exactement ?")
        
        c1, c2 = st.columns(2)
        with c1: attente = st.slider("Probabilité catastrophe (0-100%)", 0, 100, 60, step=5, key="h_attente")
        with c2: anxiete = st.slider("Niveau d'Anxiété (0-100)", 0, 100, 60, step=5, key="h_anxiete")
        
        if st.form_submit_button("Ajouter à la liste"):
            new_row = {
                "Crainte": crainte_active['Nom'], # Lien avec la crainte
                "Situation": sit, 
                "Conséquence Anticipée": cons, 
                "Attente (0-100)": attente, 
                "Anxiété (0-100)": anxiete
            }
            st.session_state.data_hierarchie = pd.concat([st.session_state.data_hierarchie, pd.DataFrame([new_row])], ignore_index=True)
            
            # Cloud (Ajout colonne Crainte)
            from connect_db import save_data
            # CORRECTION ICI : On utilise CURRENT_USER_ID
            save_data("Evitements", [CURRENT_USER_ID, datetime.now().strftime("%Y-%m-%d"), crainte_active['Nom'], sit, attente, cons, f"Anx:{anxiete}"])
            st.success("Ajouté !")

    st.divider()
    
    # FILTRAGE : On n'affiche que ceux de la crainte active
    df_global = st.session_state.data_hierarchie
    df_filtre = df_global[df_global["Crainte"] == crainte_active['Nom']].sort_values(by="Attente (0-100)", ascending=False)

    if not df_filtre.empty:
        st.write("#### 📋 Liste hiérarchisée")
        st.dataframe(df_filtre[["Situation", "Attente (0-100)", "Anxiété (0-100)"]], use_container_width=True)
        
        # SUPPRESSION (Demandé)
        with st.expander("🗑️ Gérer / Supprimer des situations"):
            opts = {f"{row['Situation']} ({row['Attente (0-100)']})": i for i, row in df_filtre.iterrows()}
            sel_del = st.selectbox("Choisir la situation à supprimer", list(opts.keys()))
            if st.button("Supprimer situation"):
                idx_to_drop = opts[sel_del]
                st.session_state.data_hierarchie = st.session_state.data_hierarchie.drop(idx_to_drop).reset_index(drop=True)
                st.rerun()
    else:
        st.info("Aucune situation listée pour cette crainte.")

# ==============================================================================
# ONGLET 3 : PLANIFICATION
# ==============================================================================
with tab3:
    st.header("Planifier")
    
    # On récupère seulement les situations de la crainte active
    df_filtre = st.session_state.data_hierarchie[st.session_state.data_hierarchie["Crainte"] == crainte_active['Nom']]
    
    if df_filtre.empty:
        st.warning("Remplissez la hiérarchie (Onglet 2) pour cette crainte d'abord.")
    else:
        choix_sit = st.selectbox("Situation à affronter :", df_filtre["Situation"].unique())
        
        # Scores initiaux
        row_sit = df_filtre[df_filtre["Situation"] == choix_sit].iloc[0]
        st.caption(f"Score initial : Attente {row_sit['Attente (0-100)']}%")
        
        c1, c2 = st.columns(2)
        with c1: date_prevue = st.date_input("Date", datetime.now())
        with c2: heure_prevue = st.time_input("Heure", datetime.now().time())
            
        with st.container(border=True):
            st.write("**Configuration (Modulateurs)**")
            # Facteurs liés à la crainte active
            aggravants = [f['Description'] for f in crainte_active["Facteurs"] if "Risque" in f['Type']]
            protecteurs = [f['Description'] for f in crainte_active["Facteurs"] if "Protecteur" in f['Type']]
            
            c_a, c_b = st.columns(2)
            with c_a: sel_agg = st.multiselect("➕ Je combine (Aggravants)", aggravants)
            with c_b: sel_prot = st.multiselect("❌ Je jette (Protecteurs)", protecteurs)
        
        st.write("---")
        st.markdown("#### Ré-évaluation dans ces conditions")
        c3, c4 = st.columns(2)
        with c3: new_att = st.slider("Probabilité catastrophe (0-100%)", 0, 100, int(row_sit['Attente (0-100)']), step=5, key="new_att")
        with c4: new_anx = st.slider("Niveau Anxiété (0-100)", 0, 100, int(row_sit['Anxiété (0-100)']), step=5, key="new_anx")

        if st.button("📅 Valider"):
            heure_propre = str(heure_prevue)[:5] 
            resume = f"Aggravants: {', '.join(sel_agg)} | Sans: {', '.join(sel_prot)}"
            
            new_plan = {
                "Crainte": crainte_active['Nom'], # Lien
                "Date": str(date_prevue), "Heure": heure_propre, "Situation": choix_sit,
                "Attente Pré-Expo": new_att, "Anxiété Pré-Expo": new_anx
            }
            st.session_state.data_planning_expo = pd.concat([st.session_state.data_planning_expo, pd.DataFrame([new_plan])], ignore_index=True)
            
            from connect_db import save_data
            # CORRECTION ICI : On utilise CURRENT_USER_ID
            # Ordre Cloud : Patient, Date, CRAINTE, Situation, Type, Details, Score1, Score2, Vide, Vide
            save_data("Expositions", [
                CURRENT_USER_ID, str(date_prevue), crainte_active['Nom'], choix_sit, 
                "PLANIFIÉ", resume, new_att, new_anx, "", ""
            ])
            st.success("Planifié !")

    # Affichage Planning Filtré + Suppression
    df_plan_filtre = st.session_state.data_planning_expo[st.session_state.data_planning_expo["Crainte"] == crainte_active['Nom']]
    
    if not df_plan_filtre.empty:
        st.write("---")
        st.write("#### 🗓️ Exercices prévus (Cette crainte)")
        st.dataframe(df_plan_filtre[["Date", "Heure", "Situation"]], use_container_width=True)
        
        # SUPPRESSION PLAN
        with st.expander("🗑️ Gérer / Supprimer un exercice planifié"):
            opts_plan = {f"{r['Date']} - {r['Situation']}": i for i, r in df_plan_filtre.iterrows()}
            sel_del_plan = st.selectbox("Choisir", list(opts_plan.keys()))
            if st.button("Supprimer exercice"):
                st.session_state.data_planning_expo = st.session_state.data_planning_expo.drop(opts_plan[sel_del_plan]).reset_index(drop=True)
                st.rerun()

# ==============================================================================
# ONGLET 4 : CONSOLIDATION
# ==============================================================================
with tab4:
    st.header("Consolidation (Bilan)")
    
    # On filtre les exos planifiés pour cette crainte
    df_plan_filtre = st.session_state.data_planning_expo[st.session_state.data_planning_expo["Crainte"] == crainte_active['Nom']]
    
    if df_plan_filtre.empty:
        st.warning("Aucun exercice planifié pour cette crainte.")
    else:
        liste_prevus = [f"{row['Date']} {row['Heure']} : {row['Situation']}" for i, row in df_plan_filtre.iterrows()]
        choix_exo_str = st.selectbox("Quel exercice avez-vous fait ?", liste_prevus)
        
        # Retrouver les infos
        idx_global = df_plan_filtre[df_plan_filtre.apply(lambda r: f"{r['Date']} {r['Heure']} : {r['Situation']}" == choix_exo_str, axis=1)].index[0]
        donnees_planif = st.session_state.data_planning_expo.iloc[idx_global]
        
        st.divider()
        with st.form("form_consolidation"):
            st.subheader("1. Juste avant / Pendant")
            c1, c2 = st.columns(2)
            with c1: pre_att = st.slider("Probabilité catastrophe (0-100%)", 0, 100, 80, step=5, key="c_att_pre")
            with c2: pre_anx = st.slider("Niveau Anxiété (0-100)", 0, 100, 80, step=5, key="c_anx_pre")
            
            st.subheader("2. Après")
            duree = st.number_input("Durée (min)", 0, 240, 20)
            st.markdown("**Analyse :**")
            q1 = st.text_area("Comment je sais que la catastrophe n'a pas eu lieu ?", height=70)
            q2 = st.text_area("Mes attentes initiales ?", height=70)
            q3 = st.text_area("La réalité ? (Surprise)", height=70)
            q4 = st.text_area("Ce que j'ai appris ?", height=70)
            
            st.subheader("3. Futur")
            c3, c4 = st.columns(2)
            with c3: post_att = st.slider("Si je recommence, probabilité catastrophe ?", 0, 100, 40, step=5, key="c_att_post")
            with c4: post_anx = st.slider("Si je recommence, niveau anxiété ?", 0, 100, 40, step=5, key="c_anx_post")
            
            if st.form_submit_button("Enregistrer Bilan"):
                new_log = {
                    "Crainte": crainte_active['Nom'],
                    "Date": datetime.now().strftime("%Y-%m-%d"),
                    "Situation": donnees_planif['Situation'],
                    "Planif-Attente": donnees_planif['Attente Pré-Expo'],
                    "Avant-Attente": pre_att,
                    "Après-Attente": post_att,
                    "Apprentissage": q4
                }
                st.session_state.data_logs_expo = pd.concat([st.session_state.data_logs_expo, pd.DataFrame([new_log])], ignore_index=True)
                
                from connect_db import save_data
                # CORRECTION ICI : On utilise CURRENT_USER_ID
                # Sauvegarde avec colonne Crainte
                save_data("Expositions", [
                    CURRENT_USER_ID, datetime.now().strftime("%Y-%m-%d"), 
                    crainte_active['Nom'], # Crainte
                    donnees_planif['Situation'], 
                    "BILAN", f"{duree} min", pre_att, post_att, pre_anx, 
                    f"Preuves:{q1}|Attentes:{q2}|Réel:{q3}|Leçon:{q4}"
                ])
                st.success("Enregistré !")

    # Historique FILTRÉ
    df_logs_filtre = st.session_state.data_logs_expo[st.session_state.data_logs_expo["Crainte"] == crainte_active['Nom']]
    
    if not df_logs_filtre.empty:
        st.divider()
        st.write(f"#### 🧠 Évolution Croyances ({crainte_active['Nom']})")
        for i, row in df_logs_filtre.iterrows():
            with st.expander(f"{row['Date']} - {row['Situation']}"):
                k1, k2, k3 = st.columns(3)
                with k1: st.metric("Planification", f"{row['Planif-Attente']}%")
                with k2: st.metric("Avant", f"{row['Avant-Attente']}%")
                with k3: st.metric("Après", f"{row['Après-Attente']}%", delta=f"{int(row['Après-Attente']) - int(row['Avant-Attente'])}%")
                st.info(row['Apprentissage'])

st.divider()
st.set_page_config(page_title="Exposition", page_icon="📉")
if st.button("⬅️ Retour au tableau de bord"):
    # On dit au menu principal de rouvrir l'onglet "Échelles"
    st.session_state["target_tab"] = "🛠️ Outils & Exos"
    st.switch_page("streamlit_app.py")