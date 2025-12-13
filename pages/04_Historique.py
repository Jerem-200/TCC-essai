import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="Historique Global", page_icon="📜", layout="wide")

# ==============================================================================
# 0. SÉCURITÉ & CONNEXION
# ==============================================================================

if "authentifie" not in st.session_state or not st.session_state.authentifie:
    st.warning("🔒 Accès restreint. Veuillez entrer votre Code Patient sur l'accueil.")
    st.page_link("streamlit_app.py", label="Retourner à l'accueil", icon="🏠")
    st.stop()

CURRENT_USER_ID = st.session_state.get("user_id", "")
if not CURRENT_USER_ID:
    st.error("Erreur d'identité. Veuillez vous reconnecter.")
    st.stop()

st.title("📜 Vue d'ensemble de vos progrès")

# ==============================================================================
# 1. CHARGEMENT UNIFIÉ DES DONNÉES
# ==============================================================================
# Fonction utilitaire pour charger une table si elle n'est pas en mémoire
def get_data(key_session, key_cloud, cols_min=None):
    if key_session in st.session_state and not st.session_state[key_session].empty:
        return st.session_state[key_session]
    
    # Tentative chargement Cloud
    try:
        from connect_db import load_data
        data = load_data(key_cloud)
        if data:
            df = pd.DataFrame(data)
            # Filtre Patient
            if "Patient" in df.columns:
                df = df[df["Patient"].astype(str).str.strip() == str(CURRENT_USER_ID).strip()]
            return df
    except: pass
    
    return pd.DataFrame(columns=cols_min if cols_min else [])

# Chargement de TOUTES les sources
df_beck = get_data("data_beck", "Colonnes_Beck")
df_sorc = get_data("data_sorc", "SORC")
df_bdi = get_data("data_echelles", "Echelles_BDI")
df_humeur = get_data("data_humeur_jour", "Humeur")
df_sommeil = get_data("data_sommeil", "Sommeil")
df_conso = get_data("data_addictions", "Addictions")
df_comp = get_data("data_compulsions", "Compulsions")
df_act = get_data("data_activites", "Activites")
df_prob = get_data("data_problemes", "Resolution_Probleme")

# ==============================================================================
# 2. AFFICHAGE PAR ONGLETS THÉMATIQUES
# ==============================================================================

tabs = st.tabs([
    "🧠 Cognitif & Émotion", 
    "🌙 Sommeil & Forme", 
    "🍷 Habitudes & Impulsions", 
    "📝 Activités & Projets"
])

# ------------------------------------------------------------------------------
# ONGLET 1 : COGNITIF (BECK, SORC, HUMEUR, BDI)
# ------------------------------------------------------------------------------
with tabs[0]:
    st.header("État Émotionnel & Cognitif")
    
    c1, c2 = st.columns(2)
    
    # --- A. Humeur Quotidienne ---
    with c1:
        st.subheader("🌈 Humeur (0-10)")
        if not df_humeur.empty:
            df_h = df_humeur.copy()
            df_h["Date"] = pd.to_datetime(df_h["Date"], errors='coerce')
            df_h["Humeur Globale (0-10)"] = pd.to_numeric(df_h["Humeur Globale (0-10)"], errors='coerce')
            df_h = df_h.dropna(subset=["Date"]).sort_values("Date")
            
            chart_hum = alt.Chart(df_h).mark_line(point=True, color="#FFA500").encode(
                x=alt.X('Date:T', axis=alt.Axis(format='%d/%m')),
                y=alt.Y('Humeur Globale (0-10):Q', scale=alt.Scale(domain=[0, 10])),
                tooltip=['Date', 'Humeur Globale (0-10)']
            ).properties(height=250)
            st.altair_chart(chart_hum, use_container_width=True)
        else: st.info("Pas de relevé d'humeur.")

    # --- B. Scores BDI ---
    with c2:
        st.subheader("📉 Dépression (BDI)")
        if not df_bdi.empty:
            df_b = df_bdi.copy()
            df_b["Date"] = pd.to_datetime(df_b["Date"], errors='coerce')
            df_b["Score Total"] = pd.to_numeric(df_b["Score Total"], errors='coerce')
            df_b = df_b.dropna(subset=["Date"]).sort_values("Date")
            
            chart_bdi = alt.Chart(df_b).mark_line(point=True, color="#e74c3c").encode(
                x=alt.X('Date:T', axis=alt.Axis(format='%d/%m')),
                y=alt.Y('Score Total:Q', title='Score BDI'),
                tooltip=['Date', 'Score Total', 'Interprétation']
            ).properties(height=250)
            st.altair_chart(chart_bdi, use_container_width=True)
        else: st.info("Pas de test BDI réalisé.")

    st.divider()
    
    # --- C. Tableaux Beck & SORC ---
    with st.expander("🧩 Voir les Colonnes de Beck (Pensées Automatiques)"):
        if not df_beck.empty: st.dataframe(df_beck, use_container_width=True)
        else: st.info("Aucune fiche Beck.")
        
    with st.expander("🔍 Voir les Analyses SORC (Situations)"):
        if not df_sorc.empty: 
            cols_sorc = ["Date", "Situation", "Pensées", "Émotions", "Réponse", "Csg Court Terme"]
            cols_ok = [c for c in cols_sorc if c in df_sorc.columns]
            st.dataframe(df_sorc[cols_ok], use_container_width=True)
        else: st.info("Aucune analyse SORC.")

