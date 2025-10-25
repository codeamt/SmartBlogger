import hashlib
from PyPDF2 import PdfReader


# Helper functions
def create_content_fingerprint(content: str) -> str:
    """Create hash for duplicate detection"""
    return hashlib.sha256(content.encode()).hexdigest()[:16]


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from PDF file"""
    try:
        with open(pdf_path, "rb") as f:
            reader = PdfReader(f)
            return "\n\n".join([page.extract_text() for page in reader.pages])
    except Exception as e:
        print(f"Error processing PDF: {e}")
        return ""