import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="Historique", page_icon="📜", layout="wide")

# --- VÉRIFICATION DE SÉCURITÉ ---
if "authentifie" not in st.session_state or not st.session_state.authentifie:
    st.warning("⛔ Veuillez vous connecter sur la page d'accueil pour accéder à cet outil.")
    st.switch_page("streamlit_app.py") # Renvoie vers le login
    st.stop() # Arrête le chargement de la page

st.title("📜 Historique de vos progrès")

# --- INITIALISATION ---
if "data_beck" not in st.session_state: st.session_state.data_beck = pd.DataFrame()
if "data_echelles" not in st.session_state: st.session_state.data_echelles = pd.DataFrame()
if "data_activites" not in st.session_state: st.session_state.data_activites = pd.DataFrame()
if "data_humeur_jour" not in st.session_state: st.session_state.data_humeur_jour = pd.DataFrame()
# On ajoute les nouvelles colonnes ici aussi pour éviter les bugs
if "data_problemes" not in st.session_state: 
    st.session_state.data_problemes = pd.DataFrame(columns=[
        "Date", "Problème", "Objectif", "Solution Choisie", 
        "Plan Action", "Obstacles", "Ressources", "Date Évaluation"
    ])

# --- 4 ONGLETS ---
t1, t2, t3, t4 = st.tabs(["🧩 Beck", "📊 Scores", "📝 Registre", "💡 Problèmes"])

# 1. BECK
with t1:
    if not st.session_state.data_beck.empty: st.dataframe(st.session_state.data_beck, use_container_width=True)
    else: st.info("Vide")

# 2. SCORES
with t2:
    if not st.session_state.data_echelles.empty: st.dataframe(st.session_state.data_echelles, use_container_width=True)
    else: st.info("Vide")

# 3. REGISTRE
with t3:
    st.subheader("1. Humeur Globale")
    if not st.session_state.data_humeur_jour.empty:
        df_humeur = st.session_state.data_humeur_jour.drop_duplicates(subset=["Date"], keep='last')
        st.line_chart(df_humeur.set_index("Date")["Humeur Globale (0-10)"])
    else: st.info("Pas d'humeur notée.")
    
    st.divider()
    
    if not st.session_state.data_activites.empty:
        df_act = st.session_state.data_activites.copy()
        cols = ["Plaisir (0-10)", "Maîtrise (0-10)", "Satisfaction (0-10)"]
        for c in cols: df_act[c] = pd.to_numeric(df_act[c], errors='coerce')

        st.subheader("2. Comparatif par Activité (Moyenne)")
        df_mean = df_act.groupby("Activité")[cols].mean().reset_index()
        df_long_bar = df_mean.melt("Activité", var_name="Type", value_name="Score")
        chart_bar = alt.Chart(df_long_bar).mark_bar().encode(
            x=alt.X('Activité:N', axis=alt.Axis(labelAngle=0)), y='Score:Q',
            color='Type:N', xOffset='Type:N', tooltip=['Activité', 'Type', alt.Tooltip('Score', format='.1f')]
        ).properties(height=350)
        st.altair_chart(chart_bar, use_container_width=True)

        st.divider()

        st.subheader("3. Fluctuations Chronologiques")
        try:
            df_act['Full_Date'] = pd.to_datetime(df_act['Date'].astype(str) + ' ' + df_act['Heure'].astype(str), errors='coerce')
        except: df_act['Full_Date'] = pd.to_datetime(df_act['Date'])

        df_line_long = df_act.melt(id_vars=['Full_Date', 'Activité'], value_vars=cols, var_name="Indicateur", value_name="Score")
        
        line_chart = alt.Chart(df_line_long).mark_line(
            point=alt.OverlayMarkDef(size=150, filled=True)
        ).encode(
            x=alt.X('Full_Date:T', title='Temps', axis=alt.Axis(format='%d/%m %H:%M')), 
            y=alt.Y('Score:Q', title='Note (0-10)'),
            color='Indicateur:N',
            tooltip=[alt.Tooltip('Full_Date', title='Date', format='%d/%m %H:%M'), alt.Tooltip('Activité'), alt.Tooltip('Indicateur'), alt.Tooltip('Score')]
        ).interactive()
        st.altair_chart(line_chart, use_container_width=True)
    else: st.info("Pas d'activités.")

# 4. FICHE RÉCAP PROBLÈMES (C'EST ICI LA NOUVEAUTÉ)
with t4:
    st.subheader("🗂️ Vos Plans d'Actions")
    
    df_prob = st.session_state.data_problemes
    
    if not df_prob.empty:
        # 1. Liste déroulante pour choisir quel problème voir
        # On crée une liste de titres "Date - Problème"
        options_dict = {f"{row['Date']} : {row['Problème'][:40]}...": i for i, row in df_prob.iterrows()}
        selected_option = st.selectbox("🔍 Sélectionnez un plan à consulter :", list(options_dict.keys()))
        
        # On récupère la ligne sélectionnée
        index_selected = options_dict[selected_option]
        row = df_prob.iloc[index_selected]
        
        st.divider()
        
        # 2. LA FICHE RÉCAP VISUELLE
        with st.container(border=True):
            st.markdown(f"### 🚀 Solution choisie : {row['Solution Choisie']}")
            
            c1, c2 = st.columns(2)
            with c1: 
                st.caption("Problème initial")
                st.info(row["Problème"])
            with c2:
                st.caption("Objectif visé")
                st.success(row["Objectif"])
            
            st.write("---")
            st.markdown("#### 📝 Plan d'action détaillé")
            # Vérification si la colonne existe (au cas où c'est un vieux problème enregistré avant la mise à jour)
            plan_txt = row.get("Plan Action", "Non renseigné")
            st.code(plan_txt, language=None) # On l'affiche joliment
            
            c3, c4 = st.columns(2)
            with c3:
                st.markdown("**⚠️ Obstacles anticipés**")
                st.write(row.get("Obstacles", "-"))
            with c4:
                st.markdown("**🛠️ Ressources nécessaires**")
                st.write(row.get("Ressources", "-"))
                
            st.write("---")
            st.caption(f"📅 Bilan prévu le : **{row['Date Évaluation']}**")

    else:
        st.info("Aucun problème enregistré. Allez dans l'onglet 'Résolution de Problèmes' pour commencer.")

st.divider()
st.page_link("streamlit_app.py", label="Retour à l'accueil", icon="🏠")