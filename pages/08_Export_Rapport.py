import streamlit as st
import pandas as pd
from datetime import datetime
from utils_pdf import generer_pdf
import concurrent.futures # C'est le module magique pour la vitesse

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
# 1. CHARGEMENT ULTRA-RAPIDE (PARALLÉLISÉ)
# ==============================================================================

# Fonction de chargement unitaire
def fetch_data(key):
    try:
        from connect_db import load_data
        data = load_data(key)
        if data:
            df = pd.DataFrame(data)
            if "Patient" in df.columns:
                # On retourne le dataframe filtré directement
                return df[df["Patient"] == CURRENT_USER_ID]
    except: pass
    return pd.DataFrame()

# Dictionnaire des tables à charger
TABLES_A_CHARGER = {
    "beck": "Beck",
    "bdi": "Echelles_BDI", # Vérifiez si c'est "BDI" ou "Echelles_BDI" dans votre GSheet
    "phq9": "PHQ9",
    "gad7": "GAD7",
    "isi": "ISI",
    "peg": "PEG",
    "who5": "WHO5",
    "wsas": "WSAS",
    "sommeil": "Sommeil",
    "activites": "Activites",
    "problemes": "Resolution_Probleme"
}

data_export = {}

# C'est ici que la magie opère : On lance tout en même temps !
with st.spinner("🚀 Récupération accélérée de vos données..."):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # On prépare les futures (les tâches)
        future_to_key = {executor.submit(fetch_data, db_key): dict_key for dict_key, db_key in TABLES_A_CHARGER.items()}
        
        # On récolte les résultats au fur et à mesure qu'ils arrivent
        for future in concurrent.futures.as_completed(future_to_key):
            key = future_to_key[future]
            try:
                data_export[key] = future.result()
            except Exception:
                data_export[key] = pd.DataFrame()

# ==============================================================================
# 2. APERÇU DES DONNÉES DISPONIBLES
# ==============================================================================
st.subheader("📊 Contenu du rapport")

# Petit calcul rapide pour l'affichage
nb_tests = len(data_export["phq9"]) + len(data_export["gad7"]) + len(data_export["who5"]) + len(data_export["isi"])
nb_agendas = len(data_export["sommeil"]) + len(data_export["activites"])

c1, c2, c3, c4 = st.columns(4)
c1.metric("Exercices Beck", len(data_export["beck"]))
c2.metric("Tests Psy", nb_tests)
c3.metric("Agendas (Jours)", nb_agendas)
c4.metric("Problèmes", len(data_export["problemes"]))

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
            label="📥 Télécharger le PDF",
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