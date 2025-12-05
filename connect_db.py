import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

def save_data(nom_onglet, donnees_liste):
    """
    Sauvegarde une ligne de données dans l'onglet spécifié du Google Sheet.
    """
    try:
        # 1. Récupération des secrets
        # On lit le JSON stocké dans les secrets Streamlit
        key_dict = json.loads(st.secrets["service_account_info"])
        
        # 2. Connexion à Google
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(key_dict, scope)
        client = gspread.authorize(creds)
        
        # 3. Ouverture du fichier Excel
        # ATTENTION : Remplacez "TCC_Base_Donnees" par le nom EXACT de votre fichier Sheet
        sheet = client.open("TCC_Base_Donnees")
        
        # 4. Sélection ou Création de l'onglet
        try:
            worksheet = sheet.worksheet(nom_onglet)
        except:
            # Si l'onglet n'existe pas, on le crée
            worksheet = sheet.add_worksheet(title=nom_onglet, rows=100, cols=20)
            
        # 5. Ajout de la ligne
        worksheet.append_row(donnees_liste)
        return True
        
    except Exception as e:
        st.error(f"Erreur de sauvegarde Cloud : {e}")
        return False