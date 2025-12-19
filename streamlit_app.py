import streamlit as st
import pandas as pd
import altair as alt
import time
import secrets
from datetime import datetime
from protocole_config import PROTOCOLE_BARLOW
import os
import json

# Import de toutes les visualisations
from visualisations import (
    afficher_activites, afficher_sommeil, afficher_conso, afficher_compulsions,
    afficher_phq9, afficher_gad7, afficher_isi, afficher_peg, afficher_who5, afficher_wsas
)

st.set_page_config(page_title="Compagnon TCC", page_icon="🧠", layout="wide")
# MASQUER LA NAVIGATION PAR DÉFAUT DE STREAMLIT
st.markdown("""
    <style>
        [data-testid="stSidebarNav"] {display: none;}
    </style>
""", unsafe_allow_html=True)

# =========================================================
# CONFIGURATION DES QUESTIONNAIRES HEBDOMADAIRES (BARLOW)
# =========================================================
QUESTIONS_HEBDO = {
    "Anxiété": {
        "titre": "📉 Échelle d'Anxiété",
        "description": "Évaluez l'intensité moyenne de votre anxiété cette semaine (0 = Nulle, 8 = Extrême).",
        "type": "scale_0_8",
        "questions": ["À quel point vous êtes-vous senti(e) anxieux(se) ou nerveux(se) cette semaine ?"]
    },
    "Dépression": {
        "titre": "☁️ Échelle de Dépression",
        "description": "Évaluez l'intensité moyenne de votre tristesse/dépression cette semaine (0 = Nulle, 8 = Extrême).",
        "type": "scale_0_8",
        "questions": ["À quel point vous êtes-vous senti(e) triste ou déprimé(e) cette semaine ?"]
    },
    "Autres Émotions Négatives": {
        "titre": "😡 Autres Émotions Négatives",
        "description": "Colère, Culpabilité, Honte, etc. (0 = Nulle, 8 = Extrême).",
        "type": "scale_0_8",
        "questions": ["Intensité de la Colère", "Intensité de la Culpabilité", "Intensité de la Honte"]
    },
    "Émotions Positives": {
        "titre": "🌞 Émotions Positives",
        "description": "Joie, Enthousiasme, Fierté, etc. (0 = Nulle, 8 = Extrême).",
        "type": "scale_0_8",
        "questions": ["À quel point avez-vous ressenti de la joie ou du plaisir cette semaine ?"]
    },
    "Fiche de Progrès": {
        "titre": "📈 Fiche des Progrès (Tâches à domicile)",
        "description": "Notez ici vos réussites et difficultés concernant les exercices.",
        "type": "text",
        "questions": [
            "Quelles tâches avez-vous accomplies cette semaine ?",
            "Quelles difficultés avez-vous rencontrées ?",
            "Qu'avez-vous appris ?"
        ]
    }
}

# =========================================================
# 0. SÉCURITÉ & UTILITAIRES
# =========================================================

def generer_code_securise(prefix="PAT", length=6):
    """Génère un code aléatoire sécurisé (ex: PAT-X9J2M)"""
    chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789" 
    suffix = ''.join(secrets.choice(chars) for _ in range(length))
    return f"{prefix}-{suffix}"

# --- INITIALISATION SESSION ---
if "authentifie" not in st.session_state: st.session_state.authentifie = False
if "user_type" not in st.session_state: st.session_state.user_type = None 
if "user_id" not in st.session_state: st.session_state.user_id = "" 

# =========================================================
# 1. FONCTIONS DE BASE DE DONNÉES (OPTIMISÉES AVEC CACHE)
# =========================================================

@st.cache_data(ttl=600)
def verifier_therapeute(identifiant, mot_de_passe):
    try:
        from connect_db import load_data
        data = load_data("Therapeutes")
        if data:
            df = pd.DataFrame(data)
            df["Identifiant"] = df["Identifiant"].astype(str).str.strip()
            df["MotDePasse"] = df["MotDePasse"].astype(str).str.strip()
            user_clean = str(identifiant).strip()
            pwd_clean = str(mot_de_passe).strip()
            user_row = df[(df["Identifiant"] == user_clean) & (df["MotDePasse"] == pwd_clean)]
            if not user_row.empty: return user_row.iloc[0]["ID"] 
    except: pass
    return None

@st.cache_data(ttl=300)
def recuperer_mes_patients(therapeute_id):
    try:
        from connect_db import load_data
        data = load_data("Codes_Patients")
        if data:
            df = pd.DataFrame(data)
            return df[df["Therapeute_ID"] == therapeute_id]
    except: pass
    return pd.DataFrame()

# Cache de 2 min pour les données cliniques
@st.cache_data(ttl=120)
def charger_donnees_specifiques(nom_onglet, patient_id):
    try:
        from connect_db import load_data
        data = load_data(nom_onglet)
        if data:
            df = pd.DataFrame(data)
            if "Patient" in df.columns:
                return df[df["Patient"] == patient_id]
    except: pass
    return pd.DataFrame()

@st.cache_data(ttl=300)
def verifier_code_patient(code):
    try:
        from connect_db import load_data
        data = load_data("Codes_Patients")
        if data:
            df = pd.DataFrame(data)
            if "Code" in df.columns:
                if code.upper() in df["Code"].astype(str).str.upper().values: return True
    except: pass
    return False

# =========================================================
# GESTION DES PERMISSIONS (NOUVEAU SYSTÈME : WHITELIST)
# =========================================================