# ------------------------------------------------------------------------------
# ONGLET 2 : SOMMEIL (EFFICACITÉ, QUALITÉ)
# ------------------------------------------------------------------------------
with tabs[1]:
    st.header("Sommeil & Énergie")
    
    if not df_sommeil.empty:
        df_s = df_sommeil.copy()
        df_s["Date"] = pd.to_datetime(df_s["Date"], errors='coerce')
        
        # Nettoyage
        for c in ["Efficacité", "Qualité", "Forme"]:
            if c in df_s.columns:
                df_s[c] = pd.to_numeric(df_s[c].astype(str).str.replace('%', ''), errors='coerce')
        
        df_s = df_s.dropna(subset=["Date"]).sort_values("Date")

        # KPI Moyens
        k1, k2, k3 = st.columns(3)
        k1.metric("Efficacité Moyenne", f"{df_s['Efficacité'].mean():.0f}%")
        k2.metric("Qualité Moyenne", f"{df_s['Qualité'].mean():.1f}/5")
        k3.metric("Forme Moyenne", f"{df_s['Forme'].mean():.1f}/5")

        # Graphique Combiné
        st.subheader("📈 Évolution Qualité vs Efficacité")
        
        base = alt.Chart(df_s).encode(x=alt.X('Date:T', axis=alt.Axis(format='%d/%m')))
        
        line_eff = base.mark_line(color="#3498db").encode(
            y=alt.Y('Efficacité:Q', axis=alt.Axis(title='Efficacité (%)', titleColor="#3498db")),
            tooltip=['Date', 'Efficacité']
        )
        
        line_qual = base.mark_line(color="#9b59b6", strokeDash=[5,5]).encode(
            y=alt.Y('Qualité:Q', axis=alt.Axis(title='Qualité (0-5)', titleColor="#9b59b6")),
            tooltip=['Date', 'Qualité']
        )
        
        st.altair_chart(alt.layer(line_eff, line_qual).resolve_scale(y='independent'), use_container_width=True)
        
    else:
        st.info("Aucune donnée de sommeil enregistrée.")

