# extractor.py
import pdfplumber
from docx import Document
import re

# -------- Extract text from PDF --------
def extract_text_from_pdf(filepath: str) -> str:
    text = ""
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
            text += "\n"
    return text.strip()

# -------- Extract text from DOCX --------
def extract_text_from_docx(filepath: str) -> str:
    doc = Document(filepath)
    text = "\n".join([p.text for p in doc.paragraphs])
    return text.strip()

# -------- Parse Events (simple regex logic) --------
def extract_events(text: str):
    """
    Very simple event extractor.
    Looks for lines like:
      'ARRIVAL - 01/01/2023 08:00 - 01/01/2023 09:00'
    and parses them into structured dicts.
    """

    events = []
    lines = text.splitlines()

    # Regex: EVENT - START - END
    pattern = re.compile(r"(?P<event>[A-Za-z ]+)\s*-\s*(?P<start>[\d/: ]+)\s*-\s*(?P<end>[\d/: ]+)")

    for line in lines:
        match = pattern.search(line)
        if match:
            events.append({
                "event": match.group("event").strip(),
                "start": match.group("start").strip(),
                "end": match.group("end").strip()
            })

    # Fallback if no matches
    if not events:
        events.append({"event": "NO_EVENTS_FOUND", "start": "", "end": ""})

    return events#
