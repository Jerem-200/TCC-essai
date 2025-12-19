import streamlit as st
import os
from protocole_config import PROTOCOLE_BARLOW
from protocole_config import PROTOCOLE_BARLOW, QUESTIONS_HEBDO # <--- Import modifié
from connect_db import load_data, sauvegarder_reponse_hebdo #


# Import sécurisé
try:
    from streamlit_app import charger_progression, charger_etat_devoirs
except ImportError:
    # Fallback si l'import direct échoue (copie de sécurité)
    def charger_progression(uid): 
        try:
            from connect_db import load_data
            import pandas as pd
            data = load_data("Progression")
            if data:
                df = pd.DataFrame(data)
                row = df[df["Patient"] == uid]
                if not row.empty:
                    return [x.strip() for x in str(row.iloc[0]["Modules_Actifs"]).split(",") if x.strip()]
        except: pass
        return ["module0"]
        
    def charger_etat_devoirs(uid): return {}

st.set_page_config(page_title="Mon Parcours", page_icon="🗺️")

if "authentifie" not in st.session_state or not st.session_state.authentifie:
    st.warning("🔒 Veuillez vous connecter.")
    st.stop()

# --- FORCER LE CHARGEMENT DES DONNÉES FRAÎCHES ---
current_user = st.session_state.get("user_id", "")
modules_debloques = charger_progression(current_user) # Charge depuis la DB
devoirs_exclus = charger_etat_devoirs(current_user)

st.title("🗺️ Mon Parcours de Soin")

# --- BOUCLE MODULES ---
for code_mod, data in PROTOCOLE_BARLOW.items():
    
    # Vérification stricte si le module est dans la liste chargée
    if code_mod in modules_debloques:
        
        # Par défaut, on ferme tout, sauf le dernier débloqué éventuellement
        with st.expander(f"✅ {data['titre']}", expanded=False):
            
            tab_proc, tab_docs = st.tabs(["📖 Ma Séance", "📂 Documents"])
            
            # ONGLET 1 : DÉROULÉ SIMPLIFIÉ
            with tab_proc:
                st.info(f"**Objectifs :** {data['objectifs']}")
                
                # Tâches à domicile (Filtrées)
                st.markdown("##### 🏠 À faire pour la prochaine fois")
                exclus_ici = devoirs_exclus.get(code_mod, [])
                a_faire = False
                
                if data['taches_domicile']:
                    for j, dev in enumerate(data['taches_domicile']):
                        if j not in exclus_ici:
                            a_faire = True
                            st.write(f"👉 **{dev['titre']}**")
                            if dev.get('pdf') and os.path.exists(dev['pdf']):
                                with open(dev['pdf'], "rb") as f:
                                    st.download_button("Télécharger", f, file_name=os.path.basename(dev['pdf']), key=f"dl_dev_{code_mod}_{j}")
                
                if not a_faire:
                    st.success("🎉 Aucun devoir spécifique.")
                else:
                    st.write("")
                    with st.expander("📸 Envoyer mon travail"):
                        st.camera_input("Prendre une photo", key=f"cam_{code_mod}")

            # ONGLET 2 : TOUS LES DOCS (Liste plate)
            with tab_docs:
                st.write("Tous les fichiers du module :")
                if 'pdfs_module' in data and data['pdfs_module']:
                    for path in data['pdfs_module']:
                        name = os.path.basename(path)
                        if os.path.exists(path):
                            with open(path, "rb") as f:
                                st.download_button(f"📥 {name}", f, file_name=name, key=f"dl_pat_all_{code_mod}_{name}")
                else:
                    st.info("Aucun document.")

    else:
        with st.container(border=True):
            st.write(f"🔒 **{data['titre']}**")
            st.caption("Verrouillé par votre thérapeute.")