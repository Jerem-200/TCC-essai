import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import json
import pandas as pd

# =========================================================
# 1. CONNEXION OPTIMISÉE (CACHE)
# =========================================================

# Le décorateur @st.cache_resource garde la connexion en mémoire !
# Elle ne se relance pas à chaque clic.
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
# 2. FONCTIONS DE LECTURE / ECRITURE
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

# =========================================================
# 3. GESTION DES UTILISATEURS
# =========================================================

def charger_utilisateurs():
    """Récupère la liste de tous les utilisateurs inscrits"""
    return load_data("Utilisateurs")

def creer_compte(identifiant, mot_de_passe):
    """Ajoute un nouvel utilisateur"""
    # On vérifie d'abord que l'onglet existe via save_data qui gère la création
    row = [identifiant, mot_de_passe, datetime.now().strftime("%Y-%m-%d %H:%M")]
    return save_data("Utilisateurs", row)

# =========================================================
# 4. SUPPRESSION (LOGIQUE CORRIGÉE)
# =========================================================

def delete_data_flexible(nom_onglet, criteres_dict):
    """
    Supprime une ligne spécifique selon des critères.
    Optimisé pour trouver l'index sans tout recharger.
    """
    client = get_client()
    if not client: return False

    try:
        sheet = client.open("TCC_Base_Donnees")
        ws = sheet.worksheet(nom_onglet)
        
        # On récupère tout pour chercher l'index
        records = ws.get_all_records()
        
        row_index_to_delete = None
        
        # i commence à 0, mais dans GSheet ligne 1 = Headers. 
        # Donc la donnée 0 est à la ligne 2.
        for i, row in enumerate(records):
            match = True
            for key, val in criteres_dict.items():
                # Comparaison en string pour éviter erreurs de type
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

def supprimer_reponse(patient_id, timestamp, type_exo):
    """
    Supprime une entrée de l'historique (Reponses_Hebdo).
    Cette fonction appelle delete_data_flexible qui fait le travail réel.
    """
    # On reformate le timestamp si c'est un objet datetime, sinon on le laisse en string
    date_str = timestamp
    if hasattr(timestamp, 'strftime'):
        date_str = timestamp.strftime("%Y-%m-%d %H:%M")
    
    criteres = {
        "Patient": patient_id,
        "Date": str(date_str), # On s'assure que c'est bien une string
        "Questionnaire": type_exo
    }
    
    return delete_data_flexible("Reponses_Hebdo", criteres)

# =========================================================
# 5. SAUVEGARDE SPÉCIFIQUE
# =========================================================

def sauvegarder_reponse_hebdo(patient_id, nom_questionnaire, score_global, details_dict):
    """Enregistre une réponse ou un exercice."""
    date_jour = datetime.now().strftime("%Y-%m-%d %H:%M")
    # Conversion du dict en JSON texte pour le stockage
    json_details = json.dumps(details_dict, ensure_ascii=False)
    
    row = [patient_id, date_jour, nom_questionnaire, score_global, json_details]
    return save_data("Reponses_Hebdo", row)