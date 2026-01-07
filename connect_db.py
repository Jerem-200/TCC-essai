import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import os 
import json
import pandas as pd
import secrets

SHEET_ID = "1xLf21h1C7Ej0tUsbnuKQSpHonlOAZ4bEvf90fSsmehI"

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
        sheet = client.open_by_key(SHEET_ID)    
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
        sheet = client.open_by_key(SHEET_ID)
        ws = sheet.worksheet(nom_onglet)
        return ws.get_all_records()
    except:
        return []

def delete_data_flexible(nom_onglet, criteres_dict):
    """Supprime une ligne spécifique selon des critères."""
    client = get_client()
    if not client: return False

    try:
        sheet = client.open_by_key(SHEET_ID)
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

#@st.cache_data(ttl=600)
def verifier_therapeute(identifiant, mot_de_passe):
    """
    Vérifie les identifiants et retourne (user_id, liste_licences).
    Retourne (None, []) si échec.
    """
    try:
        # On suppose que tu as une fonction load_data qui lit "Therapeutes"
        # Si tu utilises une autre méthode pour lire le sheet, adapte cette ligne
        users = load_data("Therapeutes") 
        
        if users:
            df = pd.DataFrame(users)
            # Nettoyage des chaînes
            identifiant = str(identifiant).strip()
            mot_de_passe = str(mot_de_passe).strip()
            
            # Recherche de l'utilisateur (exemple simple)
            # Adapte les noms de colonnes selon ton Sheet exact ("Identifiant", "MotDePasse", "ID")
            match = df[
                (df["Identifiant"].astype(str).str.strip() == identifiant) & 
                (df["MotDePasse"].astype(str).str.strip() == mot_de_passe)
            ]
            
            if not match.empty:
                user_row = match.iloc[0]
                user_id = user_row["ID"] # ou la colonne qui sert d'ID unique
                
                # --- RECUPERATION DES LICENCES ---
                # On regarde si la colonne "Licences" existe et contient quelque chose
                liste_licences = []
                if "Licences" in user_row and pd.notna(user_row["Licences"]):
                    raw_licences = str(user_row["Licences"])
                    # On sépare par la virgule : "barlow,estime" -> ["barlow", "estime"]
                    liste_licences = [x.strip() for x in raw_licences.split(",") if x.strip()]
                
                # Si la colonne est vide ou n'existe pas, on peut donner un accès par défaut ou rien
                if not liste_licences:
                    liste_licences = ["barlow"] # Optionnel : Barlow par défaut pour tous
                
                return user_id, liste_licences

    except Exception as e:
        print(f"Erreur connexion : {e}")
        
    return None, []

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


# =========================================================
# 4. NOUVELLES FONCTIONS (MESSAGES & TACHES) - VERSION CORRIGÉE
# =========================================================

# --- GESTION DU MESSAGE THÉRAPEUTE ---

def charger_message_therapeute(patient_id):
    """Récupère le message depuis l'onglet Messages_Therapeutes"""
    try:
        data = load_data("Messages_Therapeutes")
        if data:
            df = pd.DataFrame(data)
            # On vérifie que les colonnes existent
            if "Patient" in df.columns and "Message" in df.columns:
                row = df[df["Patient"] == patient_id]
                if not row.empty:
                    # On prend le dernier message trouvé
                    return str(row.iloc[-1]["Message"])
    except Exception as e:
        print(f"Erreur chargement message: {e}")
    return ""

def sauvegarder_message_therapeute(patient_id, message):
    """Supprime l'ancien message et sauvegarde le nouveau"""
    try:
        # 1. On nettoie : on supprime les anciens messages de ce patient
        # pour éviter d'accumuler des lignes inutiles.
        delete_data_flexible("Messages_Therapeutes", {"Patient": patient_id})
        
        # 2. On prépare la nouvelle ligne
        date_str = str(datetime.now().strftime("%Y-%m-%d %H:%M"))
        nouvelle_ligne = [patient_id, message, date_str]
        
        # 3. On utilise votre fonction save_data existante (append_row)
        return save_data("Messages_Therapeutes", nouvelle_ligne)
    except Exception as e:
        st.error(f"Erreur save message: {e}")
        return False

# --- GESTION DES TACHES (ALERTES) ---

