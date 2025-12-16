import streamlit as st
import os
from protocole_config import PROTOCOLE_BARLOW

st.set_page_config(page_title="Mon Parcours", page_icon="🗺️")

# --- SÉCURITÉ (Standard) ---
if "authentifie" not in st.session_state or not st.session_state.authentifie:
    st.warning("🔒 Veuillez vous connecter.")
    st.stop()

st.title("🗺️ Mon Parcours de Soin")
st.caption("Protocole Unifié (Barlow) - Suivez les étapes pas à pas.")

# Simulation de progression (À connecter plus tard à votre base de données)
# Pour l'instant, on dit que tout est ouvert pour tester
PROGRESSION_PATIENT = ["intro", "module1", "module2", "module4"] 

# --- CALCUL SÉCURISÉ DE LA PROGRESSION ---
nb_total_modules = len(PROTOCOLE_BARLOW)
nb_faits = len(PROGRESSION_PATIENT)

if nb_total_modules > 0:
    progression = nb_faits / nb_total_modules
else:
    progression = 0.0

# Sécurité : On s'assure que le chiffre ne dépasse jamais 1.0 (100%)
if progression > 1.0:
    progression = 1.0

st.progress(progression, text=f"Progression globale : {int(progression*100)}%")

# --- BOUCLE D'AFFICHAGE DES MODULES ---
for key, module in PROTOCOLE_BARLOW.items():
    
    # 1. Est-ce que ce module est débloqué ?
    is_unlocked = key in PROGRESSION_PATIENT
    
    # Visuel de l'entête (Vert si fait/en cours, Gris si bloqué)
    icon_state = "✅" if is_unlocked else "🔒"
    
    with st.expander(f"{icon_state} {module['titre']}", expanded=is_unlocked):
        if is_unlocked:
            st.write(f"*{module['description']}*")
            st.write("") # Espace
            
            # On liste les étapes du module
            for etape in module['etapes']:
                c1, c2 = st.columns([1, 4])
                
                # A. Si c'est un PDF
                if etape['type'] == 'pdf':
                    with c1: st.write("📄")
                    with c2: 
                        st.write(f"**{etape['nom']}**")
                        
                        # --- VRAI CHARGEMENT DU FICHIER ---
                        chemin_fichier = etape.get('fichier')
                        
                        # On vérifie si le fichier existe vraiment pour éviter un crash
                        if chemin_fichier and os.path.exists(chemin_fichier):
                            with open(chemin_fichier, "rb") as pdf_file:
                                btn = st.download_button(
                                    label="📥 Télécharger la fiche",
                                    data=pdf_file,
                                    file_name=os.path.basename(chemin_fichier),
                                    mime="application/pdf",
                                    key=f"btn_{etape['nom']}"
                                )
                        else:
                            st.error(f"⚠️ Fichier introuvable : {chemin_fichier}")

                # B. Si c'est un OUTIL (Lien vers vos pages)
                elif etape['type'] == 'outil':
                    with c1: st.write(etape['icon'])
                    with c2:
                        st.page_link(etape['lien'], label=f"Ouvrir l'outil : {etape['nom']}")
                
                # C. Si c'est du TEXTE (Psychoéducation directe)
                elif etape['type'] == 'text':
                    with c1: st.write("📖")
                    with c2:
                        st.info(etape['contenu'])
                
                st.divider()
        else:
            st.warning("Ce module est verrouillé pour le moment. Concentrez-vous sur les étapes précédentes.")