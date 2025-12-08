import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime

st.set_page_config(page_title="Agenda Consos", page_icon="🍷")

# --- VIGILE DE SÉCURITÉ ---
if "authentifie" not in st.session_state or not st.session_state.authentifie:
    st.warning("⛔ Veuillez vous connecter sur la page d'accueil.")
    st.switch_page("streamlit_app.py")
    st.stop()

st.title("🍷 Agenda des Envies & Consommations")
st.info("Notez vos envies (craving) et vos consommations pour identifier les déclencheurs.")

# --- 1. GESTION DES SUBSTANCES (MULTI-CIBLES) ---
if "liste_substances" not in st.session_state:
    st.session_state.liste_substances = []

# Initialisation des données locales
if "data_addictions" not in st.session_state:
    st.session_state.data_addictions = pd.DataFrame(columns=[
        "Date", "Heure", "Substance", "Type", "Intensité", "Pensées"
    ])

# Zone de sélection
col_info, col_sel = st.columns([2, 2])
with col_info:
    st.write("**De quoi voulez-vous faire le suivi ?**")

with col_sel:
    # Création
    with st.popover("➕ Nouvelle Substance/Comportement"):
        new_sub = st.text_input("Nom (ex: Alcool, Tabac, Jeux...)")
        if st.button("Créer") and new_sub:
            st.session_state.liste_substances.append(new_sub)
            st.rerun()

    # Sélection
    if st.session_state.liste_substances:
        substance_active = st.selectbox("Substance active :", st.session_state.liste_substances)
    else:
        st.warning("Ajoutez une substance ci-dessus pour commencer.")
        st.stop()

# --- ONGLETS ---
tab1, tab2 = st.tabs(["📝 Saisie (Journal)", "📊 Bilan & Historique"])

# ==============================================================================
# ONGLET 1 : SAISIE
# ==============================================================================
with tab1:
    st.header(f"Journal : {substance_active}")
    
    with st.form("form_addiction", clear_on_submit=True):
        c1, c2, c3 = st.columns([1, 1, 2])
        with c1:
            date_evt = st.date_input("Date", datetime.now())
        with c2:
            heure_evt = st.time_input("Heure", datetime.now().time())
        with c3:
            type_evt = st.radio("Qu'est-ce qui s'est passé ?", ["⚡ J'ai eu une ENVIE (Craving)", "🍷 J'ai CONSOMMÉ"], horizontal=True)
            
        st.divider()
        
        # Intensité
        intensite = st.slider("Intensité de l'envie ou quantité consommée (0-10)", 0, 10, 5)
        
        st.divider()
        
        # PENSÉES AUTOMATIQUES (Le cœur TCC)
        st.write("Quelles pensées vous ont traversé l'esprit ?")
        
        # Info-bulle pédagogique (Expander pour ne pas prendre trop de place mais être lisible)
        with st.expander("ℹ️ Aide : Les 3 types de pensées à repérer"):
            st.markdown("""
            * **🟢 Pensées Permissives :** Autorisations qu'on se donne.  
              *Ex: "Juste un seul, ça ne compte pas", "C'est l'occasion ou jamais".*
            * **🔵 Pensées Soulageantes :** Croyance que le produit est le seul remède.  
              *Ex: "Ça va me calmer", "J'ai besoin de décompresser", "Je ne tiendrai pas sans".*
            * **🟡 Attentes Positives :** Idéalisation des effets.  
              *Ex: "Je serai plus drôle", "Je dormirai mieux", "La soirée sera nulle sans ça".*
            """)
            
        pensees = st.text_area("Vos pensées / Contexte :", placeholder="Ex: Je me sentais stressé et je me suis dit 'Juste un verre pour décompresser'...")
        
        submitted = st.form_submit_button("💾 Enregistrer")
        
        if submitted:
            heure_str = str(heure_evt)[:5]
            
            # Local
            new_row = {
                "Date": str(date_evt),
                "Heure": heure_str,
                "Substance": substance_active,
                "Type": type_evt,
                "Intensité": intensite,
                "Pensées": pensees
            }
            st.session_state.data_addictions = pd.concat([st.session_state.data_addictions, pd.DataFrame([new_row])], ignore_index=True)
            
            # Cloud
            from connect_db import save_data
            patient = st.session_state.get("patient_id", "Anonyme")
            
            # Ordre : Patient, Date, Heure, Substance, Type, Intensité, Pensées
            save_data("Addictions", [
                patient, str(date_evt), heure_str, substance_active, 
                type_evt, intensite, pensees
            ])
            
            st.success("Enregistré !")

# ==============================================================================
# ONGLET 2 : BILAN
# ==============================================================================
with tab2:
    st.header(f"Historique : {substance_active}")
    
    # Filtrage par substance active
    df = st.session_state.data_addictions
    df_filtre = df[df["Substance"] == substance_active]
    
    if not df_filtre.empty:
        # Tableau
        st.dataframe(df_filtre[["Date", "Heure", "Type", "Intensité", "Pensées"]].sort_values(by=["Date", "Heure"], ascending=False), use_container_width=True)
        
        st.divider()
        st.write("#### 📉 Répartition Envies vs Consommations")
        
        # Graphique simple (Barres)
        chart = alt.Chart(df_filtre).mark_bar().encode(
            x='Type',
            y='count()',
            color='Type',
            tooltip=['Type', 'count()']
        ).properties(height=300)
        st.altair_chart(chart, use_container_width=True)
        
        # Gestion suppression
        with st.expander("🗑️ Gérer / Supprimer une entrée"):
            opts = {f"{r['Date']} {r['Heure']} - {r['Type']}": i for i, r in df_filtre.iterrows()}
            sel = st.selectbox("Choisir", list(opts.keys()))
            if st.button("Supprimer"):
                st.session_state.data_addictions = df.drop(opts[sel]).reset_index(drop=True)
                st.rerun()
    else:
        st.info("Aucune donnée pour cette substance.")

st.divider()
st.page_link("streamlit_app.py", label="Retour à l'accueil", icon="🏠")