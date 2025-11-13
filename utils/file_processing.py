import hashlib
from PyPDF2 import PdfReader

# Try to import Image processor
try:
    from utils.ocr_processor import image_processor
    IMAGE_PROCESSING_AVAILABLE = True
except ImportError:
    IMAGE_PROCESSING_AVAILABLE = False
    print("Image processor not available")


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


def extract_text_from_image(image_path: str) -> str:
    """Extract text from image file using OCR"""
    if not IMAGE_PROCESSING_AVAILABLE:
        print(f"Image processing not available for processing image: {image_path}")
        return ""
    
    try:
        # Try to extract text using OCR
        text = image_processor.extract_text_from_image(image_path, mode="markdown")
        return text if text else ""
    except Exception as e:
        print(f"Error processing image with OCR: {e}")
        return ""


def is_image_file(file_path: str) -> bool:
    """Check if a file is an image that can be processed"""
    if not IMAGE_PROCESSING_AVAILABLE:
        return False
    return image_processor.is_image_file(file_path)