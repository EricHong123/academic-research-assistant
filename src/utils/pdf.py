"""PDF processing utilities."""
import io
from typing import Optional
import fitz  # PyMuPDF


def extract_text_from_pdf(pdf_data: bytes) -> str:
    """Extract text from PDF bytes."""
    doc = fitz.open(stream=pdf_data, doc_type="pdf")
    text = "\n".join([page.get_text() for page in doc])
    doc.close()
    return text


def extract_text_from_file(file_path: str) -> str:
    """Extract text from PDF file."""
    doc = fitz.open(file_path)
    text = "\n".join([page.get_text() for page in doc])
    doc.close()
    return text


def get_pdf_info(pdf_data: bytes) -> dict:
    """Get PDF metadata."""
    doc = fitz.open(stream=pdf_data, doc_type="pdf")

    info = {
        "page_count": len(doc),
        "title": doc.metadata.get("title", ""),
        "author": doc.metadata.get("author", ""),
        "subject": doc.metadata.get("subject", ""),
        "creator": doc.metadata.get("creator", ""),
        "producer": doc.metadata.get("producer", ""),
        "creation_date": doc.metadata.get("creationDate", ""),
    }

    doc.close()
    return info


def extract_pages(pdf_data: bytes, pages: list[int]) -> bytes:
    """Extract specific pages from PDF."""
    src_doc = fitz.open(stream=pdf_data, doc_type="pdf")
    out_doc = fitz.open()

    for page_num in pages:
        if 0 <= page_num < len(src_doc):
            out_doc.insert_pdf(src_doc, from_page=page_num, to_page=page_num)

    output = io.BytesIO()
    out_doc.save(output)
    src_doc.close()
    out_doc.close()

    return output.getvalue()


def split_pdf(pdf_data: bytes) -> list[bytes]:
    """Split PDF into individual pages."""
    doc = fitz.open(stream=pdf_data, doc_type="pdf")
    pages = []

    for page_num in range(len(doc)):
        out_doc = fitz.open()
        out_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)

        output = io.BytesIO()
        out_doc.save(output)
        pages.append(output.getvalue())
        out_doc.close()

    doc.close()
    return pages


def extract_images(pdf_data: bytes) -> list[dict]:
    """Extract images from PDF."""
    doc = fitz.open(stream=pdf_data, doc_type="pdf")
    images = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        image_list = page.get_images()

        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = doc.extract_image(xref)

            images.append({
                "page": page_num + 1,
                "index": img_index,
                "width": base_image["width"],
                "height": base_image["height"],
                "colorspace": base_image["colorspace"],
                "bpc": base_image["bpc"],
                "data": base_image["image"],
            })

    doc.close()
    return images


def get_page_text(pdf_data: bytes, page_num: int) -> Optional[str]:
    """Get text from a specific page."""
    doc = fitz.open(stream=pdf_data, doc_type="pdf")

    if 0 <= page_num < len(doc):
        text = doc[page_num].get_text()
        doc.close()
        return text

    doc.close()
    return None


def search_in_pdf(pdf_data: bytes, query: str, case_sensitive: bool = False) -> list[dict]:
    """Search for text in PDF."""
    doc = fitz.open(stream=pdf_data, doc_type="pdf")
    results = []

    flags = 0 if case_sensitive else fitz.TEXT_PRESERVE_WHITESPACE

    for page_num in range(len(doc)):
        page = doc[page_num]
        text_instances = page.search_for(query, flags=flags)

        for rect in text_instances:
            results.append({
                "page": page_num + 1,
                "text": page.get_text("text", clip=rect).strip(),
                "bbox": {
                    "x0": rect.x0,
                    "y0": rect.y0,
                    "x1": rect.x1,
                    "y1": rect.y1,
                },
            })

    doc.close()
    return results
