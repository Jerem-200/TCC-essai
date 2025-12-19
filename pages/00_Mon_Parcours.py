import streamlit as st
import os
import time
import pandas as pd  
import altair as alt 
import json
from protocole_config import PROTOCOLE_BARLOW, QUESTIONS_HEBDO 
from connect_db import load_data, sauvegarder_reponse_hebdo

# --- FONCTION POUR CHARGER L'HISTORIQUE (NOUVEAU) ---
def charger_donnees_graphique(patient_id):
    """Récupère et nettoie l'historique pour les graphiques."""
    try:
        raw_data = load_data("Reponses_Hebdo")
        if raw_data:
            df = pd.DataFrame(raw_data)
            # On filtre pour le patient actuel
            df = df[df["Patient"] == patient_id].copy()
            
            if not df.empty:
                # 1. Nettoyage des dates
                df["Date"] = pd.to_datetime(df["Date"])
                
                # 2. Nettoyage des scores (forcer en numérique)
                df["Score_Global"] = pd.to_numeric(df["Score_Global"], errors='coerce')
                
                # 3. Nettoyage des noms (ex: "module1 - Anxiété" -> "Anxiété")
                # On enlève le préfixe du module pour pouvoir suivre l'évolution globale
                def nettoyer_nom(x):
                    if " - " in str(x):
                        return str(x).split(" - ")[1].split(" (")[0] # Garde "Anxiété"
                    return str(x)
                
                df["Type"] = df["Questionnaire"].apply(nettoyer_nom)
                return df
    except Exception as e:
        print(f"Erreur graph: {e}")
    return pd.DataFrame()

# Import sécurisé
try:
    from streamlit_app import charger_progression, charger_etat_devoirs
except ImportError:
    # Fallback si l'import direct échoue (copie de sécurité)
    def charger_progression(uid): 
        try:
            from connect_db import load_data
            import pandas as pd
            data = load_data("Progression")
            if data:
                df = pd.DataFrame(data)
                row = df[df["Patient"] == uid]
                if not row.empty:
                    return [x.strip() for x in str(row.iloc[0]["Modules_Actifs"]).split(",") if x.strip()]
        except: pass
        return ["module0"]
        
    def charger_etat_devoirs(uid): return {}

st.set_page_config(page_title="Mon Parcours", page_icon="🗺️")

# Masquer la navigation latérale par défaut
st.markdown("""
    <style>
        [data-testid="stSidebarNav"] {display: none;}
    </style>
""", unsafe_allow_html=True)

# Sidebar de navigation
with st.sidebar:
    st.page_link("streamlit_app.py", label="🏠 Retour Accueil")
    st.divider()

if "authentifie" not in st.session_state or not st.session_state.authentifie:
    st.warning("🔒 Veuillez vous connecter.")
    st.stop()

# --- FORCER LE CHARGEMENT DES DONNÉES FRAÎCHES ---
current_user = st.session_state.get("user_id", "")
modules_debloques = charger_progression(current_user)
devoirs_exclus = charger_etat_devoirs(current_user)

st.title("🗺️ Mon Parcours de Soin")