def charger_taches_assignees(patient_id):
    """Récupère la liste des tâches (convertit le JSON textuel en liste Python)"""
    try:
        data = load_data("Taches_Assignees")
        if data:
            df = pd.DataFrame(data)
            if "Patient" in df.columns and "Taches_JSON" in df.columns:
                row = df[df["Patient"] == patient_id]
                if not row.empty:
                    json_text = row.iloc[-1]["Taches_JSON"]
                    # On transforme le texte "[beck, sommeil]" en vraie liste Python
                    return json.loads(str(json_text))
    except Exception:
        pass # Retourne vide si erreur ou pas trouvé
    return []

def sauvegarder_taches_assignees(patient_id, liste_codes):
    """Sauvegarde la liste des codes outils sous forme de JSON"""
    try:
        # 1. On nettoie l'existant
        delete_data_flexible("Taches_Assignees", {"Patient": patient_id})
        
        # 2. On prépare la donnée (Conversion Liste -> Texte JSON pour Google Sheet)
        taches_str = json.dumps(liste_codes) # Ex: "['beck', 'sommeil']"
        date_str = str(datetime.now().strftime("%Y-%m-%d %H:%M"))
        
        nouvelle_ligne = [patient_id, taches_str, date_str]
        
        # 3. On sauvegarde
        return save_data("Taches_Assignees", nouvelle_ligne)
    except Exception as e:
        st.error(f"Erreur save taches: {e}")
        return False
    
# --- GESTION DU JOURNAL DE BORD (SÉPARÉ DU PROTOCOLE) ---

def charger_journal_patient(patient_id):
    """Charge uniquement les notes du journal personnel"""
    try:
        data = load_data("Journal_Patient")
        if data:
            df = pd.DataFrame(data)
            if "Patient" in df.columns:
                df = df[df["Patient"] == patient_id]
                # On trie par date de séance (la plus récente en haut)
                if not df.empty and "Date_Seance" in df.columns:
                    df["Date_Seance"] = pd.to_datetime(df["Date_Seance"])
                    return df.sort_values("Date_Seance", ascending=False)
                return df
    except Exception as e:
        print(f"Erreur chargement journal: {e}")
    return pd.DataFrame()

def sauvegarder_note_journal(patient_id, date_seance, contenu):
    """Sauvegarde une note dans l'onglet Journal_Patient"""
    try:
        # Format : Patient, Date de la séance, Le texte, Timestamp technique
        row = [
            patient_id, 
            str(date_seance), 
            contenu, 
            str(datetime.now().strftime("%Y-%m-%d %H:%M"))
        ]
        return save_data("Journal_Patient", row)
    except Exception as e:
        st.error(f"Erreur sauvegarde note: {e}")
        return False
    
# Gestion des licences protocoles par patient

def charger_permissions_patient(patient_id):
    """
    Retourne la liste des codes protocoles autorisés pour ce patient.
    """
    filepath = "data/Permissions_Patients.json"
    
    # Par défaut, on veut que le patient ait accès à Barlow 
    # (sauf si tu veux vraiment qu'il n'ait rien au début)
    default_access = ["barlow"] 

    if not os.path.exists(filepath):
        return default_access # <--- Modifié ici

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Si le patient n'est pas dans la liste, on lui donne l'accès par défaut
            return data.get(patient_id, default_access) # <--- Modifié ici
    except Exception as e:
        print(f"Erreur lecture permissions : {e}")
        return default_access

def sauvegarder_permissions_patient(patient_id, liste_codes):
    """
    Enregistre les droits. Crée le dossier et le fichier si nécessaires.
    """
    filepath = "data/Permissions_Patients.json"
    
    # --- CORRECTION ICI : CRÉATION AUTOMATIQUE DU DOSSIER ---
    # On vérifie si le dossier 'data' existe, sinon on le crée
    dossier = os.path.dirname(filepath)
    if dossier and not os.path.exists(dossier):
        os.makedirs(dossier, exist_ok=True)
    # --------------------------------------------------------

    # 1. On charge l'existant pour ne pas écraser les autres patients
    data = {}
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                # Si le fichier est vide ou corrompu, on gère l'erreur
                content = f.read()
                if content:
                    data = json.loads(content)
        except:
            data = {} # Repart de zéro en cas de fichier corrompu
    
    # 2. On met à jour pour CE patient
    data[patient_id] = liste_codes
    
    # 3. On sauvegarde le tout
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)