# Liste de tous les outils disponibles
MAP_OUTILS = {
    "🌙 Agenda Sommeil": "sommeil",
    "📝 Registre Activités": "activites",
    "🍷 Agenda Consos": "conso",
    "🛑 Agenda Compulsions": "compulsions",
    "🧩 Colonnes de Beck": "beck",
    "🔍 Analyse SORC": "sorc",
    "💡 Résolution Problème": "problemes",
    "⚖️ Balance Décisionnelle": "balance",
    "🧗 Exposition": "expo",
    "🧘 Relaxation": "relax",
    "📊 PHQ-9 (Dépression)": "phq9",
    "📊 GAD-7 (Anxiété)": "gad7",
    "📊 ISI (Insomnie)": "isi",
    "📊 PEG (Douleur)": "peg",
    "📊 WHO-5 (Bien-être)": "who5",
    "📊 WSAS (Handicap)": "wsas"
}

@st.cache_data(ttl=300)
def charger_outils_autorises(patient_id):
    """
    Récupère la liste des outils EXPLICITEMENT autorisés pour un patient.
    Par défaut (si pas de ligne), retourne une liste vide [].
    """
    try:
        from connect_db import load_data
        # On utilise une nouvelle table 'Outils_Autorises' (à créer dans GSheets : Patient | Outils)
        data = load_data("Outils_Autorises")
        if data:
            df = pd.DataFrame(data)
            row = df[df["Patient"] == patient_id]
            if not row.empty:
                # La colonne s'appelle 'Outils' et contient "sommeil,beck,phq9"
                outils_str = str(row.iloc[0]["Outils"])
                return [x.strip() for x in outils_str.split(",") if x.strip()]
    except: pass
    return [] # Tout est bloqué par défaut

def sauvegarder_outils_autorises(patient_id, liste_cles):
    """Enregistre la nouvelle liste d'outils autorisés."""
    try:
        from connect_db import save_data, delete_data_flexible
        
        # 1. Nettoyage
        delete_data_flexible("Outils_Autorises", {"Patient": patient_id})
        
        # 2. Sauvegarde
        chaine_outils = ",".join(liste_cles)
        save_data("Outils_Autorises", [patient_id, chaine_outils])
        
        # 3. Mise à jour du cache
        charger_outils_autorises.clear()
        return True
    except Exception as e:
        st.error(f"Erreur sauvegarde outils : {e}")
        return False
    
# --- GESTION COMBINÉE : VALIDATION + COMMENTAIRES (Onglet Suivi_Validation) ---
@st.cache_data(ttl=60)
def charger_suivi_global(patient_id):
    """
    Récupère à la fois la liste des modules validés (Vert) 
    ET les commentaires du thérapeute depuis l'onglet 'Suivi_Validation'.
    Retourne : (liste_modules_valides, dictionnaire_commentaires)
    """
    try:
        from connect_db import load_data
        data = load_data("Suivi_Validation") 
        if data:
            df = pd.DataFrame(data)
            row = df[df["Patient"] == patient_id]
            if not row.empty:
                # 1. Récupération des modules validés
                valides_str = str(row.iloc[0].get("Modules_Valides", ""))
                liste_valides = [x.strip() for x in valides_str.split(",") if x.strip()]
                
                # 2. Récupération des commentaires (JSON stocké dans la colonne 'Commentaires')
                commentaires_json = row.iloc[0].get("Commentaires", "{}")
                # Petit nettoyage si la cellule est vide ou nan
                if not commentaires_json or commentaires_json == "nan" or commentaires_json == "None":
                    dict_notes = {}
                else:
                    try:
                        dict_notes = json.loads(str(commentaires_json))
                    except:
                        dict_notes = {}
                
                return liste_valides, dict_notes
    except Exception as e:
        print(f"Erreur chargement suivi: {e}")
        pass
    return [], {}

def sauvegarder_suivi_global(patient_id, liste_modules, dict_notes):
    """Enregistre tout (Validation + Notes) dans l'onglet Suivi_Validation."""
    try:
        from connect_db import save_data, delete_data_flexible
        
        # 1. Supprimer l'ancienne ligne
        delete_data_flexible("Suivi_Validation", {"Patient": patient_id})
        
        # 2. Préparer les données
        chaine_valides = ",".join(liste_modules)
        json_notes = json.dumps(dict_notes)
        
        # 3. Sauvegarder : [Patient, Modules_Valides, Commentaires]
        # Assure-toi que ton Google Sheet a bien ces 3 colonnes dans cet ordre
        save_data("Suivi_Validation", [patient_id, chaine_valides, json_notes])
        
        # 4. Vider le cache pour rechargement immédiat
        charger_suivi_global.clear() # Important pour voir le changement tout de suite
        return True
    except Exception as e:
        st.error(f"Erreur sauvegarde globale : {e}")
        return False
    
# =========================================================
# GESTION DE LA PROGRESSION PROTOCOLE (NOUVEAU)
# =========================================================

def charger_progression(patient_id):
    """Récupère la liste des modules débloqués pour un patient"""
    try:
        from connect_db import load_data
        data = load_data("Progression")
        if data:
            df = pd.DataFrame(data)
            row = df[df["Patient"] == patient_id]
            if not row.empty:
                modules_str = str(row.iloc[0]["Modules_Actifs"])
                # Retourne une liste propre : ['intro', 'module1']
                return [x.strip() for x in modules_str.split(",") if x.strip()]
    except: pass
    return ["intro"] # Par défaut, seulement l'intro est débloquée

def sauvegarder_progression(patient_id, liste_modules):
    """Enregistre les modules débloqués"""
    try:
        from connect_db import save_data, delete_data_flexible
        # 1. On nettoie l'ancienne progression
        delete_data_flexible("Progression", {"Patient": patient_id})
        
        # 2. On enregistre la nouvelle
        chaine_modules = ",".join(liste_modules)
        save_data("Progression", [patient_id, chaine_modules])
        return True
    except Exception as e:
        st.error(f"Erreur sauvegarde progression : {e}")
        return False