# --- BOUCLE MODULES ---
for code_mod, data in PROTOCOLE_BARLOW.items():
    
    # Vérification stricte si le module est dans la liste chargée
    if code_mod in modules_debloques:
        
        # Par défaut, on ferme tout
        with st.expander(f"✅ {data['titre']}", expanded=False):
            
            tab_proc, tab_docs, tab_exos, tab_suivi = st.tabs(["📖 Ma Séance", "📂 Documents", "📝 Mes Exercices", "📈 Suivi"])
            
            # --- ONGLET 1 : DÉROULÉ INFORMATIF (MODIFIÉ) ---
            with tab_proc:
                # 1. Rappel des objectifs
                st.info(f"**Objectifs du module :** {data['objectifs']}")
                
                # 2. Rappel des étapes de la séance (Lecture seule)
                st.markdown("### 📝 Ce que nous avons vu")
                if data['etapes_seance']:
                    for etape in data['etapes_seance']:
                        # Affiche le titre de l'étape
                        st.markdown(f"- **{etape['titre']}**")
                        # Affiche le détail en petit (italique) si disponible
                        details = etape.get('details')
                        if details:
                            st.caption(f"&nbsp;&nbsp;&nbsp;_{details}_")
                else:
                    st.write("Pas d'étape spécifique listée.")

                st.divider()

                # 3. Rappel des devoirs (Lecture seule + Téléchargement)
                st.markdown("### 🏠 Travail à la maison")
                
                exclus_ici = devoirs_exclus.get(code_mod, [])
                a_faire = False
                
                if data['taches_domicile']:
                    for j, dev in enumerate(data['taches_domicile']):
                        # On affiche seulement si le thérapeute ne l'a pas décoché (exclu)
                        if j not in exclus_ici:
                            a_faire = True
                            # Affichage simple sans case à cocher
                            st.markdown(f"👉 **{dev['titre']}**")
                            
                            # Bouton de téléchargement si PDF
                            if dev.get('pdf') and os.path.exists(dev['pdf']):
                                with open(dev['pdf'], "rb") as f:
                                    st.download_button(
                                        f"📥 Télécharger le support", 
                                        f, 
                                        file_name=os.path.basename(dev['pdf']), 
                                        key=f"dl_dev_{code_mod}_{j}"
                                    )
                
                if not a_faire:
                    st.success("🎉 Aucun devoir spécifique pour la prochaine fois.")
                else:
                    # On garde la caméra car c'est utile pour envoyer le travail, 
                    # mais ce n'est pas une "case à cocher" de validation.
                    st.write("")
                    with st.expander("📸 Envoyer une photo de mon travail au thérapeute"):
                        st.camera_input("Prendre une photo", key=f"cam_{code_mod}")

            # --- ONGLET 2 : TOUS LES DOCS (INCHANGÉ) ---
            with tab_docs:
                st.write("Tous les fichiers du module :")
                if 'pdfs_module' in data and data['pdfs_module']:
                    for path in data['pdfs_module']:
                        name = os.path.basename(path)
                        if os.path.exists(path):
                            with open(path, "rb") as f:
                                st.download_button(f"📥 {name}", f, file_name=name, key=f"dl_pat_all_{code_mod}_{name}")
                else:
                    st.info("Aucun document.")

            # --- ONGLET 3 : MES EXERCICES (INCHANGÉ) ---
            with tab_exos:
                st.markdown("##### 📝 Remplir un bilan ou un exercice")
                st.caption("Sélectionnez le questionnaire ci-dessous pour le remplir numériquement.")

                choix_q = st.selectbox("Choisir l'exercice :", list(QUESTIONS_HEBDO.keys()), key=f"sel_q_{code_mod}")
                
                if choix_q:
                    config_q = QUESTIONS_HEBDO[choix_q]
                    
                    # Formulaire unique
                    with st.form(key=f"form_exo_{code_mod}_{choix_q}"):
                        st.markdown(f"**{config_q['titre']}**")
                        st.caption(config_q['description'])
                        
                        reponses = {}
                        score_total = 0
                        nom_emotion = ""

                        # --- CAS SPÉCIAL : Demander le nom de l'émotion ---
                        if config_q.get("ask_emotion"):
                            nom_emotion = st.text_input("Quelle est l'émotion concernée (ex: Colère, Honte) ?", key=f"emo_name_{code_mod}_{choix_q}")
                            if nom_emotion:
                                reponses["Émotion identifiée"] = nom_emotion
                        
                        # --- TYPE 1 : Échelles numériques simples ---
                        if config_q['type'] == "scale_0_8":
                            for q in config_q['questions']:
                                st.write(q)
                                val = st.slider("Intensité", 0, 8, 0, key=f"sld_{code_mod}_{choix_q}_{q}")
                                reponses[q] = val
                                score_total += val
                        
                        # --- TYPE 2 : Texte libre ---
                        elif config_q['type'] == "text":
                            for q in config_q['questions']:
                                val = st.text_area(q, height=100, key=f"txt_{code_mod}_{choix_q}_{q}")
                                reponses[q] = val
                            score_total = -1

                        # --- TYPE 3 : QCM OASIS/ODSIS ---
                        elif config_q['type'] == "qcm_oasis":
                            for item in config_q['questions']:
                                # Si on a un nom d'émotion, on l'injecte dans la question pour la rendre plus personnelle
                                label_dyn = item['label']
                                
                                st.markdown(f"**{label_dyn}**")
                                choix = st.radio(
                                    "Votre réponse :", 
                                    item['options'], 
                                    key=f"rad_{code_mod}_{choix_q}_{item['id']}",
                                    label_visibility="collapsed"
                                )
                                try:
                                    valeur = int(choix.split("=")[0].strip())
                                except:
                                    valeur = 0
                                
                                reponses[item['label']] = choix
                                score_total += valeur

                        st.write("")
                        
                        if st.form_submit_button("Envoyer", type="primary"):
                            # Si c'est l'échelle émotion, on vérifie que le nom est rempli
                            if config_q.get("ask_emotion") and not nom_emotion:
                                st.error("Veuillez indiquer le nom de l'émotion avant d'envoyer.")
                            else:
                                nom_final = f"{code_mod} - {choix_q}"
                                if nom_emotion:
                                    nom_final += f" ({nom_emotion})"
                                    
                                if sauvegarder_reponse_hebdo(current_user, nom_final, str(score_total), reponses):
                                    st.success("✅ Enregistré avec succès !")
                                    time.sleep(1)
                                    st.rerun()

            # --- ONGLET 4 : SUIVI (NOUVEAU) ---
            with tab_suivi:
                st.markdown("##### 📈 Mes Progrès")
                
                # 1. Chargement des données
                df_history = charger_donnees_graphique(current_user)
                
                if not df_history.empty:
                    # 2. Sélecteur pour filtrer quel graphique voir
                    types_dispos = df_history["Type"].unique().tolist()
                    type_voir = st.multiselect("Afficher les courbes de :", types_dispos, default=types_dispos[:2], key=f"multi_{code_mod}")
                    
                    if type_voir:
                        # 3. Création du graphique Altair
                        # On filtre les données
                        df_chart = df_history[df_history["Type"].isin(type_voir)]
                        
                        # Graphique de ligne
                        chart = alt.Chart(df_chart).mark_line(point=True).encode(
                            x=alt.X('Date', title='Date'),
                            y=alt.Y('Score_Global', title='Score'),
                            color=alt.Color('Type', title='Échelle'),
                            tooltip=['Date', 'Type', 'Score_Global']
                        ).properties(height=300)
                        
                        st.altair_chart(chart, use_container_width=True)
                        
                        # Petit tableau récapitulatif en dessous
                        with st.expander("Voir l'historique détaillé"):
                            st.dataframe(
                                df_chart[["Date", "Type", "Score_Global"]].sort_values("Date", ascending=False),
                                use_container_width=True,
                                hide_index=True
                            )
                    else:
                        st.info("Sélectionnez une échelle ci-dessus pour voir la courbe.")
                else:
                    st.info("Pas encore assez de données pour afficher un graphique.")
                    st.caption("Remplissez vos premiers questionnaires dans l'onglet 'Mes Exercices' !")

    else:
        with st.container(border=True):
            st.write(f"🔒 **{data['titre']}**")
            st.caption("Verrouillé par votre thérapeute.")