import os
import fitz
from docx import Document as DocxDocument


def extract_text_from_file(file_path):
    """
    Extract text from PDF, DOCX and TXT files.
    """

    extension = os.path.splitext(file_path)[1].lower()

    # PDF
    if extension == ".pdf":
        return extract_pdf_text(file_path)

    # DOCX
    elif extension == ".docx":
        return extract_docx_text(file_path)

    # TXT
    elif extension == ".txt":
        return extract_txt_text(file_path)

    else:
        return ""


def extract_pdf_text(file_path):
    text = ""

    pdf = fitz.open(file_path)

    for page_number, page in enumerate(pdf, start=1):
        page_text = page.get_text()

        if page_text:
            text += f"\n[Page {page_number}]\n"
            text += page_text

    pdf.close()

    return text.strip()


def extract_docx_text(file_path):
    document = DocxDocument(file_path)

    text = []

    for paragraph in document.paragraphs:
        if paragraph.text.strip():
            text.append(paragraph.text)

    return "\n".join(text).strip()


def extract_txt_text(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read().strip()