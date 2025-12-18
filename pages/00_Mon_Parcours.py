import streamlit as st
import os
from protocole_config import PROTOCOLE_BARLOW

# Import sécurisé
try:
    from streamlit_app import charger_progression, charger_etat_devoirs
except ImportError:
    def charger_progression(uid): return ["module0"]
    def charger_etat_devoirs(uid): return {}

st.set_page_config(page_title="Mon Parcours", page_icon="🗺️")

if "authentifie" not in st.session_state or not st.session_state.authentifie:
    st.warning("🔒 Veuillez vous connecter.")
    st.stop()

current_user = st.session_state.get("user_id", "")
modules_debloques = charger_progression(current_user)
devoirs_exclus = charger_etat_devoirs(current_user) # {module: [indices_exclus]}

st.title("🗺️ Mon Parcours de Soin")

# --- FONCTION HELPER POUR TÉLÉCHARGEMENT ---
def afficher_doc(titre, chemin, key_suffix):
    if chemin and os.path.exists(chemin):
        nom = os.path.basename(chemin)
        col_i, col_b = st.columns([0.1, 0.9])
        with col_i:
            if chemin.endswith(".mp3"): st.write("🎧")
            else: st.write("📄")
        with col_b:
            with open(chemin, "rb") as f:
                st.download_button(f"{titre}", f, file_name=nom, key=f"dl_{key_suffix}")
    elif chemin:
        st.caption(f"❌ Document indisponible : {titre}")

# --- BOUCLE MODULES ---
for code_mod, data in PROTOCOLE_BARLOW.items():
    
    if code_mod in modules_debloques:
        with st.expander(f"✅ {data['titre']}", expanded=False):
            
            # STRUCTURE MIROIR : 2 ONGLETS
            tab_proc, tab_docs = st.tabs(["📖 Ma Séance", "📂 Tous mes Documents"])
            
            # ONGLET 1 : DÉROULÉ
            with tab_proc:
                st.info(f"**Objectifs :** {data['objectifs']}")
                
                # 1. EXAMEN (Rappel)
                if data['examen_devoirs']:
                    st.markdown("##### 🔍 Retour sur vos tâches")
                    for item in data['examen_devoirs']:
                        afficher_doc(item['titre'], item.get('pdf'), f"exam_{code_mod}_{item['titre']}")

                st.write("---")

                # 2. CONTENU SÉANCE (Pour info)
                st.markdown("##### 📝 Vu en séance")
                for etape in data['etapes_seance']:
                    st.write(f"• {etape['titre']}")
                    # On affiche le doc associé directement ici si pertinent
                    if etape.get('pdf'):
                        afficher_doc("Télécharger le document", etape['pdf'], f"step_{code_mod}_{etape['titre']}")
                    # Gestion des multiples
                    if etape.get('pdf_2'): afficher_doc("Document complémentaire", etape['pdf_2'], f"step2_{code_mod}_{etape['titre']}")
                    if etape.get('extras'):
                        for ex in etape['extras']: afficher_doc(os.path.basename(ex), ex, f"extra_{code_mod}_{ex}")

                st.write("---")

                # 3. MES DEVOIRS (Filtrés !)
                st.markdown("##### 🏠 À faire pour la prochaine fois")
                
                exclus_ici = devoirs_exclus.get(code_mod, [])
                a_faire = False
                
                for j, dev in enumerate(data['taches_domicile']):
                    if j not in exclus_ici: # Si le thérapeute ne l'a pas décoché
                        a_faire = True
                        st.write(f"👉 **{dev['titre']}**")
                        if dev.get('pdf'):
                            afficher_doc("Télécharger l'exercice", dev['pdf'], f"dev_{code_mod}_{j}")
                
                if not a_faire:
                    st.success("🎉 Aucun devoir spécifique pour ce module.")
                else:
                    st.write("")
                    with st.expander("📸 Envoyer mon travail (Photo)"):
                        st.camera_input("Prendre une photo", key=f"cam_{code_mod}")

            # ONGLET 2 : TOUS LES DOCS (Bibliothèque)
            with tab_docs:
                st.write("Retrouvez ici tous les fichiers de ce module.")
                # On rassemble tout
                tous = []
                # Examen
                for x in data['examen_devoirs']: tous.append((x['titre'], x.get('pdf')))
                # Séance
                for s in data['etapes_seance']: 
                    tous.append((s['titre'], s.get('pdf')))
                    if s.get('pdf_2'): tous.append((s['titre'] + " (2)", s.get('pdf_2')))
                    if s.get('extras'): 
                        for ex in s['extras']: tous.append(("Annexe", ex))
                # Devoirs (Même ceux décochés, car c'est la bibliothèque)
                for d in data['taches_domicile']: tous.append((f"Devoir: {d['titre']}", d.get('pdf')))
                
                # Affichage unique
                vus = set()
                for titre, path in tous:
                    if path and path not in vus:
                        afficher_doc(titre, path, f"all_{code_mod}_{os.path.basename(path)}")
                        vus.add(path)

    else:
        with st.container(border=True):
            st.write(f"🔒 **{data['titre']}** (Verrouillé)")