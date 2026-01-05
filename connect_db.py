import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import json
import pandas as pd
import secrets

# =========================================================
# 1. CONNEXION BAS NIVEAU (CACHE RESOURCE)
# =========================================================
# Ce cache est différent : il garde la connexion ouverte
# pour ne pas se reconnecter à Google à chaque clic.

@st.cache_resource(ttl=3600) 
def get_client():
    try:
        # Gestion des secrets (supporte les deux formats courants)
        if "gcp_service_account" in st.secrets:
            key_dict = st.secrets["gcp_service_account"]
        elif "service_account_info" in st.secrets:
            key_dict = json.loads(st.secrets["service_account_info"], strict=False)
        else:
            st.error("Secrets Google non trouvés.")
            return None

        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(key_dict, scope)
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        st.error(f"Erreur connexion Google : {e}")
        return None

# =========================================================
# 2. FONCTIONS GÉNÉRIQUES (LECTURE / ECRITURE)
# =========================================================

def save_data(nom_onglet, donnees_liste):
    """Ajoute une ligne à la fin de l'onglet spécifié."""
    client = get_client()
    if not client: return False
    
    try:
        sheet = client.open("TCC_Base_Donnees")
        try:
            worksheet = sheet.worksheet(nom_onglet)
        except:
            # Création de l'onglet s'il n'existe pas
            worksheet = sheet.add_worksheet(title=nom_onglet, rows=100, cols=20)
        
        worksheet.append_row(donnees_liste)
        return True
    except Exception as e:
        st.error(f"Erreur sauvegarde : {e}")
        return False

def load_data(nom_onglet):
    """Récupère toutes les données d'un onglet."""
    client = get_client()
    if not client: return []
    
    try:
        sheet = client.open("TCC_Base_Donnees")
        ws = sheet.worksheet(nom_onglet)
        return ws.get_all_records()
    except:
        return []

def delete_data_flexible(nom_onglet, criteres_dict):
    """Supprime une ligne spécifique selon des critères."""
    client = get_client()
    if not client: return False

    try:
        sheet = client.open("TCC_Base_Donnees")
        ws = sheet.worksheet(nom_onglet)
        records = ws.get_all_records()
        row_index_to_delete = None
        
        # i commence à 0, mais dans GSheet ligne 1 = Headers -> Data commence ligne 2
        for i, row in enumerate(records):
            match = True
            for key, val in criteres_dict.items():
                if str(row.get(key)) != str(val):
                    match = False
                    break
            if match:
                row_index_to_delete = i + 2
                break 
        
        if row_index_to_delete:
            ws.delete_rows(row_index_to_delete)
            return True
        else:
            return False
            
    except Exception as e:
        st.error(f"Erreur suppression : {e}")
        return False

# =========================================================
# 3. LOGIQUE MÉTIER (CACHE DATA)
# =========================================================
# Ici, on utilise @st.cache_data pour mémoriser les RÉSULTATS (les DataFrames)
# et rendre l'appli rapide.

@st.cache_data(ttl=600)
def verifier_therapeute(identifiant, mot_de_passe):
    try:
        data = load_data("Therapeutes")
        if data:
            df = pd.DataFrame(data)
            # Nettoyage pour éviter les erreurs d'espaces ou de types
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
        data = load_data("Codes_Patients")
        if data:
            df = pd.DataFrame(data)
            return df[df["Therapeute_ID"] == therapeute_id]
    except: pass
    return pd.DataFrame()

@st.cache_data(ttl=300)
def verifier_code_patient(code):
    try:
        data = load_data("Codes_Patients")
        if data:
            df = pd.DataFrame(data)
            if "Code" in df.columns:
                if code.upper() in df["Code"].astype(str).str.upper().values: return True
    except: pass
    return False

@st.cache_data(ttl=120)
def charger_donnees_specifiques(nom_onglet, patient_id):
    try:
        data = load_data(nom_onglet)
        if data:
            df = pd.DataFrame(data)
            if "Patient" in df.columns:
                return df[df["Patient"] == patient_id]
    except: pass
    return pd.DataFrame()

# --- GESTION DES OUTILS AUTORISÉS (WHITELIST) ---

@st.cache_data(ttl=300)
def charger_outils_autorises(patient_id):
    try:
        data = load_data("Outils_Autorises")
        if data:
            df = pd.DataFrame(data)
            row = df[df["Patient"] == patient_id]
            if not row.empty:
                outils_str = str(row.iloc[0]["Outils"])
                return [x.strip() for x in outils_str.split(",") if x.strip()]
    except: pass
    return [] 

