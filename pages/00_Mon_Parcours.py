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
        # On utilise le Titre du module
        with st.expander(f"✅ {data['titre']}", expanded=False):
            
            # 1. DESCRIPTION / OBJECTIFS
            st.info(data['objectifs'])
            
            # 2. RESSOURCES DE LA SÉANCE (Documents liés aux étapes)
            docs_seance = [e for e in data['etapes_contenu'] if e.get('pdf')]
            
            if docs_seance:
                st.markdown("#### 📥 Documents de la séance")
                for doc in docs_seance:
                    col_icon, col_btn = st.columns([0.5, 4])
                    with col_icon: st.write("📄")
                    with col_btn:
                        nom_doc = os.path.basename(doc['pdf'])
                        st.write(f"**{doc['titre']}**")
                        if os.path.exists(doc['pdf']):
                            with open(doc['pdf'], "rb") as f:
                                st.download_button("Télécharger", f, file_name=nom_doc, key=f"dl_pat_step_{code_module}_{nom_doc}")
                        else:
                            st.caption(f"Fichier indisponible")
                st.divider()

            # 3. MES DEVOIRS (Tâches à domicile)
            if data.get('devoirs'):
                st.markdown("#### 🏠 Mes Devoirs")
                
                for i, devoir in enumerate(data['devoirs']):
                    c_check, c_info = st.columns([0.5, 4])
                    with c_check:
                        st.checkbox("", key=f"pat_check_{code_module}_{i}")
                    with c_info:
                        st.write(f"**{devoir['tache']}**")
                        # Si le devoir a un PDF associé
                        if devoir.get('pdf'):
                            pdf_path = devoir['pdf']
                            nom_pdf = os.path.basename(pdf_path)
                            if os.path.exists(pdf_path):
                                with open(pdf_path, "rb") as f:
                                    st.download_button(f"📥 {nom_pdf}", f, file_name=nom_pdf, key=f"dl_pat_dev_{code_module}_{i}")
                
                # ZONE DE RENDU D'EXERCICE (PHOTO)
                st.write("")
                with st.expander("📸 Envoyer une photo de mon exercice"):
                    st.caption("Vous avez rempli une fiche papier ? Prenez-la en photo pour votre thérapeute.")
                    photo = st.camera_input(f"Photo exercice - {data['titre']}")
                    if photo:
                        st.success("Photo envoyée ! (Simulation)")
    
    else:
        # Module verrouillé
        with st.container(border=True):
            st.write(f"🔒 **{data['titre']}**")
            st.caption("Ce module sera débloqué prochainement.")