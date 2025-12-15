from fpdf import FPDF
import pandas as pd
from datetime import datetime

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Rapport de Suivi TCC', 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.cell(0, 10, f'Généré le {datetime.now().strftime("%d/%m/%Y")}', 0, 1, 'C')
        self.ln(10)

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(200, 220, 255)
        self.cell(0, 10, f"  {title}", 0, 1, 'L', 1)
        self.ln(4)

    def chapter_body_text(self, body):
        self.set_font('Arial', '', 10)
        self.multi_cell(0, 6, body)
        self.ln()

    def add_table_simple(self, df, cols_to_show):
        self.set_font('Arial', 'B', 9)
        # En-têtes
        for col in cols_to_show:
            self.cell(40, 7, str(col)[:15], 1)
        self.ln()
        # Données
        self.set_font('Arial', '', 9)
        for i, row in df.iterrows():
            for col in cols_to_show:
                txt = str(row.get(col, '-'))[:20] # Tronquer si trop long
                self.cell(40, 7, txt, 1)
            self.ln()
        self.ln(5)

def generer_pdf(data_dict, patient_id):
    pdf = PDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f"Patient ID: {patient_id}", 0, 1)
    pdf.ln(5)

    # 1. ÉCHELLES CLINIQUES
    pdf.chapter_title("1. Échelles Cliniques & Scores")
    
    # Résumé des derniers scores disponibles
    scores_text = ""
    
    # BDI
    if not data_dict.get('bdi').empty:
        last = data_dict['bdi'].iloc[-1]
        scores_text += f"- BDI (Dépression) : {last.get('Total', '?')} (Date: {last.get('Date', '?')})\n"
    
    # PHQ-9
    if not data_dict.get('phq9').empty:
        last = data_dict['phq9'].iloc[-1]
        scores_text += f"- PHQ-9 (Dépression) : {last.get('Score Total', '?')} - {last.get('Sévérité', '')}\n"

    # GAD-7
    if not data_dict.get('gad7').empty:
        last = data_dict['gad7'].iloc[-1]
        scores_text += f"- GAD-7 (Anxiété) : {last.get('Score Total', '?')} - {last.get('Sévérité', '')}\n"

    # WHO-5
    if not data_dict.get('who5').empty:
        last = data_dict['who5'].iloc[-1]
        scores_text += f"- WHO-5 (Bien-être) : {last.get('Score Pourcent', '?')}%\n"

    if scores_text:
        pdf.chapter_body_text(scores_text)
    else:
        pdf.chapter_body_text("Aucune échelle remplie sur la période.")

    # 2. SOMMEIL
    pdf.chapter_title("2. Synthèse du Sommeil")
    df_s = data_dict.get('sommeil')
    if not df_s.empty:
        eff_moy = pd.to_numeric(df_s["Efficacité"].astype(str).str.replace('%',''), errors='coerce').mean()
        pdf.chapter_body_text(f"Nombre de nuits enregistrées : {len(df_s)}")
        pdf.chapter_body_text(f"Efficacité moyenne du sommeil : {eff_moy:.1f}%")
        # Petit tableau des 5 dernières nuits
        cols = ["Date", "Heure Coucher", "Heure Lever", "Efficacité"]
        pdf.add_table_simple(df_s.tail(5), cols)
    else:
        pdf.chapter_body_text("Pas de données de sommeil.")

    # 3. ACTIVITÉS
    pdf.chapter_title("3. Activités & Humeur")
    df_a = data_dict.get('activites')
    if not df_a.empty:
        pdf.chapter_body_text(f"Nombre d'activités notées : {len(df_a)}")
        cols = ["Date", "Heure", "Activité", "Plaisir (0-10)"]
        pdf.add_table_simple(df_a.tail(7), cols)
    else:
        pdf.chapter_body_text("Pas d'activités enregistrées.")

    # 4. BECK (Pensées)
    pdf.chapter_title("4. Colonnes de Beck (Derniers exercices)")
    df_b = data_dict.get('beck')
    if not df_b.empty:
        # Affichage simplifié pour Beck (car le texte est long)
        pdf.set_font('Arial', '', 9)
        for i, row in df_b.tail(3).iterrows():
            pdf.set_font('Arial', 'B', 10)
            pdf.cell(0, 6, f"Date : {row.get('Date','?')}", 0, 1)
            pdf.set_font('Arial', '', 9)
            pdf.multi_cell(0, 5, f"Situation: {str(row.get('Situation',''))[:100]}...")
            pdf.multi_cell(0, 5, f"Pensée Auto: {str(row.get('Pensée Auto',''))[:100]}...")
            pdf.multi_cell(0, 5, f"Réponse Rationnelle: {str(row.get('Pensée Rationnelle',''))[:100]}...")
            pdf.ln(3)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y()) # Ligne de séparation
            pdf.ln(3)
    else:
        pdf.chapter_body_text("Pas d'exercice de restructuration.")

    return pdf.output(dest='S').encode('latin-1', 'replace')