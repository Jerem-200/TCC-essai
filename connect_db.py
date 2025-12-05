import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def save_data(nom_onglet, donnees_liste):
    try:
        # --- NOUVELLE MÉTHODE PLUS SIMPLE ---
        # On regarde si la configuration est au format "TOML" (sans json.loads)
        if "gcp_service_account" in st.secrets:
            key_dict = st.secrets["gcp_service_account"]
        # Sinon, on garde l'ancienne méthode au cas où
        elif "service_account_info" in st.secrets:
            import json
            key_dict = json.loads(st.secrets["service_account_info"], strict=False)
        else:
            st.error("Aucune clé trouvée dans les Secrets.")
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