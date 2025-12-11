import streamlit as st

st.set_page_config(page_title="Espace Relaxation", page_icon="🧘")

# --- VIGILE DE SÉCURITÉ SIMPLIFIÉ ---
if "authentifie" not in st.session_state or not st.session_state.authentifie:
    st.warning("🔒 Accès restreint. Veuillez entrer votre Code Patient sur l'accueil.")
    st.page_link("streamlit_app.py", label="Retourner à l'accueil pour se connecter", icon="🏠")
    st.stop() # Arrête le chargement du reste de la page

# Récupération du code patient pour les sauvegardes
patient_id = st.session_state.patient_id

st.title("🧘 Espace de Relaxation")
st.info("Prenez un moment pour vous recentrer. Choisissez un exercice ci-dessous.")

# --- ONGLETS ---
tab1, tab2 = st.tabs(["🫁 Cohérence Cardiaque", "💪 Relaxation Musculaire"])

# --- COHÉRENCE CARDIAQUE ---
with tab1:
    st.header("Respiration guidée (5 min)")
    st.write("""
    **La cohérence cardiaque** permet de réduire le stress immédiatement en synchronisant votre respiration.
    
    1. Inspirez par le nez pendant 5 secondes.
    2. Expirez par la bouche pendant 5 secondes.
    3. Répétez.
    """)
    
    st.divider()
    
    # Vidéo Youtube intégrée (C'est souvent plus simple et fiable que des fichiers MP3 lourds)
    # Exemple : Une vidéo classique de cohérence cardiaque (boule qui monte et descend)
    st.video("https://www.youtube.com/watch?v=bM3mWlq4M8E")
    
    st.success("Astuce : Pratiquez cet exercice 3 fois par jour pour un effet durable sur l'anxiété.")

# --- RELAXATION DE JACOBSON ---
with tab2:
    st.header("Relaxation Progressive de Jacobson")
    st.write("""
    Cette technique consiste à contracter puis relâcher certains muscles pour sentir la différence entre tension et détente.
    """)
    
    with st.expander("📖 Lire les instructions avant de commencer"):
        st.write("""
        1. Installez-vous confortablement (assis ou allongé).
        2. Fermez les yeux.
        3. Nous allons parcourir le corps : mains, bras, épaules, visage...
        4. Contractez le muscle fort pendant 5 secondes.
        5. Relâchez brusquement et savourez la détente pendant 15 secondes.
        """)

    st.divider()
    
    st.write("🎧 **Séance Audio Guidée (10 min)**")
    # Exemple d'audio (ici un lien placeholder, vous pourrez mettre le vôtre)
    # Si vous avez votre propre MP3, glissez-le dans le dossier 'assets' et utilisez :
    # st.audio("assets/mon_audio_relaxation.mp3")
    
    # Ici j'utilise un exemple en ligne pour que ça marche tout de suite
    st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3", format="audio/mp3")
    
    st.info("Prenez le temps de 'revenir' doucement à la réalité après l'écoute.")

st.divider()
st.page_link("streamlit_app.py", label="Retour à l'accueil", icon="🏠")