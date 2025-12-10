import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import mysql.connector

# --- FONCTION DE CONNEXION ---
def get_client():
    try:
        if "gcp_service_account" in st.secrets:
            key_dict = st.secrets["gcp_service_account"]
        elif "service_account_info" in st.secrets:
            import json
            key_dict = json.loads(st.secrets["service_account_info"], strict=False)
        else:
            return None

        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(key_dict, scope)
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        st.error(f"Erreur connexion : {e}")
        return None

# --- SAUVEGARDE DES DONNÉES (Beck, BDI, etc.) ---
def save_data(nom_onglet, donnees_liste):
    client = get_client()
    if not client: return False
    
    try:
        sheet = client.open("TCC_Base_Donnees")
        try:
            worksheet = sheet.worksheet(nom_onglet)
        except:
            worksheet = sheet.add_worksheet(title=nom_onglet, rows=100, cols=20)
        
        worksheet.append_row(donnees_liste)
        return True
    except Exception as e:
        st.error(f"Erreur sauvegarde : {e}")
        return False

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

# --- CHARGEMENT DES DONNÉES ---
def load_data(nom_onglet):
    """Récupère toutes les données d'un onglet sous forme de liste de dictionnaires"""
    client = get_client()
    if not client: return []
    
    try:
        sheet = client.open("TCC_Base_Donnees")
        ws = sheet.worksheet(nom_onglet)
        return ws.get_all_records() # Retourne une liste de dicts
    except:
        return [] # Retourne une liste vide si l'onglet n'existe pas ou erreur