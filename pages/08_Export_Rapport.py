import streamlit as st
import pandas as pd
from utils_pdf import generer_pdf # On importe notre moteur PDF

st.set_page_config(page_title="Export Rapport", page_icon="📩")

# --- VIGILE ---
if "authentifie" not in st.session_state or not st.session_state.authentifie:
    st.warning("⛔ Connectez-vous d'abord.")
    st.switch_page("streamlit_app.py")
    st.stop()

st.title("📩 Envoyer mon rapport")
st.write("Générez un document PDF récapitulatif de votre travail pour l'envoyer à votre thérapeute.")

# --- RÉCUPÉRATION DES DONNÉES ---
# On prend ce qui est en mémoire (ce que le patient a fait dans cette session ou ce qui a été chargé)
df_beck = st.session_state.get("data_beck", pd.DataFrame())
df_bdi = st.session_state.get("data_echelles", pd.DataFrame())
df_act = st.session_state.get("data_activites", pd.DataFrame())
df_prob = st.session_state.get("data_problemes", pd.DataFrame())
patient = st.session_state.get("patient_id", "Patient")

# Stats rapides
c1, c2, c3, c4 = st.columns(4)
c1.metric("Fiches Beck", len(df_beck))
c2.metric("Scores BDI", len(df_bdi))
c3.metric("Activités", len(df_act))
c4.metric("Problèmes", len(df_prob))

st.divider()

# --- GÉNÉRATION DU PDF ---
if st.button("📄 Générer le Rapport PDF"):
    try:
        # On appelle notre moteur
        pdf_bytes = generer_pdf(df_beck, df_bdi, df_act, df_prob, patient)
        
        # On affiche le bouton de téléchargement
        st.download_button(
            label="📥 Télécharger le Rapport (PDF)",
            data=pdf_bytes,
            file_name=f"Rapport_TCC_{patient}.pdf",
            mime="application/pdf"
        )
        
        st.success("Le PDF est prêt ! Téléchargez-le ci-dessus.")
        
        # --- PRÉPARATION DE L'EMAIL ---
        st.write("---")
        st.subheader("Envoyer par mail")
        email_psy = st.text_input("Email du thérapeute", placeholder="psy@exemple.com")
        
        if email_psy:
            # Lien mailto intelligent
            sujet = f"Rapport TCC - {patient}"
            corps = "Bonjour,\n\nVoici mon rapport d'exercices TCC de la période.\n\nCordialement."
            mailto_link = f"mailto:{email_psy}?subject={sujet}&body={corps}"
            
            st.markdown(f"""
            <a href="{mailto_link}" target="_blank" style="text-decoration:none;">
                <button style="background-color:#FF4B4B;color:white;padding:10px;border:none;border-radius:5px;cursor:pointer;">
                    📧 Ouvrir ma messagerie pour envoyer le PDF
                </button>
            </a>
            """, unsafe_allow_html=True)
            st.caption("1. Téléchargez le PDF (bouton blanc). 2. Cliquez sur le bouton rouge. 3. Ajoutez le PDF en pièce jointe.")
            
    except Exception as e:
        st.error(f"Erreur lors de la création du PDF : {e}")

st.divider()
st.page_link("streamlit_app.py", label="Retour à l'accueil", icon="🏠")