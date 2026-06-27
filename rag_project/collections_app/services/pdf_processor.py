import logging
import PyPDF2

logger = logging.getLogger('collections_app')


def extract_text(file_path: str) -> str:
    """
    Opens a PDF from disk and extracts all text page by page.
    Returns the full text as a single string.
    """
    logger.info(f"Extracting text from: {file_path}")
    text_parts = []

    with open(file_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        total_pages = len(reader.pages)
        logger.debug(f"PDF has {total_pages} pages")

        for i, page in enumerate(reader.pages):
            page_text = page.extract_text() or ''
            text_parts.append(page_text)
            logger.debug(f"Page {i + 1}/{total_pages}: extracted {len(page_text)} chars")

    full_text = '\n'.join(text_parts)
    logger.info(f"Total extracted text length: {len(full_text)} chars")
    return full_text