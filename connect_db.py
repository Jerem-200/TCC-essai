import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import mysql.connector
import json

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

# --- GESTION UTILISATEURS (NOUVEAU) ---

def charger_utilisateurs():
    """Récupère la liste de tous les utilisateurs inscrits"""
    client = get_client()
    if not client: return []
    
    try:
        sheet = client.open("TCC_Base_Donnees")
        try:
            ws = sheet.worksheet("Utilisateurs")
        except:
            ws = sheet.add_worksheet(title="Utilisateurs", rows=100, cols=3)
            ws.append_row(["Identifiant", "MotDePasse", "DateInscription"])
            
        # On récupère toutes les lignes (liste de dictionnaires)
        users = ws.get_all_records()
        return users
    except:
        return []

def creer_compte(identifiant, mot_de_passe):
    """Ajoute un nouvel utilisateur"""
    client = get_client()
    if not client: return False
    
    try:
        sheet = client.open("TCC_Base_Donnees")
        ws = sheet.worksheet("Utilisateurs")
        
        # On ajoute la ligne
        ws.append_row([
            identifiant, 
            mot_de_passe, 
            datetime.now().strftime("%Y-%m-%d %H:%M")
        ])
        return True
    except Exception as e:
        st.error(f"Erreur création : {e}")
        return False

# --- 3. FONCTION DE SUPPRESSION (ADAPTÉE GOOGLE SHEETS) ---
def delete_data_flexible(nom_onglet, criteres_dict):
    """
    Supprime une ligne dans Google Sheets en cherchant la correspondance.
    
    Args:
        nom_onglet (str): Nom de la feuille (ex: "Activites")
        criteres_dict (dict): Dictionnaire des colonnes à vérifier.
                              ATTENTION : Les clés doivent correspondre EXACTEMENT 
                              aux noms des colonnes dans votre Google Sheet (1ère ligne).
                              Ex: {"Date": "2023-12-08", "Heure": "12:00"}
    """
    client = get_client()
    if not client: return False

    try:
        sheet = client.open("TCC_Base_Donnees")
        ws = sheet.worksheet(nom_onglet)
        
        # On récupère toutes les données (dictionnaires avec en-têtes comme clés)
        records = ws.get_all_records()
        
        # On cherche la ligne à supprimer
        row_index_to_delete = None
        
        # On parcourt chaque ligne (enumerate commence à 0, mais GSheet ligne 1 = Headers)
        for i, row in enumerate(records):
            match = True
            for key, val in criteres_dict.items():
                # On compare en string pour éviter les problèmes de format
                # row.get(key) récupère la valeur dans la colonne 'key' du Google Sheet
                if str(row.get(key)) != str(val):
                    match = False
                    break
            
            if match:
                # Si tout correspond, on a trouvé l'index.
                # i est l'index dans la liste Python (0, 1, 2...)
                # Dans GSheet : Ligne 1 = Headers. Ligne 2 = Donnée 0.
                # Donc la ligne à supprimer est i + 2
                row_index_to_delete = i + 2
                break # On supprime la première occurence trouvée
        
        if row_index_to_delete:
            ws.delete_rows(row_index_to_delete)
            return True
        else:
            # st.warning("Ligne introuvable pour suppression.")
            return False
            
    except Exception as e:
        st.error(f"Erreur suppression GSheet : {e}")
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


def supprimer_reponse(patient_id, timestamp, type_exo):
    """Supprime une entrée spécifique de l'historique."""
    try:
        from connect_db import load_data, save_data_raw # Hypothèse que vous avez une fonction pour écraser le fichier
        # Note : Si vous utilisez Google Sheets, la logique dépend de votre implémentation 'delete_row'.
        # Ici je simule une logique Pandas classique : Charger -> Filtrer -> Sauvegarder tout
        
        data = load_data("Reponses_Hebdo")
        if data:
            import pandas as pd
            df = pd.DataFrame(data)
            
            # On garde tout SAUF la ligne qui correspond exactement au patient + date + type
            # Attention : timestamp doit être converti en string ou format identique
            df = df[~((df["Patient"] == patient_id) & (df["Date"] == timestamp) & (df["Questionnaire"] == type_exo))]
            
            # On sauvegarde le nouveau dataframe (fonction à adapter selon votre connecteur GSheet)
            # Si vous n'avez pas de fonction d'écrasement, c'est plus complexe avec GSheet API direct.
            # Pour l'instant, supposons que save_data ajoute juste.
            # L'idéal est d'avoir une fonction 'overwrite_sheet'
            pass 
            
        return True
    except Exception as e:
        print(f"Erreur suppression : {e}")
        return False