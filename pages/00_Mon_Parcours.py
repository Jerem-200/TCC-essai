import streamlit as st
import os
from protocole_config import PROTOCOLE_BARLOW

# Import sécurisé de la fonction de chargement
try:
    from streamlit_app import charger_progression
except ImportError:
    # Fonction de secours si l'import échoue
    def charger_progression(uid): return ["module0"]

st.set_page_config(page_title="Mon Parcours", page_icon="🗺️")

if "authentifie" not in st.session_state or not st.session_state.authentifie:
    st.warning("🔒 Veuillez vous connecter.")
    st.page_link("streamlit_app.py", label="Retour Accueil", icon="🏠")
    st.stop()

# --- RÉCUPÉRATION DONNÉES ---
current_user = st.session_state.get("user_id", "")
modules_debloques = charger_progression(current_user)

st.title("🗺️ Mon Parcours de Soin")

# --- BOUCLE D'AFFICHAGE ---
for code_module, data in PROTOCOLE_BARLOW.items():
    
    is_accessible = code_module in modules_debloques
    
    if is_accessible:
        with st.expander(f"✅ {data['titre']}", expanded=False):
            st.info(data['description'])
            
            # 1. LES DOCUMENTS & AUDIOS
            st.markdown("#### 📥 Mes Ressources")
            for doc in data.get('fichiers_patient', []):
                col_icon, col_btn = st.columns([1, 5])
                
                # Gestion AUDIO (MP3)
                if doc.get('type') == 'audio':
                    with col_icon: st.write("🎧")
                    with col_btn:
                        st.write(f"**{doc['nom']}**")
                        chemin = doc.get('fichier')
                        if chemin and os.path.exists(chemin):
                            st.audio(chemin, format='audio/mp3')
                        else:
                            st.error(f"Fichier audio manquant : {chemin}")
                
                # Gestion PDF
                else:
                    with col_icon: st.write("📄")
                    with col_btn:
                        st.write(f"**{doc['nom']}**")
                        chemin = doc.get('fichier')
                        if chemin and os.path.exists(chemin):
                            with open(chemin, "rb") as f:
                                st.download_button("Télécharger", f, file_name=os.path.basename(chemin), key=f"dl_{doc['nom']}")
                        else:
                            st.error(f"Fichier manquant : {chemin}")

            st.divider()
            
            # 2. LES DEVOIRS & UPLOAD PHOTO (NOUVEAU !)
            if data.get('devoirs_patient'):
                st.markdown("#### 🏠 Mes Devoirs")
                for dev in data['devoirs_patient']:
                    st.write(f"- {dev}")
                
                # ZONE DE RENDU D'EXERCICE
                st.write("")
                st.caption("📷 Vous avez rempli une fiche papier ? Prenez-la en photo pour l'envoyer à votre thérapeute.")
                
                with st.popover("📸 Envoyer mon exercice"):
                    photo = st.camera_input(f"Photo exercice - {data['titre']}")
                    if photo:
                        # Simulation d'envoi (Pour le prototype)
                        st.success("Photo envoyée au thérapeute ! (Simulation)")
                        # Pour aller plus loin : il faudrait sauvegarder l'image dans un dossier 'uploads/{user_id}/'
    
    else:
        # Module verrouillé
        with st.container(border=True):
            st.write(f"🔒 **{data['titre']}**")
            st.caption("Ce module sera débloqué prochainement par votre thérapeute.")