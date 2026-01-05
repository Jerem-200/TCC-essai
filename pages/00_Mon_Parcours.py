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

# ==============================================================================
# 🚀 ZONE D'OPTIMISATION (CACHE)
# ==============================================================================

# 1. On met en cache l'historique pour ne pas le recharger à chaque clic
@st.cache_data(ttl=300) # Garde en mémoire 5 minutes
def charger_historique_complet_cache(uid):
    """Charge tout l'historique (Version optimisée)"""
    try:
        raw = load_data("Reponses_Hebdo")
        if raw:
            df = pd.DataFrame(raw)
            df = df[df["Patient"] == uid].copy()
            if not df.empty:
                df["Date"] = pd.to_datetime(df["Date"])
                df["Score_Global"] = pd.to_numeric(df["Score_Global"], errors='coerce')

                def nettoyer_nom(x):
                    s = str(x)
                    if " - " in s: s = s.split(" - ")[1]
                    return s.split(" (")[0]
                
                df["Type"] = df["Questionnaire"].apply(nettoyer_nom)
                return df
    except Exception as e:
        print(f"Erreur chargement histo: {e}")
    return pd.DataFrame()

# 2. On "enveloppe" les fonctions externes dans un cache local
# Cela empêche de re-télécharger la progression quand on change d'outil
#@st.cache_data(ttl=300)
def charger_donnees_utilisateur_cache(uid):
    try:
        from streamlit_app import charger_progression, charger_etat_devoirs
        prog = charger_progression(uid)
        dev = charger_etat_devoirs(uid)
        return prog, dev
    except ImportError:
        return ["module0"], {}

# --- CHARGEMENT DES DONNÉES (RAPIDE GRÂCE AU CACHE) ---
modules_debloques, devoirs_exclus = charger_donnees_utilisateur_cache(current_user)
df_history = charger_historique_complet_cache(current_user)

st.title(f"Espace Patient - {current_user}")

# =========================================================
# LA GRANDE NAVIGATION (Refaite proprement)
# =========================================================

# 1. On définit l'ordre fixe des onglets
titres_onglets = [
    "🗺️ Ma Progression", 
    "🛠️ Mes Outils", 
    "📝 Bilan Hebdo", 
    "📜 Mon Historique"
]

# 2. On calcule quel onglet doit être actif par défaut
index_par_defaut = 0 # Par défaut : Progression (le premier)

if st.session_state.get("retour_outils", False):
    index_par_defaut = 1 # Si on revient d'un exo : Outils (le deuxième)
    st.session_state["retour_outils"] = False # On reset le "drapeau"

# 3. On crée la barre de navigation (Radio horizontal)
choix_onglet = st.radio(
    "Navigation",
    options=titres_onglets,
    index=index_par_defaut,
    horizontal=True,             # C'est ça qui donne l'aspect "Barre"
    label_visibility="collapsed" # On cache le titre "Navigation"
)

st.divider() # Une petite ligne pour séparer le menu du contenu

# =========================================================
# 1. MA PROGRESSION
# =========================================================
if choix_onglet == titres_onglets[0]:
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
# 2. MES OUTILS (LE LANCEUR RAPIDE)
# =========================================================
if choix_onglet == titres_onglets[1]:
    
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

    liste_exos_dispos.sort(key=lambda x: x['mod_code'])
    
    st.subheader("🚀 Lanceur d'outils")
    st.caption("Cliquez sur un outil pour l'ouvrir immédiatement.")

    if not liste_exos_dispos:
        st.warning("⚠️ Aucun exercice trouvé.")
        st.info("Les exercices apparaîtront ici quand vous débloquerez les modules.")
    else:
        # On affiche une liste de boutons. 
        # Un clic = Une action immédiate.
        for item in liste_exos_dispos:
            exo_data = item["exo_data"]
            titre_complet = f"{item['mod_code']} - {exo_data['titre']}"
            
            # Astuce : on met la description dans l'infobulle (help) pour garder l'info dispo
            if st.button(f"👉 {titre_complet}", key=f"btn_launch_{exo_data['id']}", help=exo_data['description'], use_container_width=True):
                # 1. On sauvegarde le contexte
                st.session_state["exercice_actif"] = item
                # 2. On change de page immédiatement
                st.switch_page("pages/21_Barlow_Exercice.py")

# =========================================================
# 3. MON SUIVI DE SANTÉ
# =========================================================
if choix_onglet == titres_onglets[2]:
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
                            # Pour le bilan, on recharge juste la page actuelle, c'est assez rapide
                            st.success("Sauvegardé !")
                            charger_historique_complet_cache.clear() # On force la mise à jour de l'historique
                            time.sleep(1)
                            st.rerun()
    
# =========================================================
# 4. MON HISTORIQUE
# =========================================================
if choix_onglet == titres_onglets[3]:
    st.subheader("📜 Historique Complet")
    
    if not df_history.empty:
        
        # --- A. GRAPHIQUES (Scores) ---
        st.markdown("#### 📈 Évolution des Scores (Questionnaires)")
        df_charts = df_history[~df_history["Questionnaire"].str.contains("Exercice", na=False)]
        
        if not df_charts.empty:
            types_dispos = df_charts["Type"].unique().tolist()
            choix_types = st.multiselect("Afficher les courbes de :", types_dispos, default=types_dispos[:2] if len(types_dispos)>0 else None)
            
            if choix_types:
                df_viz = df_charts[df_charts["Type"].isin(choix_types)]
                chart = alt.Chart(df_viz).mark_line(point=True).encode(
                    x=alt.X('Date', axis=alt.Axis(format='%d/%m')),
                    y='Score_Global',
                    color='Type',
                    tooltip=['Date', 'Type', 'Score_Global']
                ).properties(height=300).interactive()
                st.altair_chart(chart, use_container_width=True)
            
            with st.expander("📊 Voir le tableau détaillé des scores", expanded=False):
                st.dataframe(
                    df_charts[["Date", "Questionnaire", "Score_Global"]].sort_values("Date", ascending=False),
                    use_container_width=True,
                    hide_index=True
                )
        else:
            st.info("Aucun questionnaire rempli pour le moment.")

        st.divider()

        # --- B. JOURNAL DES EXERCICES ---
        st.markdown("#### 🛠️ Journal des Exercices (Détails)")
        df_exos = df_history[df_history["Questionnaire"].str.contains("Exercice", na=False)].copy()
        
        if not df_exos.empty:
            for idx, row in df_exos.sort_values("Date", ascending=False).iterrows():
                with st.expander(f"🗓️ {row['Date'].strftime('%d/%m')} - {row['Questionnaire']}"):
                    col_del, col_content = st.columns([1, 5])
                    with col_del:
                        st.write("") 
                        if st.button("🗑️ Supprimer", key=f"hist_del_{idx}", type="primary"):
                            supprimer_reponse(current_user, row["Date"], row["Questionnaire"])
                            charger_historique_complet_cache.clear() # On vide le cache pour voir la suppression
                            st.rerun()
                    
                    with col_content:
                        try:
                            d = json.loads(row["Details_Json"])
                            # Affiche le JSON brut ou formaté (suffisant pour historique)
                            st.json(d)
                        except Exception as e:
                            st.error(f"Erreur lecture : {e}")
        else:
            st.info("Aucun exercice réalisé pour le moment.")

    else:
        st.info("Votre historique est vide. Commencez par remplir un bilan ou un exercice !")