def charger_etat_devoirs(patient_id):
    """Charge la liste des devoirs EXCLUS (décochés) par le thérapeute."""
    try:
        from connect_db import load_data
        data = load_data("Suivi_Devoirs")
        if data:
            df = pd.DataFrame(data)
            row = df[df["Patient"] == patient_id]
            if not row.empty:
                # On stocke sous forme JSON : {"module1": [0], "module2": [1]} (indices décochés)
                json_str = row.iloc[0]["Donnees_Json"]
                return json.loads(json_str)
    except: pass
    return {}

def sauvegarder_etat_devoirs(patient_id, dict_devoirs_exclus):
    """Sauvegarde l'état des devoirs."""
    try:
        from connect_db import save_data, delete_data_flexible
        delete_data_flexible("Suivi_Devoirs", {"Patient": patient_id})
        
        json_str = json.dumps(dict_devoirs_exclus)
        save_data("Suivi_Devoirs", [patient_id, json_str])
        return True
    except Exception as e:
        st.error(f"Erreur sauvegarde devoirs : {e}")
        return False

def sauvegarder_reponse_hebdo(patient_id, nom_questionnaire, score_global, details_dict):
    """Enregistre une réponse à un questionnaire hebdo."""
    try:
        from connect_db import save_data
        # On sauvegarde chaque remplissage comme une nouvelle ligne (historique)
        # Date du jour
        date_jour = datetime.now().strftime("%Y-%m-%d %H:%M")
        json_details = json.dumps(details_dict)
        
        save_data("Reponses_Hebdo", [patient_id, date_jour, nom_questionnaire, score_global, json_details])
        return True
    except Exception as e:
        st.error(f"Erreur sauvegarde hebdo : {e}")
        return False

# --- GESTION DES NOTES DE SÉANCE (NOUVEAU) ---
def charger_notes_seance(patient_id):
    """Charge les notes textuelles du thérapeute pour chaque module."""
    try:
        from connect_db import load_data
        # On utilise une table 'Notes_Seance' (à créer ou simuler)
        data = load_data("Notes_Seance")
        if data:
            df = pd.DataFrame(data)
            row = df[df["Patient"] == patient_id]
            if not row.empty:
                # Format JSON : {"module1": "Patient va bien...", "module2": "..."}
                json_str = row.iloc[0]["Donnees_Json"]
                return json.loads(json_str)
    except: pass
    return {}

def sauvegarder_notes_seance(patient_id, dict_notes):
    """Sauvegarde les notes."""
    try:
        from connect_db import save_data, delete_data_flexible
        delete_data_flexible("Notes_Seance", {"Patient": patient_id})
        
        json_str = json.dumps(dict_notes)
        save_data("Notes_Seance", [patient_id, json_str])
        return True
    except Exception as e:
        st.error(f"Erreur sauvegarde notes : {e}")
        return False

# =========================================================
# 2. ÉCRAN DE CONNEXION
# =========================================================

if not st.session_state.authentifie:
    st.title("🧠 Compagnon TCC")
    st.write("Bienvenue dans votre espace de travail thérapeutique.")

    tab_patient, tab_pro = st.tabs(["👤 Accès Patient", "🩺 Accès Thérapeute"])
    
    with tab_patient:
        st.info("🔒 Entrez votre code unique fourni par votre thérapeute.")
        with st.form("login_patient"):
            code_input = st.text_input("Code Patient (ex: TCC-X9J...)", type="password")
            if st.form_submit_button("Accéder à mon journal"):
                clean_code = code_input.strip().upper()
                if verifier_code_patient(clean_code):
                    st.session_state.authentifie = True
                    st.session_state.user_type = "patient"
                    
                    final_id = clean_code 
                    try:
                        from connect_db import load_data
                        data_p = load_data("Codes_Patients")
                        if data_p:
                            df_p = pd.DataFrame(data_p)
                            match = df_p[df_p["Code"].astype(str).str.upper() == clean_code]
                            if not match.empty:
                                c_cible = "Identifiant" if "Identifiant" in df_p.columns else "Commentaire"
                                final_id = match.iloc[0][c_cible]
                    except: pass

                    st.session_state.user_id = final_id 
                    st.success(f"Bienvenue {final_id}")
                    time.sleep(0.5)
                    st.rerun()
                else: st.error("❌ Code non reconnu.")

    with tab_pro:
        st.warning("Espace réservé aux professionnels.")
        with st.form("login_therapeute"):
            u_in = st.text_input("Identifiant")
            p_in = st.text_input("Mot de passe", type="password")
            if st.form_submit_button("Connexion Pro"):
                th_id = verifier_therapeute(u_in, p_in)
                if th_id:
                    st.session_state.authentifie = True
                    st.session_state.user_type = "therapeute"
                    st.session_state.user_id = th_id
                    st.success(f"Bonjour {th_id}")
                    time.sleep(0.5)
                    st.rerun()
                else: st.error("❌ Identifiants incorrects.")

