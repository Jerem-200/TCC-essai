import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Échelles BDI", page_icon="📊")

# --- VÉRIFICATION DE SÉCURITÉ ---
if "authentifie" not in st.session_state or not st.session_state.authentifie:
    st.warning("⛔ Veuillez vous connecter sur la page d'accueil pour accéder à cet outil.")
    st.switch_page("streamlit_app.py") # Renvoie vers le login
    st.stop() # Arrête le chargement de la page

st.title("📊 Échelle BDI-II (Dépression)")
st.write("Ce questionnaire comporte 21 groupes d'énoncés. Choisissez l'énoncé qui décrit le mieux comment vous vous êtes senti(e) au cours des deux dernières semaines.")

# --- 1. S'ASSURER QUE LA MÉMOIRE EXISTE ---
if "data_echelles" not in st.session_state:
    st.session_state.data_echelles = pd.DataFrame(columns=["Date", "Type", "Score", "Commentaire"])


questions_bdi = {
    "1. Tristesse": [
        "0 Je ne me sens pas triste.",
        "1 Je me sens triste la plupart du temps.",
        "2 Je suis triste tout le temps.",
        "3 Je suis si triste ou malheureux que je ne peux pas le supporter."
    ],
    "2. Pessimisme": [
        "0 Je ne suis pas découragé(e) face à mon avenir.",
        "1 Je suis plus découragé(e) face à mon avenir que d'habitude.",
        "2 Je ne m'attends pas à ce que les choses s'arrangent.",
        "3 J'ai le sentiment que mon avenir est sans espoir..."
    ],
    "3. Échecs dans le passé": [
        "0 Je n'ai pas le sentiment d'avoir échoué dans la vie, d'être un(e) raté(e).",
        "1 J'ai échoué plus souvent que je n'aurais dû.",
        "2 Quand je pense à mon passé, je constate un grand nombre d'échecs.",
        "3 J'ai le sentiment d'avoir complètement raté ma vie."
    ],
    "4. Perte de plaisir": [ 
        "0 J'éprouve toujours autant de plaisir qu'avant aux choses qui me plaisent.",
        "1 Je n'éprouve pas autant de plaisir aux choses qu'avant.",
        "2 J'éprouve très peu de plaisir aux choses qui me plaisaient habituellement.",
        "3 Je n'éprouve aucun plaisir aux choses qui me plaisaient habituellement."
    ],
    "5. Sentiments de culpabilité":[
        "0 Je ne me sens pas particulièrement coupable.",
        "1 Je me sens coupable pour bien des choses que j'ai faites ou que j'aurais dû faire.",
        "2 Je me sens coupable la plupart du temps.",
        "3 Je me sens tout le temps coupable."
    ],
    "6. Sentiment d'être puni(e)": [
        "0 Je n'ai pas le sentiment d'être puni(e).",
        "1 Je sens que je pourrais être puni(e).",
        "2 Je m'attends à être puni(e).",
        "3 J'ai le sentiment d'être puni(e)."
    ],
    "7. Sentiments négatifs envers soi-même": [
        "0 Mes sentiments envers moi-même n'ont pas changé.",
        "1 J'ai perdu confiance en moi.",
        "2 Je suis déçu(e) par moi-même.",
        "3 Je ne m'aime pas du tout."
    ],
    "8. Attitude critique envers soi": [
        "0 Je ne me blâme pas ou ne me critique pas plus que d'habitude.",
        "1 Je suis plus critique envers moi-même que je ne l'étais.",
        "2 Je me reproche tous mes défauts.",
        "3 Je me reproche tous les malheurs qui arrivent."
    ],
    "9. Pensées ou désirs de suicide": [
        "0 Je ne pense pas du tout à me suicider.",
        "1 Il m'arrive de penser à me suicider, mais je ne le ferai pas.",
        "2 J'aimerais me suicider.",
        "3 Je me suiciderais si l'occasion se présentait."
    ],
    "10. Pleurs":[
        "0 Je ne pleure pas plus qu'avant.",
        "1 Je pleure plus qu'avant.",
        "2 Je pleure pour la moindre petite chose.",
        "3 Je voudrais pleurer mais je ne suis pas capable."
    ],
    "11. Agitation":[
        "0 Je ne suis pas plus agité(e) ou plus tendu(e) que d'habitude.",
        "1 Je me sens plus agité(e) ou plus tendu(e) que d'habitude.",
        "2 Je suis si agité(e) ou tendu(e) que j'ai du mal à rester tranquille.",
        "3 Je suis si agité(e) ou tendu(e) que je dois continuellement bouger ou faire quelque chose."
    ],
    "12. Perte d'intérêt":[
        "0 Je n'ai pas perdu d'intérêt pour les gens ou pour les activités.",
        "1 Je m'intéresse moins qu'avant aux gens et aux choses.",
        "2 Je ne m'intéresse presque plus aux gens et aux choses.",
        "3 J'ai du mal à m'intéresser à quoique ce soit."
    ],
    "13. Indécision":[
        "0 Je prends des décisions toujours aussi bien qu'avant.",
        "1 Il m'est plus difficile que d'habitude de prendre des décisions.",
        "2 J'ai beaucoup plus de mal qu'avant à prendre des décisions.",
        "3 J'ai du mal à prendre n'importe quelle décision."
    ],
    "14. Dévalorisation":[
        "0 Je pense être quelqu'un de valable.",
        "1 Je ne crois pas avoir autant de valeur ni être aussi utile qu'avant.",
        "2 Je me sens moins valable que les autres.",
        "3 Je sens que je ne vaux absolument rien."
    ],
    "15. Perte d'énergie":[
        "0 J'ai toujours autant d'énergie qu'avant.",
        "1 J'ai moins d'énergie qu'avant.",
        "2 Je n'ai pas assez d'énergie pour pouvoir faire grand-chose.",
        "3 J'ai trop peu d'énergie pour faire quoi que ce soit."
    ],
    "16. Modifications dans les habitudes de sommeil":[
        "0 Mes habitudes de sommeil n'ont pas changé.",
        "1a Je dors un peu plus que d'habitude.",
        "1a Je dors un peu moins que d'habitude.",
        "2b Je dors beaucoup plus que d'habitude.",
        "2b Je dors beaucoup moins que d'habitude.",
        "3c Je dors presque toute la journée.",
        "3c Je me réveille une ou deux heures plus tôt et je suis incapable de me rendormir."
    ],
    "17. Irritabilité":[
        "0 Je ne suis pas plus irritable que d'habitude.",
        "1 Je suis plus irritable que d'habitude.",
        "2 Je suis beaucoup plus irritable que d'habitude.",
        "3 Je suis constamment irritable."
    ],
    "18. Modifications de l'appétit":[
        "0 Mon appétit n'a pas changé.",
        "1 J'ai un peu moins d'appétit que d'habitude.",
        "1 J'ai un peu plus d'appétit que d'habitude.",
        "2 J'ai beaucoup moins d'appétit que d'habitude.",
        "2 J'ai beaucoup plus d'appétit que d'habitude.",
        "3 Je n'ai pas d'appétit du tout.",
        "3 J'ai constamment envie de manger."
    ],
    "19. Difficulté à se concentrer":[
        "0 Je parviens à me concentrer toujours aussi bien qu'avant.",
        "1 Je ne parviens pas à me concentrer aussi bien que d'habitude.",
        "2 J'ai du mal à me concentrer longtemps sur quoi que ce soit.",
        "3 Je me trouve incapable de me concentrer sur quoi que ce soit."
    ],
    "20. Fatigue":[
        "0 Je ne suis pas plus fatiqué(e) que d'habitude.",
        "1 Je me fatigue plus facilement que d'habitude.",
        "2 Je suis trop fatigué(e) pour faire un grand nombre de choses que je faisais avant.",
        "3 Je suis trop fatigué(e) pour faire la plupart des choses que je faisais avant."
    ],
    "21. Perte d'intérêt pour le sexe":[
        "0 Je n'ai pas noté de changement récent dans mon intérêt pour le sexe.",
        "1 Le sexe m'intéresse moins qu'avant.",
        "2 Le sexe m'intéresse beaucoup moins maintenant.",
        "3 J'ai perdu tout intérêt pour le sexe."
    ]
}
# --- 3. LE FORMULAIRE ---
score_total = 0

