import streamlit as st
import pandas as pd
from utils_pdf import generer_pdf 

st.set_page_config(page_title="Export Rapport", page_icon="📩")

# --- VIGILE DE SÉCURITÉ SIMPLIFIÉ ---
if "authentifie" not in st.session_state or not st.session_state.authentifie:
    st.warning("🔒 Accès restreint. Veuillez entrer votre Code Patient sur l'accueil.")
    st.page_link("streamlit_app.py", label="Retourner à l'accueil pour se connecter", icon="🏠")
    st.stop() # Arrête le chargement du reste de la page

# Récupération du code patient pour les sauvegardes
patient_id = st.session_state.patient_id

st.title("📩 Envoyer mon rapport")
st.info("Générez un PDF de vos progrès pour l'envoyer à votre thérapeute.")

# --- 1. RÉCUPÉRATION DES DONNÉES ---
df_beck = st.session_state.get("data_beck", pd.DataFrame())
df_bdi = st.session_state.get("data_echelles", pd.DataFrame())
df_act = st.session_state.get("data_activites", pd.DataFrame())
df_prob = st.session_state.get("data_problemes", pd.DataFrame())
patient = st.session_state.get("patient_id", "Patient")

# Stats
c1, c2, c3, c4 = st.columns(4)
c1.metric("Beck", len(df_beck))
c2.metric("BDI", len(df_bdi))
c3.metric("Activités", len(df_act))
c4.metric("Problèmes", len(df_prob))

st.divider()

# --- GESTION DE LA MÉMOIRE DU PDF ---
if "pdf_bytes" not in st.session_state:
    st.session_state.pdf_bytes = None

# --- 2. BOUTON DE GÉNÉRATION ---
if st.button("📄 Générer le Rapport PDF"):
    try:
        st.session_state.pdf_bytes = generer_pdf(df_beck, df_bdi, df_act, df_prob, patient)
        st.rerun()
    except Exception as e:
        st.error(f"Erreur : {e}")

# --- 3. AFFICHAGE ET ENVOI ---
if st.session_state.pdf_bytes:
    
    st.success("Le PDF est prêt ! Suivez les étapes :")
    
    col_gauche, col_droite = st.columns(2)
    
    # ÉTAPE A : TÉLÉCHARGEMENT
    with col_gauche:
        st.markdown("#### Étape 1 : Télécharger")
        st.download_button(
            label="📥 Télécharger le PDF",
            data=st.session_state.pdf_bytes,
            file_name=f"Rapport_TCC_{patient}.pdf",
            mime="application/pdf"
        )

    # ÉTAPE B : ENVOI MAIL (MODIFIÉ AVEC VALIDATION)
    with col_droite:
        st.markdown("#### Étape 2 : Envoyer")
        
        # --- NOUVEAU : FORMULAIRE DE VALIDATION ---
        with st.form("email_form"):
            email_psy = st.text_input("Adresse email du thérapeute :", placeholder="psy@cabinet.com")
            # Ce bouton sert uniquement à valider la saisie
            submit_email = st.form_submit_button("Valider l'adresse")
        
        # Si le bouton du formulaire a été cliqué ET qu'il y a un email
        if submit_email and email_psy:
            sujet = f"Suivi TCC - {patient}"
            corps = "Bonjour,\n\nVoici mon rapport d'exercices TCC de la période (voir pièce jointe).\n\nCordialement."
            # On remplace les sauts de ligne pour le lien mailto
            mailto_link = f"mailto:{email_psy}?subject={sujet}&body={corps}".replace("\n", "%0D%0A")
            
            st.success(f"Adresse validée : {email_psy}")
            
            # Le bouton final qui ouvre la messagerie
            st.link_button("📧 Ouvrir ma messagerie maintenant", mailto_link, type="primary")
            
            st.caption("⚠️ N'oubliez pas d'ajouter le fichier PDF en pièce jointe dans votre mail !")
            
            # Solution de secours
            with st.expander("Le bouton ne marche pas ?"):
                st.write("Copiez l'adresse :")
                st.code(email_psy)
        
        elif submit_email and not email_psy:
            st.warning("Veuillez entrer une adresse email avant de valider.")
            
    st.divider()
    if st.button("🔄 Effacer et recommencer"):
        st.session_state.pdf_bytes = None
        st.rerun()

st.divider()
st.page_link("streamlit_app.py", label="Retour à l'accueil", icon="🏠")