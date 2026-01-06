import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload
import io

# --- CONFIGURATION ---
# Mettez ici l'ID de votre dossier Drive (copié à l'étape 1)
# Ou mieux : mettez-le dans st.secrets["drive"]["folder_id"]
DRIVE_FOLDER_ID = "16q9tWGTHu39_UXsGajKhsWwhrCiZEGd5" 

# Fonction d'authentification (Même logique que pour GSheets)
def get_drive_service():
    # On vérifie si les secrets sont disponibles
    if "gcp_service_account" in st.secrets:
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = service_account.Credentials.from_service_account_info(
            creds_dict,
            scopes=["https://www.googleapis.com/auth/drive"]
        )
        return build('drive', 'v3', credentials=creds)
    else:
        st.error("Secrets GCP introuvables. Vérifiez .streamlit/secrets.toml")
        return None

def lister_fichiers_drive():
    """Retourne une liste de dict : [{'id': '...', 'name': '...'}, ...]"""
    service = get_drive_service()
    if not service: return []
    
    query = f"'{DRIVE_FOLDER_ID}' in parents and trashed=false"
    results = service.files().list(q=query, fields="files(id, name, mimeType)").execute()
    return results.get('files', [])

def uploader_fichier_drive(file_obj, filename):
    """Envoie un fichier Streamlit (BytesIO) vers Drive"""
    service = get_drive_service()
    if not service: return False
    
    file_metadata = {
        'name': filename,
        'parents': [DRIVE_FOLDER_ID]
    }
    
    media = MediaIoBaseUpload(file_obj, mimetype=file_obj.type, resumable=False)
    
    try:
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        return True
    except Exception as e:
        st.error(f"Erreur Upload Drive : {e}")
        return False

def telecharger_fichier_drive(file_id):
    """Récupère le contenu binaire d'un fichier Drive pour le bouton download"""
    service = get_drive_service()
    if not service: return None
    
    request = service.files().get_media(fileId=file_id)
    file_stream = io.BytesIO()
    downloader = MediaIoBaseDownload(file_stream, request)
    
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        
    file_stream.seek(0)
    return file_stream

def supprimer_fichier_drive(file_id):
    service = get_drive_service()
    if not service: return False
    try:
        service.files().delete(fileId=file_id).execute()
        return True
    except:
        return False