from io import BytesIO

from pypdf import PdfReader


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extract text from all pages of a PDF.

    Args:
        file_bytes: PDF file contents as bytes.

    Returns:
        Extracted text from the PDF.
    """

    pdf_file = BytesIO(file_bytes)

    reader = PdfReader(pdf_file)

    extracted_text = []

    for page in reader.pages:
        text = page.extract_text()

        if text:
            extracted_text.append(text)

    return "\n\n".join(extracted_text)