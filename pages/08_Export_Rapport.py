import streamlit as st
import pandas as pd
from utils_pdf import generer_pdf # Assurez-vous d'avoir créé le fichier utils_pdf.py

st.set_page_config(page_title="Export Rapport", page_icon="📩")

# --- VIGILE DE SÉCURITÉ ---
if "authentifie" not in st.session_state or not st.session_state.authentifie:
    st.warning("⛔ Veuillez vous connecter sur la page d'accueil.")
    st.switch_page("streamlit_app.py")
    st.stop()

st.title("📩 Envoyer mon rapport")
st.info("Générez un PDF de vos progrès pour l'envoyer à votre thérapeute.")

# --- 1. RÉCUPÉRATION DES DONNÉES ---
df_beck = st.session_state.get("data_beck", pd.DataFrame())
df_bdi = st.session_state.get("data_echelles", pd.DataFrame())
df_act = st.session_state.get("data_activites", pd.DataFrame())
df_prob = st.session_state.get("data_problemes", pd.DataFrame())
patient = st.session_state.get("patient_id", "Patient")

# Petit résumé visuel
c1, c2, c3, c4 = st.columns(4)
c1.metric("Fiches Beck", len(df_beck))
c2.metric("Scores BDI", len(df_bdi))
c3.metric("Activités", len(df_act))
c4.metric("Problèmes", len(df_prob))

st.divider()

# --- 2. GÉNÉRATION DU PDF ---
if st.button("📄 Générer le Rapport PDF"):
    try:
        # On fabrique le PDF
        pdf_bytes = generer_pdf(df_beck, df_bdi, df_act, df_prob, patient)
        
        # Zone de succès
        st.success("Le PDF est prêt ! Suivez les deux étapes ci-dessous :")
        
        col_gauche, col_droite = st.columns(2)
        
        # ÉTAPE A : TÉLÉCHARGEMENT
        with col_gauche:
            st.markdown("#### Étape 1 : Télécharger")
            st.download_button(
                label="📥 Télécharger le PDF sur mon appareil",
                data=pdf_bytes,
                file_name=f"Rapport_TCC_{patient}.pdf",
                mime="application/pdf"
            )

        # ÉTAPE B : ENVOI MAIL
        with col_droite:
            st.markdown("#### Étape 2 : Envoyer")
            email_psy = st.text_input("Adresse email du thérapeute :", placeholder="psy@cabinet.com")
            
            if email_psy:
                # Création du lien mailto
                sujet = f"Suivi TCC - {patient}"
                corps = "Bonjour,\n\nVoici mon rapport d'exercices TCC de la période (voir pièce jointe).\n\nCordialement."
                mailto_link = f"mailto:{email_psy}?subject={sujet}&body={corps}"
                
                # Le Bouton Rouge en HTML pour ouvrir la messagerie
                st.markdown(f"""
                <a href="{mailto_link}" target="_blank" style="text-decoration:none;">
                    <button style="
                        background-color: #FF4B4B;
                        color: white;
                        padding: 10px 20px;
                        border: none;
                        border-radius: 5px;
                        cursor: pointer;
                        font-weight: bold;
                        width: 100%;">
                        📧 Ouvrir ma messagerie avec le mail prêt
                    </button>
                </a>
                """, unsafe_allow_html=True)
                
                st.caption("⚠️ N'oubliez pas d'ajouter le fichier PDF en pièce jointe avant d'envoyer !")
            else:
                st.info("👆 Entrez l'email pour voir le bouton d'envoi.")

    except Exception as e:
        st.error(f"Erreur lors de la création du PDF : {e}")

st.divider()
st.page_link("streamlit_app.py", label="Retour à l'accueil", icon="🏠")