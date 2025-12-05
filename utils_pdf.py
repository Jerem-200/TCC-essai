from fpdf import FPDF
import pandas as pd

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Mon Rapport TCC - Suivi Hebdomadaire', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, label):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(200, 220, 255) # Bleu clair
        self.cell(0, 6, label, 0, 1, 'L', 1)
        self.ln(4)

    def chapter_body(self, text):
        self.set_font('Arial', '', 11)
        self.multi_cell(0, 5, text)
        self.ln()

def generer_pdf(beck_df, bdi_df, activites_df, problemes_df, patient_name):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font('Arial', '', 12)
    
    # Intro
    pdf.cell(0, 10, f"Patient : {patient_name}", 0, 1)
    pdf.cell(0, 10, f"Date du rapport : {pd.Timestamp.now().strftime('%d/%m/%Y')}", 0, 1)
    pdf.ln(5)

    # 1. SCORES BDI
    pdf.chapter_title(f"1. Suivi de l'Humeur (BDI) - {len(bdi_df)} enregistrements")
    if not bdi_df.empty:
        for index, row in bdi_df.iterrows():
            txt = f"- Date : {row.get('Date','?')} | Score : {row.get('Score','?')} | {row.get('Commentaire','')}"
            # Nettoyage des caractères spéciaux pour éviter les bugs PDF
            txt = txt.encode('latin-1', 'replace').decode('latin-1')
            pdf.chapter_body(txt)
    else:
        pdf.chapter_body("Aucune donnée.")

    # 2. COLONNES DE BECK
    pdf.chapter_title(f"2. Colonnes de Beck - {len(beck_df)} exercices")
    if not beck_df.empty:
        for index, row in beck_df.iterrows():
            txt = (f"Date : {row.get('Date','?')}\n"
                   f"Situation : {row.get('Situation','-')}\n"
                   f"Emotion : {row.get('Émotion','-')} ({row.get('Intensité Avant','?')} -> {row.get('Intensité Après','?')})\n"
                   f"Pensée Auto : {row.get('Pensée Auto','-')} ({row.get('Croyance (Avant)','?')} -> {row.get('Croyance (Après)','?')})\n"
                   f"Pensée Rationnelle : {row.get('Pensée Rationnelle','-')}\n"
                   "------------------------------------------------")
            txt = txt.encode('latin-1', 'replace').decode('latin-1')
            pdf.chapter_body(txt)
    else:
        pdf.chapter_body("Aucune donnée.")

    # 3. ACTIVITÉS
    pdf.chapter_title(f"3. Registre des Activités - {len(activites_df)} activités")
    if not activites_df.empty:
        # On affiche juste les 10 dernières pour ne pas faire 50 pages
        derniers = activites_df.tail(15) 
        for index, row in derniers.iterrows():
            txt = f"- {row.get('Date','?')} à {row.get('Heure','?')} : {row.get('Activité','-')} (P:{row.get('Plaisir (0-10)','-')} M:{row.get('Maîtrise (0-10)','-')} S:{row.get('Satisfaction (0-10)','-')})"
            txt = txt.encode('latin-1', 'replace').decode('latin-1')
            pdf.chapter_body(txt)
    else:
        pdf.chapter_body("Aucune donnée.")
        
    # 4. PROBLÈMES
    pdf.chapter_title(f"4. Résolution de Problèmes - {len(problemes_df)} plans")
    if not problemes_df.empty:
        for index, row in problemes_df.iterrows():
            txt = (f"Problème : {row.get('Problème','-')}\n"
                   f"Solution choisie : {row.get('Solution Choisie','-')}\n"
                   f"Bilan prévu le : {row.get('Date Évaluation','?')}\n")
            txt = txt.encode('latin-1', 'replace').decode('latin-1')
            pdf.chapter_body(txt)
    else:
        pdf.chapter_body("Aucun plan.")

    return pdf.output(dest='S').encode('latin-1')