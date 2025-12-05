import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

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