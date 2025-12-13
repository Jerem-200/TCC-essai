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

st.title("📜 Historique de vos progrès")

# ==============================================================================
# 1. FONCTION DE CHARGEMENT UNIFIÉE
# ==============================================================================
def get_data(key_session, key_cloud):
    """Charge les données depuis la session ou le cloud de manière sécurisée"""
    # 1. Priorité Session
    if key_session in st.session_state and isinstance(st.session_state[key_session], pd.DataFrame) and not st.session_state[key_session].empty:
        return st.session_state[key_session]
    
    # 2. Sinon Cloud
    try:
        from connect_db import load_data
        data = load_data(key_cloud)
        if data:
            df = pd.DataFrame(data)
            # Filtre sur l'utilisateur courant
            if "Patient" in df.columns:
                df = df[df["Patient"].astype(str).str.strip() == str(CURRENT_USER_ID).strip()]
            return df
    except: pass
    
    return pd.DataFrame() # Retourne vide si rien trouvé

# Chargement de toutes les données au début
df_sommeil = get_data("data_sommeil", "Sommeil")
df_act = get_data("data_activites", "Activites")
df_conso = get_data("data_addictions", "Addictions")
df_comp = get_data("data_compulsions", "Compulsions")
df_humeur = get_data("data_humeur_jour", "Humeur")

df_beck = get_data("data_beck", "Colonnes_Beck")
df_sorc = get_data("data_sorc", "SORC")
df_prob = get_data("data_problemes", "Resolution_Probleme")
df_bdi = get_data("data_echelles", "Echelles_BDI")
df_balance = get_data("data_balance", "Balance_Decisionnelle")

# ==============================================================================
# 2. AFFICHAGE PAR GRANDS ONGLETS
# ==============================================================================

main_tab1, main_tab2 = st.tabs(["📅 Agendas (Suivi Quotidien)", "🛠️ Outils Thérapeutiques"])

# ------------------------------------------------------------------------------
# ONGLET 1 : AGENDAS
# ------------------------------------------------------------------------------
with main_tab1:
    st.header("Suivi des habitudes")

    # --- 1. SOMMEIL ---
    with st.expander("🌙 Sommeil & Énergie"):
        if not df_sommeil.empty:
            df_s = df_sommeil.copy()
            df_s["Date"] = pd.to_datetime(df_s["Date"], errors='coerce')
            
            # Nettoyage chiffres
            for c in ["Efficacité", "Qualité", "Forme"]:
                if c in df_s.columns:
                    df_s[c] = pd.to_numeric(df_s[c].astype(str).str.replace('%', ''), errors='coerce')
            
            df_s = df_s.dropna(subset=["Date"]).sort_values("Date")
            
            # KPI
            k1, k2, k3 = st.columns(3)
            k1.metric("Efficacité Moy.", f"{df_s['Efficacité'].mean():.0f}%")
            k2.metric("Qualité Moy.", f"{df_s['Qualité'].mean():.1f}/5")
            k3.metric("Forme Moy.", f"{df_s['Forme'].mean():.1f}/5")
            
            # Graphique
            base = alt.Chart(df_s).encode(x=alt.X('Date:T', axis=alt.Axis(format='%d/%m')))
            line_eff = base.mark_line(color="#3498db").encode(y=alt.Y('Efficacité:Q', title='Efficacité (%)'))
            st.altair_chart(line_eff.interactive(), use_container_width=True)
            
            # Tableau
            st.dataframe(df_s[["Date", "Heure Coucher", "Heure Lever", "Efficacité", "Qualité"]], hide_index=True, use_container_width=True)
        else:
            st.info("Aucune donnée de sommeil.")

    # --- 2. ACTIVITÉS ---
    with st.expander("📝 Registre des Activités & Humeur"):
        c1, c2 = st.columns(2)
        with c1:
            if not df_humeur.empty:
                st.caption("Évolution de l'Humeur")
                df_h = df_humeur.copy()
                df_h["Date"] = pd.to_datetime(df_h["Date"], errors='coerce')
                df_h["Humeur Globale (0-10)"] = pd.to_numeric(df_h["Humeur Globale (0-10)"], errors='coerce')
                st.line_chart(df_h.set_index("Date")["Humeur Globale (0-10)"], color="#FFA500")
            else: st.info("Pas d'humeur notée.")
            
        with c2:
            if not df_act.empty:
                st.caption("Activités : Plaisir Moyen")
                df_a = df_act.copy()
                df_a["Plaisir (0-10)"] = pd.to_numeric(df_a["Plaisir (0-10)"], errors='coerce')
                top_act = df_a.groupby("Activité")["Plaisir (0-10)"].mean().sort_values(ascending=False).head(5)
                st.bar_chart(top_act, color="#2ecc71")
            else: st.info("Pas d'activités notées.")
            
        if not df_act.empty:
            st.dataframe(df_act, hide_index=True, use_container_width=True)

    # --- 3. CONSOMMATIONS ---
    with st.expander("🍷 Envies & Consommations"):
        if not df_conso.empty:
            df_c = df_conso.copy()
            df_c["Date"] = pd.to_datetime(df_c["Date"], errors='coerce')
            
            cnt_envie = len(df_c[df_c["Type"].str.contains("ENVIE", na=False)])
            cnt_conso = len(df_c[df_c["Type"].str.contains("CONSOMMÉ", na=False)])
            
            m1, m2 = st.columns(2)
            m1.metric("Total Envies", cnt_envie)
            m2.metric("Total Consos", cnt_conso)
            
            st.dataframe(df_c[["Date", "Heure", "Type", "Substance", "Intensité", "Quantité", "Unité"]], hide_index=True, use_container_width=True)
        else:
            st.info("Aucune donnée de consommation.")

    # --- 4. COMPULSIONS ---
    with st.expander("🛑 Compulsions (TOC)"):
        if not df_comp.empty:
            df_t = df_comp.copy()
            df_t["Date"] = pd.to_datetime(df_t["Date"], errors='coerce')
            df_t["Durée (min)"] = pd.to_numeric(df_t["Durée (min)"], errors='coerce').fillna(0)
            
            st.metric("Temps total consacré aux rituels", f"{int(df_t['Durée (min)'].sum())} min")
            
            chart_toc = alt.Chart(df_t).mark_bar(color="#e74c3c").encode(
                x=alt.X('Date:T', axis=alt.Axis(format='%d/%m')),
                y='sum(Durée (min)):Q'
            ).properties(height=200)
            st.altair_chart(chart_toc, use_container_width=True)
            
            st.dataframe(df_t, hide_index=True, use_container_width=True)
        else:
            st.info("Aucune compulsion notée.")


