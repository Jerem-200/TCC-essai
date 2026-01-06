import streamlit as st
from google.cloud import storage
from google.oauth2 import service_account
import io

# --- CONFIGURATION ---
# 👇 METTEZ ICI LE NOM EXACT DE VOTRE BUCKET (sans gs://, juste le nom)
BUCKET_NAME = "tcc-app-assets-jeremy" 

# --- AUTHENTIFICATION ---
def get_storage_client():
    # On réutilise vos secrets existants (le même robot !)
    if "gcp_service_account" in st.secrets:
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = service_account.Credentials.from_service_account_info(creds_dict)
        return storage.Client(credentials=creds, project=creds_dict["project_id"])
    else:
        st.error("Secrets introuvables. Vérifiez .streamlit/secrets.toml")
        return None

# --- FONCTIONS COMPATIBLES (Mêmes noms qu'avant pour ne rien casser) ---

def lister_fichiers_drive():
    """Liste les fichiers du Bucket Cloud Storage"""
    client = get_storage_client()
    if not client: return []
    
    try:
        bucket = client.bucket(BUCKET_NAME)
        # On récupère tous les objets (blobs) du bucket
        blobs = bucket.list_blobs()
        
        # On transforme ça en liste de dictionnaires comme le faisait l'ancien code
        # id = le nom du fichier dans le bucket
        return [{'id': b.name, 'name': b.name, 'mimeType': b.content_type} for b in blobs]
    except Exception as e:
        st.error(f"Erreur connexion Storage : {e}")
        return []

def uploader_fichier_drive(file_obj, filename):
    """Envoie un fichier vers le Bucket"""
    client = get_storage_client()
    if not client: return False
    
    try:
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(filename)
        
        # On s'assure d'être au début du fichier
        file_obj.seek(0)
        
        # Upload direct (plus simple et robuste que Drive)
        blob.upload_from_file(file_obj, content_type=file_obj.type)
        return True
    except Exception as e:
        st.error(f"Erreur Upload : {e}")
        return False

def telecharger_fichier_drive(file_id):
    """Télécharge un fichier depuis le Bucket"""
    # Note: Dans GCS, l'ID est le nom du fichier
    client = get_storage_client()
    if not client: return None
    
    try:
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(file_id)
        
        # On télécharge en mémoire RAM
        file_stream = io.BytesIO()
        blob.download_to_file(file_stream)
        file_stream.seek(0)
        return file_stream
    except Exception as e:
        st.error(f"Erreur Téléchargement : {e}")
        return None

def supprimer_fichier_drive(file_id):
    """Supprime un fichier du Bucket"""
    client = get_storage_client()
    if not client: return False
    try:
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(file_id)
        blob.delete()
        return True
    except:
        return False