import streamlit as st

st.set_page_config(page_title="Mon Compagnon TCC", page_icon="🧠", layout="wide")

# --- AUTHENTIFICATION ---
if "authentifie" not in st.session_state:
    st.session_state.authentifie = False

def verifier_mot_de_passe():
    if st.session_state.password_input == "TCC2025": 
        st.session_state.authentifie = True
    else:
        st.error("Mot de passe incorrect")

if not st.session_state.authentifie:
    st.title("🔒 Espace Patient")
    st.text_input("Mot de passe", type="password", key="password_input", on_change=verifier_mot_de_passe)
    st.stop()

# --- ACCUEIL ---
st.title("🧠 Mon Compagnon TCC")
st.subheader("Tableau de bord")
st.divider()

# --- LIGNE 1 ---
c1, c2 = st.columns(2)
with c1:
    st.info("### 🧩 Restructuration")
    st.write("Colonnes de Beck")
    if st.button("Lancer l'exercice", key="btn_beck"):
        st.switch_page("pages/01_Colonnes_Beck.py")

with c2:
    st.info("### 📊 Échelles (BDI)")
    st.write("Auto-évaluation")
    if st.button("Faire le test", key="btn_bdi"):
        st.switch_page("pages/02_Echelles_BDI.py")

st.divider()

# --- LIGNE 2 (3 colonnes) ---
c3, c4, c5 = st.columns(3)

with c3:
    st.warning("### 📝 Activités")
    st.write("Registre journalier")
    if st.button("Ouvrir le registre", key="btn_act"):
        st.switch_page("pages/05_Registre_Activites.py")

with c4:
    st.error("### 💡 Problèmes")
    st.write("Résolution de problèmes")
    if st.button("Trouver une solution", key="btn_prob"):
        st.switch_page("pages/06_Resolution_Probleme.py")

with c5:
    st.success("### 📜 Historique")
    st.write("Vos progrès")
    if st.button("Voir mon suivi", key="btn_hist"):
        st.switch_page("pages/04_Historique.py")

st.divider()

with st.expander("📚 Ressources"):
    st.write("Fiches et documents")
    if st.button("Accéder aux fiches", key="btn_res"):
        st.switch_page("pages/03_Ressources.py")