# =========================================================
# 3. TABLEAUX DE BORD (CONNECTÉ)
# =========================================================
else:
# -----------------------------------------------------
    # A. ESPACE THÉRAPEUTE (OPTIMISÉ & RAPIDE)
    # -----------------------------------------------------
    if st.session_state.user_type == "therapeute":
        st.title("🩺 Espace Thérapeute")
        
        c1, c2 = st.columns([3, 1])
        with c1: st.write(f"Praticien : **{st.session_state.user_id}**")
        with c2: 
            if st.button("Déconnexion"):
                st.session_state.authentifie = False
                st.rerun()
        st.divider()

        # --- OPTIMISATION : Chargement unique de la liste des patients ---
        if "liste_patients_cache" not in st.session_state:
            df_pats = recuperer_mes_patients(st.session_state.user_id)
            if not df_pats.empty:
                st.session_state.liste_patients_cache = df_pats["Identifiant"].unique().tolist()
            else:
                st.session_state.liste_patients_cache = []

        # 1. CRÉATION PATIENT (Code simplifié pour ne pas alourdir)
        with st.expander("➕ Nouveau Patient"):
            c_gen1, c_gen2 = st.columns([1, 2])
            with c_gen1: 
                # Calcul rapide de l'ID suivant sans appel DB si possible
                nb_pats = len(st.session_state.liste_patients_cache)
                prochain_id = f"PAT-{nb_pats+1:03d}"
                id_dossier = st.text_input("Dossier", value=prochain_id)
            with c_gen2:
                st.write(" ")
                if st.button("Générer accès"):
                    ac_code = generer_code_securise("TCC")
                    try:
                        from connect_db import save_data
                        save_data("Codes_Patients", [ac_code, st.session_state.user_id, id_dossier, str(datetime.now().date())])
                        st.success(f"Créé : {id_dossier} -> Code : {ac_code}")
                        # On force le rechargement de la liste au prochain tour
                        if "liste_patients_cache" in st.session_state:
                            del st.session_state.liste_patients_cache
                        recuperer_mes_patients.clear()
                        time.sleep(1)
                        st.rerun()
                    except Exception as e: st.error(e)

        # 2. SÉLECTION PATIENT
        st.subheader("📂 Dossiers Patients")
        
        if st.session_state.liste_patients_cache:
            patient_sel = st.selectbox("Sélectionner un dossier :", st.session_state.liste_patients_cache)

            if patient_sel:
                st.markdown(f"### 👤 {patient_sel}")
                
                # --- GESTION DES OUTILS (NOUVELLE LOGIQUE WHITELIST) ---
                # C'est ici qu'on définit la variable qui manquait
                outils_autorises = charger_outils_autorises(patient_sel)

                with st.expander("🔒 Débloquer des outils pour le patient"):
                    st.caption("Par défaut, tout est masqué. Cochez les outils pour les rendre accessibles.")
                    
                    # On crée la liste des noms lisibles déjà activés
                    INV_MAP = {v: k for k, v in MAP_OUTILS.items()}
                    default_options = [INV_MAP[k] for k in outils_autorises if k in INV_MAP]
                    
                    choix_ouverts = st.multiselect(
                        "Outils accessibles :",
                        options=list(MAP_OUTILS.keys()),
                        default=default_options
                    )
                    
                    if st.button("💾 Mettre à jour les accès"):
                        nouvelle_liste_cles = [MAP_OUTILS[nom] for nom in choix_ouverts]
                        if sauvegarder_outils_autorises(patient_sel, nouvelle_liste_cles):
                            st.success("Accès mis à jour !")
                            time.sleep(0.5)
                            st.rerun()

                st.divider()

