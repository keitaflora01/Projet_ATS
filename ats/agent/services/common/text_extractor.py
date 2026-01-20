from pathlib import Path

def extract_text_from_file(file_path: str) -> str:
    """
    Extrait texte brut d'un fichier (PDF, DOCX, ODT, TXT).
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
            from odf import text, teletype
            from odf.opendocument import load
            doc = load(path)
            return teletype.extractText(doc)

        elif ext == '.txt':
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()

        else:
            print(f"[EXTRACTOR] Format non supporté : {ext}")
            return ""

    except Exception as e:
        print(f"[EXTRACTOR ERROR] {str(e)} - Fichier: {file_path}")
        return ""