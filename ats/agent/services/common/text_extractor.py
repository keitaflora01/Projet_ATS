import os
from pathlib import Path

def extract_text_from_file(file_path):
    """
    Extrait le texte brut d'un fichier (PDF, DOCX, ODT, TXT).
    Retourne une chaîne ou vide en cas d'erreur.
    """
    path = Path(file_path)
    ext = path.suffix.lower()

    try:
        if ext == '.pdf':
            import pdfplumber
            with pdfplumber.open(path) as pdf:
                return "\n".join(page.extract_text() or "" for page in pdf.pages)

        elif ext in ['.docx', '.doc']:
            from docx import Document
            doc = Document(path)
            return "\n".join(para.text for para in doc.paragraphs if para.text.strip())

        elif ext == '.odt':
            # ODT nécessite odfpy (pip install odfpy)
            from odf import text, teletype
            from odf.opendocument import load
            doc = load(path)
            all_texts = teletype.extractText(doc)
            return all_texts

        elif ext == '.txt':
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()

        else:
            print(f"[TEXT EXTRACTOR] Format non supporté : {ext}")
            return ""

    except Exception as e:
        print(f"[TEXT EXTRACTOR ERROR] {str(e)} - File: {file_path}")
        return ""