def sauvegarder_outils_autorises(patient_id, liste_cles):
    # Pas de cache ici car c'est une action d'écriture
    try:
        delete_data_flexible("Outils_Autorises", {"Patient": patient_id})
        chaine_outils = ",".join(liste_cles)
        save_data("Outils_Autorises", [patient_id, chaine_outils])
        charger_outils_autorises.clear() # On vide le cache lecture
        return True
    except: return False

# --- GESTION SUIVI GLOBAL (VALIDATION + COMMENTAIRES) ---

@st.cache_data(ttl=60)
def charger_suivi_global(patient_id):
    try:
        data = load_data("Suivi_Validation") 
        if data:
            df = pd.DataFrame(data)
            row = df[df["Patient"] == patient_id]
            if not row.empty:
                valides_str = str(row.iloc[0].get("Modules_Valides", ""))
                liste_valides = [x.strip() for x in valides_str.split(",") if x.strip()]
                
                commentaires_json = row.iloc[0].get("Commentaires", "{}")
                if not commentaires_json or commentaires_json == "nan": dict_notes = {}
                else:
                    try: dict_notes = json.loads(str(commentaires_json))
                    except: dict_notes = {}
                return liste_valides, dict_notes
    except: pass
    return [], {}

def sauvegarder_suivi_global(patient_id, liste_modules, dict_notes):
    try:
        delete_data_flexible("Suivi_Validation", {"Patient": patient_id})
        chaine_valides = ",".join(liste_modules)
        json_notes = json.dumps(dict_notes)
        save_data("Suivi_Validation", [patient_id, chaine_valides, json_notes])
        charger_suivi_global.clear()
        return True
    except: return False

# --- GESTION PROGRESSION PROTOCOLE ---

@st.cache_data(ttl=300)
def charger_progression(patient_id):
    try:
        data = load_data("Progression")
        if data:
            df = pd.DataFrame(data)
            row = df[df["Patient"] == patient_id]
            if not row.empty:
                modules_str = str(row.iloc[0]["Modules_Actifs"])
                return [x.strip() for x in modules_str.split(",") if x.strip()]
    except: pass
    return ["intro"]

def sauvegarder_progression(patient_id, liste_modules):
    try:
        delete_data_flexible("Progression", {"Patient": patient_id})
        chaine_modules = ",".join(liste_modules)
        save_data("Progression", [patient_id, chaine_modules])
        return True
    except: return False

# --- GESTION DEVOIRS ---

@st.cache_data(ttl=300)
def charger_etat_devoirs(patient_id):
    try:
        data = load_data("Suivi_Devoirs")
        if data:
            df = pd.DataFrame(data)
            row = df[df["Patient"] == patient_id]
            if not row.empty:
                json_str = row.iloc[0]["Donnees_Json"]
                return json.loads(json_str)
    except: pass
    return {}

def sauvegarder_etat_devoirs(patient_id, dict_devoirs_exclus):
    try:
        delete_data_flexible("Suivi_Devoirs", {"Patient": patient_id})
        json_str = json.dumps(dict_devoirs_exclus)
        save_data("Suivi_Devoirs", [patient_id, json_str])
        return True
    except: return False

# --- SAUVEGARDE REPONSES EXERCICES ---

def sauvegarder_reponse_hebdo(patient_id, nom_questionnaire, score_global, details_dict):
    date_jour = datetime.now().strftime("%Y-%m-%d %H:%M")
    json_details = json.dumps(details_dict, ensure_ascii=False)
    row = [patient_id, date_jour, nom_questionnaire, score_global, json_details]
    return save_data("Reponses_Hebdo", row)

def supprimer_reponse(patient_id, timestamp, type_exo):
    date_str = timestamp
    if hasattr(timestamp, 'strftime'):
        date_str = timestamp.strftime("%Y-%m-%d %H:%M")
    
    criteres = {
        "Patient": patient_id,
        "Date": str(date_str),
        "Questionnaire": type_exo
    }
    return delete_data_flexible("Reponses_Hebdo", criteres)

# --- UTILITAIRES DIVERS ---

def generer_code_securise(prefix="PAT", length=6):
    chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789" 
    suffix = ''.join(secrets.choice(chars) for _ in range(length))
    return f"{prefix}-{suffix}"