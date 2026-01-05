import streamlit as st
import time

st.set_page_config(page_title="Relaxation", page_icon="🧘")

# ==============================================================================
# 0. SÉCURITÉ
# ==============================================================================
if "authentifie" not in st.session_state or not st.session_state.authentifie:
    st.warning("🔒 Accès restreint.")
    st.page_link("streamlit_app.py", label="Retourner à l'accueil", icon="🏠")
    st.stop()



# ==============================================================================
# CONTENU
# ==============================================================================
st.title("🧘 Espace Relaxation")
st.caption("Prenez un moment pour faire redescendre la pression.")

tab1, tab2 = st.tabs(["🌬️ Respiration Carrée", "💪 Jacobson (Musculaire)"])

# --- RESPIRATION CARRÉE ---
with tab1:
    st.header("La Respiration Carrée")
    st.info("Technique simple pour calmer une anxiété soudaine ou une attaque de panique.")
    
    st.markdown("""
    1. **Inspirez** par le nez pendant 4 secondes.
    2. **Bloquez** votre souffle (poumons pleins) pendant 4 secondes.
    3. **Expirez** par la bouche pendant 4 secondes.
    4. **Bloquez** votre souffle (poumons vides) pendant 4 secondes.
    """)
    
    if st.button("Lancer le guide visuel (1 min)", type="primary"):
        barre = st.progress(0)
        status = st.empty()
        
        cycles = 4 # 4 cycles de 16 secondes = 64 secondes
        
        for i in range(cycles):
            # 1. INSPIRATION
            status.markdown("### 😤 INSPIREZ... (4s)")
            for x in range(100):
                time.sleep(0.04)
                barre.progress(x + 1)
            
            # 2. RETENTION
            status.markdown("### 😶 BLOQUEZ (4s)")
            time.sleep(4)
            
            # 3. EXPIRATION
            status.markdown("### 😮 EXPIREZ... (4s)")
            for x in range(100, 0, -1):
                time.sleep(0.04)
                barre.progress(x - 1)
                
            # 4. RETENTION
            status.markdown("### 😶 BLOQUEZ (4s)")
            time.sleep(4)
            
        status.success("Exercice terminé. Comment vous sentez-vous ?")

# --- JACOBSON ---
with tab2:
    st.header("Relaxation Musculaire Progressive")
    st.write("Le principe : contracter fort un muscle, puis relâcher brusquement pour sentir la détente.")
    
    with st.expander("Voir le protocole rapide"):
        st.markdown("""
        **Répétez pour chaque zone : Contractez 5s, Relâchez 10s.**
        
        1. **Mains :** Serrez les poings très fort.
        2. **Bras :** Pliez les bras ("faire ses muscles").
        3. **Épaules :** Haussez les épaules vers les oreilles.
        4. **Visage :** Grimacez (froncez sourcils, serrez dents).
        5. **Ventre :** Contractez les abdominaux.
        6. **Jambes :** Tendez les jambes et pointez les pieds.
        """)
    
    st.info("💡 Astuce : Pratiquez cet exercice le soir pour faciliter l'endormissement.")

st.divider()
st.set_page_config(page_title="Relaxation", page_icon="📉")
if st.button("⬅️ Retour au tableau de bord"):
    # On dit au menu principal de rouvrir l'onglet "Échelles"
    st.session_state["target_tab"] = "🛠️ Outils & Exos"
    st.switch_page("streamlit_app.py")