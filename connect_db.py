import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def save_data(nom_onglet, donnees_liste):
    try:
        # On récupère les secrets directement au format dictionnaire
        # (Plus besoin de json.loads compliqué)
        if "gcp_service_account" in st.secrets:
            key_dict = st.secrets["gcp_service_account"]
        else:
            st.error("Clé 'gcp_service_account' introuvable dans les Secrets.")
            return False

        # Connexion
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(key_dict, scope)
        client = gspread.authorize(creds)
        
        # Ouverture Sheet
        sheet = client.open("TCC_Base_Donnees")
        
        # Onglet
        try:
            worksheet = sheet.worksheet(nom_onglet)
        except:
            worksheet = sheet.add_worksheet(title=nom_onglet, rows=100, cols=20)
            
        # Ajout
        worksheet.append_row(donnees_liste)
        return True
        
    except Exception as e:
        st.error(f"Erreur technique : {e}")
        return False