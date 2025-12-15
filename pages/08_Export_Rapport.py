import streamlit as st
import pandas as pd
from utils_pdf import generer_pdf 
from datetime import datetime

st.set_page_config(page_title="Export Rapport", page_icon="📩")

# ==============================================================================
# 0. SÉCURITÉ
# ==============================================================================
if "authentifie" not in st.session_state or not st.session_state.authentifie:
    st.warning("🔒 Accès restreint.")
    st.page_link("streamlit_app.py", label="Accueil", icon="🏠")
    st.stop()

CURRENT_USER_ID = st.session_state.get("user_id", "")
if not CURRENT_USER_ID:
    st.error("Erreur d'identité. Veuillez vous reconnecter.")
    st.stop()

st.title("📩 Exporter mon Dossier")
st.info("Générez un rapport PDF complet incluant toutes vos échelles et agendas.")

# ==============================================================================
# 1. CHARGEMENT CENTRALISÉ DES DONNÉES (CLOUD)
# ==============================================================================
# Fonction utilitaire locale pour charger proprement
def load_safe(key):
    try:
        from connect_db import load_data
        data = load_data(key)
        if data:
            df = pd.DataFrame(data)
            if "Patient" in df.columns:
                return df[df["Patient"] == CURRENT_USER_ID]
    except: pass
    return pd.DataFrame() # Retourne vide si échec

with st.spinner("Récupération de vos données..."):
    # On charge tout dans un dictionnaire
    data_export = {
        "beck": load_safe("Beck"),
        "bdi": load_safe("Echelles_BDI"), # Ou "BDI" selon votre nom exact
        "phq9": load_safe("PHQ9"),
        "gad7": load_safe("GAD7"),
        "who5": load_safe("WHO5"),
        "sommeil": load_safe("Sommeil"),
        "activites": load_safe("Activites"),
        "problemes": load_safe("Resolution_Probleme")
    }

# ==============================================================================
# 2. APERÇU DES DONNÉES DISPONIBLES
# ==============================================================================
st.subheader("📊 Contenu du rapport")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Exercices Beck", len(data_export["beck"]))
c2.metric("Nuits (Sommeil)", len(data_export["sommeil"]))
c3.metric("Activités", len(data_export["activites"]))
c4.metric("Tests Psy", len(data_export["phq9"]) + len(data_export["gad7"]))

st.divider()

# ==============================================================================
# 3. GÉNÉRATION DU PDF
# ==============================================================================
if "pdf_bytes" not in st.session_state:
    st.session_state.pdf_bytes = None

if st.button("📄 Générer le Rapport PDF Complet", type="primary"):
    try:
        # On passe le dictionnaire complet au générateur
        st.session_state.pdf_bytes = generer_pdf(data_export, CURRENT_USER_ID)
        st.rerun()
    except Exception as e:
        st.error(f"Erreur lors de la création du PDF : {e}")

# ==============================================================================
# 4. TÉLÉCHARGEMENT & ENVOI
# ==============================================================================
if st.session_state.pdf_bytes:
    
    st.success("✅ Le document est prêt !")
    
    col_gauche, col_droite = st.columns(2)
    
    # TÉLÉCHARGEMENT
    with col_gauche:
        st.markdown("#### 1. Télécharger")
        st.download_button(
            label="📥 Télécharger le PDF sur mon appareil",
            data=st.session_state.pdf_bytes,
            file_name=f"Rapport_TCC_{CURRENT_USER_ID}_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    # ENVOI MAIL
    with col_droite:
        st.markdown("#### 2. Envoyer par mail")
        
        with st.form("email_form"):
            email_psy = st.text_input("Email du destinataire :", placeholder="psy@cabinet.com")
            valider = st.form_submit_button("Préparer l'email")
        
        if valider and email_psy:
            sujet = f"Suivi TCC - Dossier {CURRENT_USER_ID}"
            corps = "Bonjour,\n\nVeuillez trouver ci-joint mon rapport d'avancement (exercices, sommeil et échelles).\n\nCordialement."
            mailto_link = f"mailto:{email_psy}?subject={sujet}&body={corps}".replace("\n", "%0D%0A")
            
            st.markdown(f"""
            <a href="{mailto_link}" target="_blank" style="text-decoration:none;">
                <button style="width:100%; padding:0.5rem; background-color:#FF4B4B; color:white; border:none; border-radius:5px; cursor:pointer;">
                    📧 Ouvrir ma messagerie avec {email_psy}
                </button>
            </a>
            """, unsafe_allow_html=True)
            
            st.caption("⚠️ Important : Une fois votre messagerie ouverte, n'oubliez pas de **glisser le fichier PDF** que vous venez de télécharger en pièce jointe !")

    st.divider()
    if st.button("🔄 Réinitialiser"):
        st.session_state.pdf_bytes = None
        st.rerun()

st.divider()
st.page_link("streamlit_app.py", label="Retour à l'accueil", icon="🏠")