# --- ZONE DE GESTION DU PROTOCOLE (BARLOW) ---
                from protocole_config import PROTOCOLE_BARLOW
                import os
                import json

                with st.expander("🗺️ Pilotage du Protocole (Barlow)", expanded=True):
                    
                    # --- CHARGEMENT OPTIMISÉ (CACHE SESSION) ---
                    # On crée une clé unique pour le cache de ce patient
                    cache_key = f"cache_data_{patient_sel}"
                    
                    # Si les données ne sont pas en session, on les charge depuis la DB
                    if cache_key not in st.session_state:
                        progression = charger_progression(patient_sel)
                        devoirs = charger_etat_devoirs(patient_sel)
                        valides, notes = charger_suivi_global(patient_sel)
                        
                        st.session_state[cache_key] = {
                            "progression": progression,
                            "devoirs": devoirs,
                            "valides": valides,
                            "notes": notes
                        }
                    
                    # On travaille avec les données de la session (C'est INSTANTANÉ)
                    data_session = st.session_state[cache_key]
                    progression_patient = data_session["progression"]
                    devoirs_exclus_memoire = data_session["devoirs"]
                    modules_valides_db = data_session["valides"]
                    notes_seance_db = data_session["notes"]

                    if "last_active_module" not in st.session_state:
                        st.session_state.last_active_module = "module0"

                    # Barre de progression
                    nb_total = len(PROTOCOLE_BARLOW)
                    nb_fait = len(modules_valides_db)
                    st.progress(min(nb_fait / nb_total, 1.0), text=f"Avancement : {nb_fait}/{nb_total} modules terminés")
                    st.write("---")

                    # 3. BOUCLE DES MODULES
                    for i, (code_mod, data) in enumerate(PROTOCOLE_BARLOW.items()):
                        
                        is_done = code_mod in modules_valides_db
                        icon = "✅" if is_done else "🟦"
                        should_be_expanded = (code_mod == st.session_state.last_active_module)

                        # EN-TÊTE
                        c_titre, c_lock = st.columns([0.95, 0.05])
                        with c_titre:
                            mon_expander = st.expander(f"{icon} {data['titre']}", expanded=should_be_expanded)
                        
                        with c_lock:
                            is_accessible = code_mod in progression_patient
                            if is_accessible:
                                if st.button("🔒", key=f"lock_{patient_sel}_{code_mod}", help="Bloquer l'accès"):
                                    progression_patient.remove(code_mod)
                                    # Mise à jour DB + Session
                                    sauvegarder_progression(patient_sel, progression_patient)
                                    st.session_state[cache_key]["progression"] = progression_patient
                                    st.rerun()
                            else:
                                if st.button("🔓", type="primary", key=f"unlock_{patient_sel}_{code_mod}", help="Débloquer"):
                                    progression_patient.append(code_mod)
                                    # Mise à jour DB + Session
                                    sauvegarder_progression(patient_sel, progression_patient)
                                    st.session_state[cache_key]["progression"] = progression_patient
                                    st.rerun()

                        # CONTENU
                        with mon_expander:
                            t_action, t_docs = st.tabs(["⚡ Pilotage Séance", "📂 Documents PDF"])
                            
                            with t_action:
                                with st.expander("ℹ️ Objectifs & Outils", expanded=False):
                                    st.info(data['objectifs'])
                                    st.caption(data['outils'])

                                with st.form(key=f"form_main_{patient_sel}_{code_mod}"):
                                    check_list = []

                                    # A. EXAMEN DES TÂCHES
                                    if data['examen_devoirs']:
                                        st.markdown("**🔍 Examen des tâches précédentes**")
                                        for idx, d in enumerate(data['examen_devoirs']):
                                            val = st.checkbox(f"{d['titre']}", key=f"exam_{patient_sel}_{code_mod}_{idx}")
                                            check_list.append(val)
                                            if d.get('pdf'):
                                                nom = os.path.basename(d['pdf'])
                                                st.markdown(f"<small style='color:grey; margin-left: 20px;'>📄 Document : {nom}</small>", unsafe_allow_html=True)
                                        st.write("---")
                                    
                                    # B. ÉTAPES SÉANCE
                                    st.markdown("**📝 Étapes de la séance**")
                                    for idx_etape, etape in enumerate(data['etapes_seance']):
                                        info_bulle = etape.get('details', None) 
                                        val = st.checkbox(
                                            f"{etape['titre']}", 
                                            key=f"step_{patient_sel}_{code_mod}_{idx_etape}",
                                            help=info_bulle
                                        )
                                        check_list.append(val)
                                        if etape.get('pdfs'):
                                            for pdf_path in etape['pdfs']:
                                                nom = os.path.basename(pdf_path)
                                                st.markdown(f"<small style='color:grey; margin-left: 20px;'>📄 Document : {nom}</small>", unsafe_allow_html=True)
                                    
                                    st.write("")
                                    st.write("---")

                                    # C. DEVOIRS
                                    indices_exclus = devoirs_exclus_memoire.get(code_mod, [])
                                    choix_devoirs_temp = [] 
                                    if data['taches_domicile']:
                                        st.markdown("**🏠 Assignation Devoirs**")
                                        for j, dev in enumerate(data['taches_domicile']):
                                            is_chk = (j not in indices_exclus)
                                            val = st.checkbox(dev['titre'], value=is_chk, key=f"dev_{patient_sel}_{code_mod}_{j}")
                                            choix_devoirs_temp.append(val)
                                            if dev.get('pdf'):
                                                nom = os.path.basename(dev['pdf'])
                                                st.markdown(f"<small style='color:grey; margin-left: 20px;'>📄 Document : {nom}</small>", unsafe_allow_html=True)
                                    st.write("---")
                                    
                                    # D. COMMENTAIRES
                                    st.markdown("**👩‍⚕️ Notes de séance**")
                                    texte_actuel = notes_seance_db.get(code_mod, "")
                                    nouvelle_note = st.text_area("Compte-rendu :", value=texte_actuel, height=150, key=f"note_area_{patient_sel}_{code_mod}")
                                    st.write("")
                                    
                                    # E. ENREGISTRER (RAPIDE)
                                    if st.form_submit_button("💾 Enregistrer la séance", type="primary"):
                                        
                                        # 1. Mise à jour Session State (Instantané pour l'utilisateur)
                                        
                                        # Devoirs
                                        if data['taches_domicile']:
                                            nouveaux_exclus = [k for k, chk in enumerate(choix_devoirs_temp) if not chk]
                                            devoirs_exclus_memoire[code_mod] = nouveaux_exclus
                                            st.session_state[cache_key]["devoirs"] = devoirs_exclus_memoire
                                        
                                        # Notes
                                        notes_seance_db[code_mod] = nouvelle_note
                                        st.session_state[cache_key]["notes"] = notes_seance_db

                                        # Progression
                                        if code_mod not in progression_patient:
                                            progression_patient.append(code_mod)
                                            st.session_state[cache_key]["progression"] = progression_patient
                                        
                                        # Validation
                                        tout_est_fini = all(check_list) if check_list else True
                                        if tout_est_fini:
                                            if code_mod not in modules_valides_db:
                                                modules_valides_db.append(code_mod)
                                                st.toast("✅ Validé (Vert) !", icon="🎉")
                                        else:
                                            if code_mod in modules_valides_db:
                                                modules_valides_db.remove(code_mod)
                                                st.toast("ℹ️ En cours (Bleu)", icon="ue800")
                                        st.session_state[cache_key]["valides"] = modules_valides_db

                                        # 2. Sauvegarde Cloud (Le "Slow part")
                                        # On lance les sauvegardes mais on affiche le succès tout de suite
                                        if data['taches_domicile']:
                                            sauvegarder_etat_devoirs(patient_sel, devoirs_exclus_memoire)
                                        
                                        if code_mod not in charger_progression(patient_sel): # Vérif légère
                                            sauvegarder_progression(patient_sel, progression_patient)
                                            
                                        sauvegarder_suivi_global(patient_sel, modules_valides_db, notes_seance_db)
                                        
                                        # 3. Rafraîchissement
                                        st.session_state.last_active_module = code_mod
                                        st.success("✅ Enregistré !")
                                        time.sleep(0.1) # Très court juste pour l'UX
                                        st.rerun()

                            # ONGLET 2 (inchangé)
                            with t_docs:
                                st.info("📂 Documents")
                                if 'pdfs_module' in data and data['pdfs_module']:
                                    for chemin in data['pdfs_module']:
                                        nom_fichier = os.path.basename(chemin)
                                        if os.path.exists(chemin):
                                            with open(chemin, "rb") as f:
                                                st.download_button(f"📥 {nom_fichier}", f, file_name=nom_fichier, key=f"dl_th_{patient_sel}_{code_mod}_{nom_fichier}")
                                        else: st.warning(f"Manque : {nom_fichier}")
                                else: st.caption("Aucun document.")

                # --- FONCTION POUR AJOUTER LE CADENAS DANS LE TITRE ---
                def T(titre, cle_technique):
                    # Si l'outil N'EST PAS dans la liste des autorisés, on met un cadenas
                    if cle_technique not in outils_autorises:
                        return f"{titre} 🔒"
                    return titre

                # =========================================================
                # OPTIMISATION PERFORMANCES : REMPLACEMENT DES TABS PAR SELECTBOX
                # =========================================================
                
                st.write("---")
                st.subheader("📊 Visualisation des Données")

                # 1. On construit la liste des choix avec les Cadenas (Fonction T)
                liste_choix = [
                    "📊 Dashboard Général",
                    T("📝 Activités & Humeur", "activites"), 
                    T("🌙 Sommeil", "sommeil"), 
                    T("🍷 Consommations", "conso"), 
                    T("🛑 Compulsions", "compulsions"),
                    T("🧩 Colonnes de Beck", "beck"), 
                    T("📉 PHQ-9 (Dépression)", "phq9"), 
                    T("😰 GAD-7 (Anxiété)", "gad7"), 
                    T("😴 ISI (Insomnie)", "isi"), 
                    T("🤕 PEG (Douleur)", "peg"), 
                    T("🌿 WHO-5 (Bien-être)", "who5"), 
                    T("🧩 WSAS (Handicap)", "wsas"),
                    T("💡 Résolution Problèmes", "problemes"), 
                    T("🧗 Exposition", "expo"), 
                    T("⚖️ Balance Décisionnelle", "balance"), 
                    T("🔍 Analyse SORC", "sorc")
                ]

                # 2. Le menu déroulant (Ne charge RIEN pour l'instant)
                choix_vue = st.selectbox("Sélectionnez l'outil à analyser :", liste_choix)

                # 3. CHARGEMENT CONDITIONNEL (Lazy Loading)
                # On ne charge QUE ce que l'utilisateur demande
                
                if "Dashboard" in choix_vue:
                    st.info("Sélectionnez un outil spécifique dans la liste ci-dessus pour voir le détail.")
                    # Vous pouvez ajouter ici des indicateurs globaux légers si nécessaire

                elif "Activités" in choix_vue:
                    df_act = charger_donnees_specifiques("Activites", patient_sel)
                    df_hum = charger_donnees_specifiques("Humeur", patient_sel)
                    if not df_act.empty or not df_hum.empty:
                        afficher_activites(df_act, df_hum, patient_sel)
                    else: st.info("Aucune activité enregistrée.")

                elif "Sommeil" in choix_vue:
                    df = charger_donnees_specifiques("Sommeil", patient_sel)
                    if not df.empty: afficher_sommeil(df, patient_sel)
                    else: st.info("Pas de données sommeil.")

                elif "Conso" in choix_vue:
                    df = charger_donnees_specifiques("Addictions", patient_sel)
                    if not df.empty: afficher_conso(df, patient_sel)
                    else: st.info("Pas de consommation enregistrée.")

                elif "Compulsions" in choix_vue:
                    df = charger_donnees_specifiques("Compulsions", patient_sel)
                    if not df.empty: afficher_compulsions(df, patient_sel)
                    else: st.info("Pas de compulsions enregistrées.")

                elif "Beck" in choix_vue:
                    df = charger_donnees_specifiques("Beck", patient_sel)
                    if not df.empty:
                        st.dataframe(df.sort_values(by="Date", ascending=False), use_container_width=True, hide_index=True)
                    else: st.info("Aucune donnée.")

                elif "PHQ-9" in choix_vue:
                    df = charger_donnees_specifiques("PHQ9", patient_sel)
                    afficher_phq9(df, patient_sel)

                elif "GAD-7" in choix_vue:
                    df = charger_donnees_specifiques("GAD7", patient_sel)
                    afficher_gad7(df, patient_sel)

                elif "ISI" in choix_vue:
                    df = charger_donnees_specifiques("ISI", patient_sel)
                    afficher_isi(df, patient_sel)

                elif "PEG" in choix_vue:
                    df = charger_donnees_specifiques("PEG", patient_sel)
                    afficher_peg(df, patient_sel)

                elif "WHO-5" in choix_vue:
                    df = charger_donnees_specifiques("WHO5", patient_sel)
                    afficher_who5(df, patient_sel)

                elif "WSAS" in choix_vue:
                    df = charger_donnees_specifiques("WSAS", patient_sel)
                    afficher_wsas(df, patient_sel)

                elif "Problèmes" in choix_vue:
                    df = charger_donnees_specifiques("Resolution_Probleme", patient_sel)
                    if not df.empty: st.dataframe(df, use_container_width=True)
                    else: st.info("Aucune donnée.")

                elif "Expo" in choix_vue:
                    df = charger_donnees_specifiques("Exposition", patient_sel)
                    if not df.empty: st.dataframe(df, use_container_width=True)
                    else: st.info("Aucune donnée.")

                elif "Balance" in choix_vue:
                    df = charger_donnees_specifiques("Balance_Decisionnelle", patient_sel)
                    if not df.empty: st.dataframe(df, use_container_width=True)
                    else: st.info("Aucune donnée.")

                elif "SORC" in choix_vue:
                    df = charger_donnees_specifiques("SORC", patient_sel)
                    if not df.empty: st.dataframe(df, use_container_width=True)
                    else: st.info("Aucune donnée.")
        
        else:
            st.warning("Aucun patient trouvé.")

            

    # -----------------------------------------------------
    # B. ESPACE PATIENT (AVEC FILTRAGE)
    # -----------------------------------------------------
    elif st.session_state.user_type == "patient":
        
        # 1. CHARGEMENT DES AUTORISATIONS (WHITELIST)
        # On remplace l'ancien appel 'charger_blocages' par le nouveau
        OUTILS_AUTORISES = charger_outils_autorises(st.session_state.user_id)
        
        c_titre, c_logout = st.columns([4, 1])
        with c_titre:
            st.title(f"🧠 Espace Patient")
        with c_logout:
            if st.button("Se déconnecter"):
                st.session_state.authentifie = False
                st.session_state.user_id = "" 
                st.rerun()

        st.divider()

        # =========================================================
        # SECTION 1 : AGENDAS
        # =========================================================
        st.markdown("### 📅 Mes Agendas (Quotidien)")

        # =========================================================
        # SECTION 0 : BILANS HEBDOMADAIRES (NUMÉRIQUES)
        # =========================================================
        st.info("📝 **C'est le moment du bilan ?** Cliquez ci-dessous pour remplir vos questionnaires.")
        
        with st.expander("✍️ Remplir mes questionnaires de la semaine", expanded=False):
            
            # 1. Menu déroulant pour choisir le questionnaire
            choix_quest = st.selectbox("Quel questionnaire voulez-vous remplir ?", list(QUESTIONS_HEBDO.keys()))
            
            # 2. Récupération de la config
            config_q = QUESTIONS_HEBDO[choix_quest]
            st.markdown(f"#### {config_q['titre']}")
            st.caption(config_q['description'])
            
            # 3. Génération du formulaire
            with st.form(key=f"form_hebdo_{choix_quest}"):
                
                reponses = {}
                score_total = 0
                
                # Cas A : Échelles numériques (0-8)
                if config_q['type'] == "scale_0_8":
                    for q in config_q['questions']:
                        st.write(f"**{q}**")
                        # Slider 0 à 8
                        val = st.slider("Intensité", 0, 8, 0, key=f"slider_{choix_quest}_{q}")
                        reponses[q] = val
                        score_total += val # Somme simple pour l'instant
                
                # Cas B : Texte (Fiche progrès)
                elif config_q['type'] == "text":
                    for q in config_q['questions']:
                        val = st.text_area(q, height=100, key=f"txt_{choix_quest}_{q}")
                        reponses[q] = val
                    score_total = -1 # Pas de score numérique applicable
                
                st.write("")
                
                # 4. Bouton de validation
                if st.form_submit_button("Envoyer ce questionnaire", type="primary"):
                    if sauvegarder_reponse_hebdo(st.session_state.user_id, choix_quest, str(score_total), reponses):
                        st.success("✅ Réponse enregistrée avec succès !")
                        time.sleep(1)
                        st.rerun()
        
        st.divider()
        
        c1, c2, c3, c4 = st.columns(4)
        
        # ATTENTION : On change la condition !
        # Avant : if "sommeil" not in OUTILS_BLOQUES
        # Maintenant : if "sommeil" in OUTILS_AUTORISES
        
        if "sommeil" in OUTILS_AUTORISES:
            with c1:
                st.warning("**Sommeil**")
                st.page_link("pages/10_Agenda_Sommeil.py", label="Ouvrir", icon="🌙")
        
        if "activites" in OUTILS_AUTORISES:
            with c2:
                st.warning("**Activités**")
                st.page_link("pages/05_Registre_Activites.py", label="Ouvrir", icon="📝")
        
        if "conso" in OUTILS_AUTORISES:
            with c3:
                st.warning("**Consommations**")
                st.page_link("pages/13_Agenda_Consos.py", label="Ouvrir", icon="🍷")
        
        if "compulsions" in OUTILS_AUTORISES:
            with c4:
                st.warning("**Compulsions**")
                st.page_link("pages/14_Agenda_Compulsions.py", label="Ouvrir", icon="🛑")

        st.write("") 

        # =========================================================
        # SECTION 2 : BOÎTE À OUTILS
        # =========================================================
        st.markdown("### 🛠️ Boîte à Outils (Exercices)")
        
        c5, c6, c7 = st.columns(3)
        with c5:
            if "beck" in OUTILS_AUTORISES:
                st.info("**Restructuration (Beck)**")
                st.page_link("pages/01_Colonnes_Beck.py", label="Lancer", icon="🧩")
                st.write("")
            
            if "sorc" in OUTILS_AUTORISES:
                st.info("**Analyse SORC**")
                st.page_link("pages/12_Analyse_SORC.py", label="Lancer", icon="🔍")
            
        with c6:
            if "problemes" in OUTILS_AUTORISES:
                st.info("**Résolution Problème**")
                st.page_link("pages/06_Resolution_Probleme.py", label="Lancer", icon="💡")
                st.write("")
            
            if "balance" in OUTILS_AUTORISES:
                st.info("**Balance Décisionnelle**")
                st.page_link("pages/11_Balance_Decisionnelle.py", label="Lancer", icon="⚖️")

        with c7:
            if "expo" in OUTILS_AUTORISES:
                st.info("**Exposition**")
                st.page_link("pages/09_Exposition.py", label="Lancer", icon="🧗")
                st.write("")
            
            if "relax" in OUTILS_AUTORISES:
                st.info("**Relaxation**")
                st.page_link("pages/07_Relaxation.py", label="Lancer", icon="🧘")

        st.write("") 

        # =========================================================
        # SECTION 3 : MESURES
        # =========================================================
        st.markdown("### 📊 Mesures & Échelles")
        
        m1, m2, m3 = st.columns(3)
        with m1:
            if "phq9" in OUTILS_AUTORISES:
                st.success("**PHQ-9 (Dépression)**")
                st.page_link("pages/15_Echelle_PHQ9.py", label="Lancer", icon="📊")
        with m2:
            if "gad7" in OUTILS_AUTORISES:
                st.success("**GAD-7 (Anxiété)**")
                st.page_link("pages/16_Echelle_GAD7.py", label="Lancer", icon="📊")
        with m3:
            if "who5" in OUTILS_AUTORISES:
                st.success("**WHO-5 (Bien-être)**")
                st.page_link("pages/20_Echelle_WHO5.py", label="Lancer", icon="📊")

        m4, m5, m6 = st.columns(3)
        with m4:
            if "isi" in OUTILS_AUTORISES:
                st.success("**ISI (Insomnie)**")
                st.page_link("pages/17_Echelle_ISI.py", label="Lancer", icon="📊")
        with m5:
            if "peg" in OUTILS_AUTORISES:
                st.success("**PEG (Douleur)**")
                st.page_link("pages/18_Echelle_PEG.py", label="Lancer", icon="📊")
        with m6:
            if "wsas" in OUTILS_AUTORISES:
                st.success("**WSAS (Impact)**")
                st.page_link("pages/19_Echelle_WSAS.py", label="Lancer", icon="📊")

        st.write("")

        # =========================================================
        # SECTION 4 : BILAN & EXPORT
        # =========================================================
        st.markdown("### 📜 Bilan Global")
        
        b1, b2, b3 = st.columns([1, 1, 2])
        with b1:
            st.page_link("pages/04_Historique.py", label="Voir mon Historique", icon="📜")
        with b2:
            st.page_link("pages/08_Export_Rapport.py", label="Exporter en PDF", icon="📤")
        
        st.divider()
        st.page_link("pages/03_Ressources.py", label="Consulter les Fiches & Ressources", icon="📚")


    # =========================================================
    # 4. SIDEBAR (MENU LATÉRAL) - FILTRÉE ET SÉCURISÉE
    # =========================================================
    with st.sidebar:
        
        # A. LOGIQUE PATIENT
        if st.session_state.user_type == "patient":
            
            # 1. Récupération ID Affichage
            display_id = st.session_state.user_id 
            try:
                from connect_db import load_data
                infos = load_data("Codes_Patients")
                if infos:
                    df_infos = pd.DataFrame(infos)
                    code_actuel = str(st.session_state.user_id).strip().upper()
                    match = df_infos[df_infos["Identifiant"].astype(str).str.strip().str.upper() == code_actuel]
                    if not match.empty:
                        col_id = "Identifiant" if "Identifiant" in df_infos.columns else "Commentaire"
                        display_id = match.iloc[0][col_id]
            except: pass
            
            # 2. Chargement des permissions (au cas où)
            # On s'assure d'avoir la liste à jour
            OUTILS_AUTORISES = charger_outils_autorises(st.session_state.user_id)

            # 3. Affichage Menu
            st.write(f"👤 ID: **{display_id}**")
            st.divider()
            
            st.title("Navigation")
            st.page_link("streamlit_app.py", label="🏠 Accueil")
            st.info("🎯 **Protocole**")
            st.page_link("pages/00_Mon_Parcours.py", label="Mon Parcours", icon="🗺️")
            st.divider()
            # 👆 FIN DE L'AJOUT 👆
            
            # --- AGENDAS ---
            st.caption("📅 Agendas")
            if "sommeil" in OUTILS_AUTORISES:
                st.page_link("pages/10_Agenda_Sommeil.py", label="🌙 Sommeil")
            if "activites" in OUTILS_AUTORISES:
                st.page_link("pages/05_Registre_Activites.py", label="📝 Activités")
            if "conso" in OUTILS_AUTORISES:
                st.page_link("pages/13_Agenda_Consos.py", label="🍷 Consos")
            if "compulsions" in OUTILS_AUTORISES:
                st.page_link("pages/14_Agenda_Compulsions.py", label="🛑 Compulsions")
            
            # --- OUTILS ---
            st.caption("🛠️ Outils")
            if "beck" in OUTILS_AUTORISES:
                st.page_link("pages/01_Colonnes_Beck.py", label="🧩 Beck")
            if "sorc" in OUTILS_AUTORISES:
                st.page_link("pages/12_Analyse_SORC.py", label="🔍 SORC")
            if "problemes" in OUTILS_AUTORISES:
                st.page_link("pages/06_Resolution_Probleme.py", label="💡 Problèmes")
            if "balance" in OUTILS_AUTORISES:
                st.page_link("pages/11_Balance_Decisionnelle.py", label="⚖️ Balance")
            if "expo" in OUTILS_AUTORISES:
                st.page_link("pages/09_Exposition.py", label="🧗 Exposition")
            if "relax" in OUTILS_AUTORISES:
                st.page_link("pages/07_Relaxation.py", label="🧘 Relaxation")
            
            # --- ÉCHELLES ---
            st.caption("📊 Échelles")
            if "phq9" in OUTILS_AUTORISES:
                st.page_link("pages/15_Echelle_PHQ9.py", label="📊 PHQ-9")
            if "gad7" in OUTILS_AUTORISES:
                st.page_link("pages/16_Echelle_GAD7.py", label="📊 GAD-7")
            if "who5" in OUTILS_AUTORISES:
                st.page_link("pages/20_Echelle_WHO5.py", label="📊 WHO-5")
            if "isi" in OUTILS_AUTORISES:
                st.page_link("pages/17_Echelle_ISI.py", label="📊 ISI")
            if "peg" in OUTILS_AUTORISES:
                st.page_link("pages/18_Echelle_PEG.py", label="📊 PEG")
            if "wsas" in OUTILS_AUTORISES:
                st.page_link("pages/19_Echelle_WSAS.py", label="📊 WSAS")
            
            # --- BILAN (Toujours visible) ---
            st.caption("📜 Bilan")
            st.page_link("pages/04_Historique.py", label="Historique")
            st.page_link("pages/08_Export_Rapport.py", label="Export PDF")

        # B. LOGIQUE THÉRAPEUTE
        elif st.session_state.user_type == "therapeute":
            st.title("Navigation")
            st.page_link("streamlit_app.py", label="🏠 Accueil")
            st.page_link("pages/00_Mon_Parcours.py", label="Voir le Parcours", icon="🗺️")