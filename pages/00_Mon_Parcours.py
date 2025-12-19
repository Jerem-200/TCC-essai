import streamlit as st
import os
import time
import pandas as pd
import altair as alt
import json
from datetime import datetime

from protocole_config import PROTOCOLE_BARLOW, QUESTIONS_HEBDO 
from connect_db import load_data, sauvegarder_reponse_hebdo, supprimer_reponse

# --- CONFIGURATION ---
st.set_page_config(page_title="Mon Espace Santé", page_icon="🧘", layout="wide")

st.markdown("""
    <style>
        [data-testid="stSidebarNav"] {display: none;}
        .stExpander {border: 1px solid #ddd; border-radius: 5px;}
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.page_link("streamlit_app.py", label="🏠 Accueil")
    st.divider()

# --- SÉCURITÉ ---
if "authentifie" not in st.session_state or not st.session_state.authentifie:
    st.warning("🔒 Connexion requise.")
    st.stop()

current_user = st.session_state.user_id

# --- FONCTIONS UTILITAIRES (CACHE) ---
def charger_historique_complet(uid):
    """Charge tout l'historique et prépare la colonne 'Type' pour les graphiques"""
    try:
        raw = load_data("Reponses_Hebdo")
        if raw:
            df = pd.DataFrame(raw)
            df = df[df["Patient"] == uid].copy()
            if not df.empty:
                df["Date"] = pd.to_datetime(df["Date"])
                
                # --- CORRECTION ICI : ON CRÉE LA COLONNE 'Type' ---
                # On force le score en numérique
                df["Score_Global"] = pd.to_numeric(df["Score_Global"], errors='coerce')

                def nettoyer_nom(x):
                    s = str(x)
                    # Si c'est lié à un module "module1 - Anxiété", on garde "Anxiété"
                    if " - " in s: 
                        s = s.split(" - ")[1]
                    # On retire les parenthèses de détails "Anxiété (Colère)" -> "Anxiété"
                    return s.split(" (")[0]
                
                df["Type"] = df["Questionnaire"].apply(nettoyer_nom)
                # --------------------------------------------------
                
                return df
    except Exception as e:
        print(f"Erreur chargement histo: {e}")
    return pd.DataFrame()

# Import helpers progression
try:
    from streamlit_app import charger_progression, charger_etat_devoirs
except ImportError:
    def charger_progression(uid): return ["module0"] 
    def charger_etat_devoirs(uid): return {}

# --- CHARGEMENT DONNÉES ---
modules_debloques = charger_progression(current_user)
devoirs_exclus = charger_etat_devoirs(current_user)
df_history = charger_historique_complet(current_user)

st.title(f"Espace Patient - {current_user}")

# =========================================================
# LA GRANDE NAVIGATION
# =========================================================
tab_parcours, tab_outils, tab_sante = st.tabs([
    "🗺️ Ma Progression",
    "🛠️ Mes Outils & Exercices", 
    "📊 Mon Suivi de Santé" 
])

# =========================================================
# 1. MA PROGRESSION
# =========================================================
with tab_parcours:
    st.markdown("### 📍 Mon cheminement")
    
    for code_mod, data in PROTOCOLE_BARLOW.items():
        if code_mod in modules_debloques:
            with st.expander(f"✅ {data['titre']}", expanded=False):
                t_seance, t_doc = st.tabs(["📖 Résumé Séance", "📂 Documents"])
                
                with t_seance:
                    st.info(f"**Objectifs :** {data['objectifs']}")
                    col_step, col_home = st.columns(2)
                    
                    with col_step:
                        st.markdown("#### 📝 Ce que nous avons vu")
                        if data['etapes_seance']:
                            for etape in data['etapes_seance']:
                                st.markdown(f"- **{etape['titre']}**")
                                if etape.get('details'): st.caption(f"_{etape.get('details')}_")
                        else: st.caption("Pas d'étapes listées.")
                    
                    with col_home:
                        st.markdown("#### 🏠 Travail à la maison")
                        exclus = devoirs_exclus.get(code_mod, [])
                        a_faire = False
                        if data['taches_domicile']:
                            for j, dev in enumerate(data['taches_domicile']):
                                if j not in exclus:
                                    a_faire = True
                                    st.markdown(f"👉 **{dev['titre']}**")
                                    if dev.get('pdf') and os.path.exists(dev['pdf']):
                                        with open(dev['pdf'], "rb") as f:
                                            st.download_button("📥 Support", f, file_name=os.path.basename(dev['pdf']), key=f"d_home_{code_mod}_{j}")
                        if not a_faire: st.success("🎉 Rien de spécial.")
                        else:
                            st.write("")
                            with st.expander("📸 Envoyer une photo"):
                                st.camera_input("Photo", key=f"cam_{code_mod}")

                with t_doc:
                    st.write("Tous les fichiers du module :")
                    if data.get('pdfs_module'):
                        for p in data['pdfs_module']:
                            if os.path.exists(p):
                                with open(p, "rb") as f:
                                    st.download_button(f"📥 {os.path.basename(p)}", f, file_name=os.path.basename(p), key=f"da_{code_mod}_{os.path.basename(p)}")
                    else: st.caption("Aucun document.")
        else:
            with st.container():
                st.markdown(f"🔒 **{data['titre']}** _(Verrouillé)_")
                st.divider()


# =========================================================
# 2. MES OUTILS
# =========================================================
with tab_outils:
    
    # Recherche des exercices disponibles
    liste_exos_dispos = []
    
    for m in modules_debloques:
        if m in PROTOCOLE_BARLOW and "exercices" in PROTOCOLE_BARLOW[m]:
            for exo in PROTOCOLE_BARLOW[m]["exercices"]:
                liste_exos_dispos.append({
                    "mod_code": m,
                    "mod_titre": PROTOCOLE_BARLOW[m]["titre"],
                    "exo_data": exo
                })
    
    col_menu, col_work = st.columns([1, 2])
    
    with col_menu:
        st.subheader("Choix de l'outil")
        
        if not liste_exos_dispos:
            st.warning("⚠️ Aucun exercice trouvé.")
            st.info("💡 Astuce : Les exercices apparaissent ici une fois que votre thérapeute a débloqué le module correspondant.")
            exo_choisi = None
        else:
            options_map = {f"{x['mod_code']} - {x['exo_data']['titre']}": x for x in liste_exos_dispos}
            choix_cle = st.radio("Exercices disponibles :", list(options_map.keys()))
            exo_choisi = options_map[choix_cle]

    with col_work:
        if exo_choisi:
            exo_data = exo_choisi["exo_data"]
            st.markdown(f"### {exo_data['titre']}")
            st.info(exo_data['description'])
            
            # --- FICHE OBJECTIFS (Refaite selon votre demande) ---
            if exo_data["type"] == "fiche_objectifs_traitement":
                
                # 1. Initialisation des variables temporaires en session
                if "temp_main_pb" not in st.session_state:
                    st.session_state.temp_main_pb = ""
                if "temp_objectives_list" not in st.session_state:
                    st.session_state.temp_objectives_list = []
                
                # 2. Le Problème Principal (Persistant)
                st.markdown("#### 1️⃣ Le Problème Principal")
                st.caption("Décrivez ici la difficulté majeure (émotionnelle ou situationnelle) que vous souhaitez traiter.")
                
                # On utilise on_change pour sauvegarder le texte sans recharger toute la page visuellement trop fort
                def update_pb():
                    st.session_state.temp_main_pb = st.session_state.widget_main_pb
                
                st.text_area(
                    "Votre problème principal :", 
                    value=st.session_state.temp_main_pb, 
                    height=80, 
                    key="widget_main_pb",
                    on_change=update_pb
                )

                st.divider()

                # 3. Ajout des Objectifs (Dans un FORMULAIRE pour éviter le rechargement à chaque lettre)
                st.markdown("#### 2️⃣ Ajouter des Objectifs liés")
                st.caption("Pour ce problème, quels sont vos objectifs concrets ?")

                with st.form("form_add_obj", clear_on_submit=True):
                    c_obj, c_step = st.columns(2)
                    with c_obj:
                        new_obj_txt = st.text_input("Nouvel Objectif :", placeholder="Ex: Aller au cinéma")
                    with c_step:
                        new_steps_txt = st.text_area("Étapes (une par ligne) :", height=100, placeholder="1. Choisir le film\n2. Acheter le billet...")
                    
                    submitted = st.form_submit_button("➕ Ajouter cet objectif")
                    
                    if submitted:
                        if new_obj_txt:
                            st.session_state.temp_objectives_list.append({
                                "objectif": new_obj_txt,
                                "etapes": [s.strip() for s in new_steps_txt.split('\n') if s.strip()]
                            })
                            st.rerun() # Rechargement unique ici pour afficher le nouvel élément
                        else:
                            st.error("L'objectif ne peut pas être vide.")

                # 4. Affichage de la liste construite
                if st.session_state.temp_objectives_list:
                    st.markdown("##### 📋 Liste des objectifs à enregistrer :")
                    for i, item in enumerate(st.session_state.temp_objectives_list):
                        with st.expander(f"🎯 Objectif {i+1} : {item['objectif']}", expanded=False):
                            st.write("**Étapes :**")
                            for s in item['etapes']:
                                st.markdown(f"- {s}")
                            
                            # Bouton suppression
                            if st.button("Supprimer", key=f"del_lst_{i}"):
                                st.session_state.temp_objectives_list.pop(i)
                                st.rerun()
                    
                    st.divider()
                    
                    # 5. SAUVEGARDE FINALE (CLOUD)
                    # C'est ici que ça part dans Google Sheets
                    if st.button("💾 Sauvegarder définitivement cet exercice", type="primary"):
                        if not st.session_state.temp_main_pb:
                            st.error("Veuillez définir le problème principal avant de sauvegarder.")
                        else:
                            # Structure des données envoyées au Cloud
                            payload = {
                                "type_exercice": "Objectifs Traitement",
                                "probleme_principal": st.session_state.temp_main_pb,
                                "liste_objectifs": st.session_state.temp_objectives_list
                            }
                            
                            nom_save = f"Exercice - {exo_data['titre']}"
                            
                            if sauvegarder_reponse_hebdo(current_user, nom_save, "N/A", payload):
                                st.success("✅ Exercice sauvegardé dans le cloud !")
                                # On vide la mémoire
                                st.session_state.temp_main_pb = ""
                                st.session_state.temp_objectives_list = []
                                time.sleep(1)
                                st.rerun()
                else:
                    st.info("Aucun objectif ajouté pour l'instant.")

    # --- HISTORIQUE EXERCICES (LECTURE DU CLOUD) ---
    st.divider()
    with st.expander("📜 Historique de mes exercices réalisés", expanded=False):
        if not df_history.empty and "Questionnaire" in df_history.columns:
            df_exos = df_history[df_history["Questionnaire"].str.contains("Exercice", na=False)].copy()
            if not df_exos.empty:
                for idx, row in df_exos.iterrows():
                    c_d, c_n, c_a = st.columns([1, 3, 1])
                    with c_d: st.write(row["Date"].strftime("%d/%m"))
                    with c_n: st.write(f"**{row['Questionnaire']}**")
                    with c_a:
                        if st.button("Supprimer", key=f"del_h_{idx}"):
                            supprimer_reponse(current_user, row["Date"], row["Questionnaire"])
                            st.rerun()
                    with st.expander("Voir le détail"):
                        try:
                            d = json.loads(row["Details_Json"])
                            
                            # Affichage spécifique pour ce nouveau format
                            if "probleme_principal" in d:
                                st.info(f"**Problème :** {d['probleme_principal']}")
                                if "liste_objectifs" in d:
                                    for it in d["liste_objectifs"]:
                                        st.markdown(f"**🎯 {it['objectif']}**")
                                        for s in it.get('etapes', []): st.write(f"- {s}")
                                        st.write("---")
                            # Ancien format (rétro-compatibilité)
                            elif "contenu" in d:
                                for it in d["contenu"]:
                                    st.markdown(f"**🎯 {it['objectif']}**")
                                    st.caption(f"Pb: {it.get('probleme', '')}")
                                    for s in it.get('etapes', []): st.write(f"- {s}")
                            else: st.json(d)
                        except: st.write("Erreur lecture.")
            else: st.info("Aucun exercice sauvegardé.")
        else: st.info("Historique vide.")


# =========================================================
# 3. MON SUIVI DE SANTÉ
# =========================================================
with tab_sante:
    c1, c2 = st.columns([1, 2])
    
    with c1:
        st.subheader("📝 Bilan Hebdo")
        st.info("Sélectionnez une échelle à remplir :")
        choix_q = st.radio("Questionnaire :", list(QUESTIONS_HEBDO.keys()), label_visibility="collapsed")
    
    with c2:
        if choix_q:
            config = QUESTIONS_HEBDO[choix_q]
            with st.container(border=True):
                st.markdown(f"**{config['titre']}**")
                st.caption(config['description'])
                
                with st.form(f"form_sante_{choix_q}"):
                    reponses = {}
                    score = 0
                    
                    if config.get("ask_emotion"):
                        emo = st.text_input("Emotion (ex: Colère) :")
                        if emo: reponses["Emotion"] = emo
                    
                    if config['type'] == "scale_0_8":
                        for q in config['questions']:
                            val = st.slider(q, 0, 8, 0)
                            reponses[q] = val
                            score += val
                    elif config['type'] == "qcm_oasis":
                        for item in config['questions']:
                            lbl = item['label']
                            res = st.radio(lbl, item['options'])
                            try: score += int(res.split("=")[0])
                            except: pass
                            reponses[lbl] = res
                    
                    if st.form_submit_button("Enregistrer", type="primary"):
                        nom_final = choix_q
                        if config.get("ask_emotion") and "Emotion" in reponses:
                            nom_final += f" ({reponses['Emotion']})"
                            
                        if sauvegarder_reponse_hebdo(current_user, nom_final, str(score), reponses):
                            st.success("Sauvegardé !")
                            time.sleep(1)
                            st.rerun()
    
    st.divider()
    st.subheader("📈 Mes Courbes")
    
    if not df_history.empty and "Type" in df_history.columns:
        # On exclut les exercices de l'affichage graphique
        types_graph = [t for t in df_history["Type"].unique() if "Exercice" not in str(t)]
        
        if types_graph:
            sel_graph = st.multiselect("Afficher :", types_graph, default=types_graph[:2])
            
            if sel_graph:
                sub_df = df_history[df_history["Type"].isin(sel_graph)]
                chart = alt.Chart(sub_df).mark_line(point=True).encode(
                    x=alt.X('Date', axis=alt.Axis(format='%d/%m')), 
                    y='Score_Global', 
                    color='Type', 
                    tooltip=['Date', 'Score_Global']
                ).interactive()
                st.altair_chart(chart, use_container_width=True)
            else:
                st.info("Sélectionnez une courbe ci-dessus.")
        else:
            st.info("Aucune donnée chiffrée (questionnaires) disponible.")
    else:
        st.info("Historique vide. Remplissez un questionnaire pour voir vos progrès !")