# ------------------------------------------------------------------------------
# ONGLET 2 : OUTILS
# ------------------------------------------------------------------------------
with main_tab2:
    st.header("Exercices & Analyses")

    # --- 1. COLONNES DE BECK ---
    with st.expander("🧩 Restructuration Cognitive (Beck)"):
        if not df_beck.empty:
            st.caption("Vos pensées alternatives")
            st.dataframe(df_beck, use_container_width=True, hide_index=True)
        else:
            st.info("Aucun tableau de Beck enregistré.")

    # --- 2. ANALYSE SORC ---
    with st.expander("🔍 Analyse Fonctionnelle (SORC)"):
        if not df_sorc.empty:
            cols_sorc = ["Date", "Situation", "Pensées", "Émotions", "Réponse", "Csg Court Terme"]
            # On vérifie quelles colonnes existent vraiment
            cols_ok = [c for c in cols_sorc if c in df_sorc.columns]
            st.dataframe(df_sorc[cols_ok], use_container_width=True, hide_index=True)
        else:
            st.info("Aucune analyse SORC enregistrée.")

    # --- 3. RÉSOLUTION DE PROBLÈMES ---
    with st.expander("💡 Résolution de Problèmes"):
        if not df_prob.empty:
            # Sélecteur pour voir le détail
            opts = {f"{r['Date']} : {r['Problème'][:50]}...": i for i, r in df_prob.iterrows()}
            choix = st.selectbox("Voir un plan d'action :", list(opts.keys()))
            
            if choix:
                row = df_prob.iloc[opts[choix]]
                st.success(f"🎯 Objectif : {row['Objectif']}")
                st.info(f"🚀 Solution : {row['Solution Choisie']}")
                st.text_area("Plan d'action", row.get("Plan Action", ""), disabled=True)
                
                c1, c2 = st.columns(2)
                c1.write(f"**Obstacles:** {row.get('Obstacles', '-')}")
                c2.write(f"**Ressources:** {row.get('Ressources', '-')}")
        else:
            st.info("Aucun problème traité.")

    # --- 4. BALANCE DÉCISIONNELLE ---
    with st.expander("⚖️ Balance Décisionnelle"):
        if not df_balance.empty:
             st.dataframe(df_balance, use_container_width=True, hide_index=True)
        else:
            st.info("Aucune balance décisionnelle enregistrée.")

    # --- 5. ÉCHELLES BDI ---
    with st.expander("📉 Suivi Dépression (BDI)"):
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
            st.dataframe(df_b, use_container_width=True, hide_index=True)
        else:
            st.info("Aucun test BDI réalisé.")

st.divider()
st.page_link("streamlit_app.py", label="Retour à l'accueil", icon="🏠")