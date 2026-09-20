from io import BytesIO

from pypdf import PdfReader


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extract text from all pages of a PDF.
    """

    if not file_bytes:
        raise ValueError("PDF file is empty")

    pdf_file = BytesIO(file_bytes)

    reader = PdfReader(pdf_file)

    extracted_text = []

    for page_number, page in enumerate(reader.pages, start=1):

        try:
            text = page.extract_text()

            if text:
                extracted_text.append(text)

        except Exception as error:
            print(
                f"Could not extract text from page "
                f"{page_number}: {error}"
            )

    return "\n\n".join(extracted_text)