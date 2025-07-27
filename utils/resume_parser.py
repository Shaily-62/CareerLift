import re
from pdfplumber import open as pdf_open

def extract_skills_from_pdf(file):
    skills_keywords = ['python', 'sql', 'excel', 'tensorflow', 'java', 'communication', 'machine learning']
    text = ""
    with pdf_open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
    text = text.lower()
    found_skills = [skill for skill in skills_keywords if skill in text]
    return list(set(found_skills))