# ------------------------------------------------------------------------------
# ONGLET 3 : HABITUDES (CONSOS & COMPULSIONS)
# ------------------------------------------------------------------------------
with tabs[2]:
    st.header("Consommations & Compulsions")
    
    c_conso, c_comp = st.columns(2)
    
    # --- A. Consommations ---
    with c_conso:
        st.subheader("🍷 Envies & Consos")
        if not df_conso.empty:
            df_c = df_conso.copy()
            # Séparation
            df_envie = df_c[df_c["Type"].str.contains("ENVIE", na=False)]
            df_acte = df_c[df_c["Type"].str.contains("CONSOMMÉ", na=False)]
            
            st.metric("Total Envies", len(df_envie))
            st.metric("Total Consos", len(df_acte))
            
            if not df_acte.empty:
                st.caption("Substances les plus fréquentes :")
                st.dataframe(df_acte["Substance"].value_counts(), use_container_width=True)
        else:
            st.info("Rien à signaler.")

    # --- B. Compulsions ---
    with c_comp:
        st.subheader("🛑 Compulsions (TOC)")
        if not df_comp.empty:
            df_t = df_comp.copy()
            df_t["Date"] = pd.to_datetime(df_t["Date"], errors='coerce')
            df_t["Durée (min)"] = pd.to_numeric(df_t["Durée (min)"], errors='coerce').fillna(0)
            
            total_tps = df_t["Durée (min)"].sum()
            st.metric("Temps total perdu", f"{int(total_tps)} min")
            
            # Petit graph d'évolution du temps perdu
            if not df_t.dropna(subset=["Date"]).empty:
                 chart_toc = alt.Chart(df_t).mark_bar().encode(
                     x=alt.X('Date:T', axis=alt.Axis(format='%d/%m')),
                     y='sum(Durée (min)):Q',
                     tooltip=['Date', 'sum(Durée (min))']
                 ).properties(height=200, title="Minutes perdues par jour")
                 st.altair_chart(chart_toc, use_container_width=True)
        else:
            st.info("Pas de compulsions notées.")

# ------------------------------------------------------------------------------
# ONGLET 4 : ACTIVITÉS & PROBLÈMES
# ------------------------------------------------------------------------------
with tabs[3]:
    st.header("Engagement & Solutions")
    
    # --- A. Activités ---
    st.subheader("📝 Registre des Activités")
    if not df_act.empty:
        df_a = df_act.copy()
        cols_score = ["Plaisir (0-10)", "Maîtrise (0-10)", "Satisfaction (0-10)"]
        for c in cols_score: df_a[c] = pd.to_numeric(df_a[c], errors='coerce')
        
        # Moyennes globales
        m_plaisir = df_a["Plaisir (0-10)"].mean()
        m_maitrise = df_a["Maîtrise (0-10)"].mean()
        
        k1, k2 = st.columns(2)
        k1.metric("Plaisir Moyen", f"{m_plaisir:.1f}/10")
        k2.metric("Maîtrise Moyenne", f"{m_maitrise:.1f}/10")
        
        # Top Activités
        st.caption("Top Activités (Par Plaisir)")
        top_act = df_a.groupby("Activité")["Plaisir (0-10)"].mean().sort_values(ascending=False).head(5)
        st.bar_chart(top_act)
    else:
        st.info("Aucune activité enregistrée.")
        
    st.divider()
    
    # --- B. Problèmes ---
    st.subheader("💡 Résolution de Problèmes (Plans d'action)")
    if not df_prob.empty:
        # Sélecteur pour voir le détail
        opts = {f"{r['Date']} : {r['Problème'][:50]}...": i for i, r in df_prob.iterrows()}
        choix = st.selectbox("Voir un plan d'action :", list(opts.keys()))
        
        if choix:
            row = df_prob.iloc[opts[choix]]
            with st.container(border=True):
                st.success(f"🎯 Objectif : {row['Objectif']}")
                st.info(f"🚀 Solution : {row['Solution Choisie']}")
                st.text_area("Plan d'action", row.get("Plan Action", ""), disabled=True)
                c1, c2 = st.columns(2)
                c1.write(f"**Obstacles:** {row.get('Obstacles', '-')}")
                c2.write(f"**Ressources:** {row.get('Ressources', '-')}")
    else:
        st.info("Aucun problème traité.")

st.divider()
st.page_link("streamlit_app.py", label="Retour à l'accueil", icon="🏠")