with st.form("bdi_form"):
    for question, options in questions_bdi.items():
        st.write(f"**{question}**")
        # On affiche les choix
        choix = st.radio(f"Choix pour {question}", options, index=0, label_visibility="collapsed")
        
        # --- CORRECTION ICI ---
        # On prend juste le premier caractère de la chaîne (le '0', '1', '2' ou '3')
        # C'est plus solide : ça marche qu'il y ait un tiret ou non.
        points = int(choix[0])
        
        score_total += points
        st.markdown("---")

    # Le bouton est bien à l'intérieur du form, tout à la fin
    submitted = st.form_submit_button("Calculer et Enregistrer le Score")

    if submitted:
        # Interprétation
        interpretation = ""
        if score_total <= 13: interpretation = "Dépression minimale"
        elif score_total <= 19: interpretation = "Dépression légère"
        elif score_total <= 28: interpretation = "Dépression modérée"
        else: interpretation = "Dépression sévère"

        # 1. Sauvegarde Locale (Session)
        new_row = {
            "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "Type": "BDI-II", "Score": score_total, "Commentaire": interpretation
        }
        st.session_state.data_echelles = pd.concat([st.session_state.data_echelles, pd.DataFrame([new_row])], ignore_index=True)
        
        # 2. SAUVEGARDE CLOUD (NOUVEAU)
        from connect_db import save_data

        # On récupère l'ID du patient (ou "Inconnu" s'il y a un bug)
        patient = st.session_state.get("patient_id", "Inconnu")
        
        # On prépare la ligne pour Excel
        ligne_excel = [
            patient,
            datetime.now().strftime("%Y-%m-%d %H:%M"), 
            "BDI-II", 
            score_total, 
            interpretation
        ]
        
        # On envoie vers l'onglet "Scores"
        if save_data("Scores", ligne_excel):
            st.success(f"Score ({score_total}) sauvegardé dans le Cloud ! ☁️")
        else:
            st.warning("Sauvegardé en local uniquement (Erreur Cloud).")

st.divider()
st.page_link("streamlit_app.py", label="Retour à l'accueil", icon="🏠")