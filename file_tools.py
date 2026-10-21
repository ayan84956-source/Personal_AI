import base64
from io import BytesIO
from pathlib import Path
from xml.etree import ElementTree
from zipfile import BadZipFile, ZipFile

from PIL import Image
from pypdf import PdfReader


MAX_TEXT_CHARS = 20000
MAX_IMAGE_BYTES = 10 * 1024 * 1024
MAX_DOCX_XML_BYTES = 2 * 1024 * 1024
TEXT_EXTENSIONS = {
    ".txt", ".md", ".csv", ".json", ".py", ".js", ".ts", ".tsx",
    ".jsx", ".html", ".css", ".xml", ".yaml", ".yml", ".log", ".sql",
}


def extract_file_text(uploaded_file):
    """Extract readable text from supported documents."""

    name = uploaded_file.name.lower()
    raw = uploaded_file.getvalue()

    if name.endswith(".pdf"):
        reader = PdfReader(BytesIO(raw))
        pages = []

        for page_number, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            pages.append(f"Page {page_number}:\n{text}")

        result = "\n\n".join(pages)

        if not result.strip():
            return (
                "No selectable text was found in this PDF. "
                "It may be a scanned document."
            )

        return result[:MAX_TEXT_CHARS]

    suffix = Path(name).suffix
    if suffix in TEXT_EXTENSIONS:
        return raw.decode("utf-8", errors="replace")[:MAX_TEXT_CHARS]

    if suffix == ".docx":
        try:
            with ZipFile(BytesIO(raw)) as document:
                if (
                    document.getinfo("word/document.xml").file_size
                    > MAX_DOCX_XML_BYTES
                ):
                    raise ValueError(
                        "The Word document contains too much text to process."
                    )
                xml = document.read("word/document.xml")
        except (BadZipFile, KeyError) as error:
            raise ValueError("The Word document could not be read.") from error

        try:
            root = ElementTree.fromstring(xml)
        except ElementTree.ParseError as error:
            raise ValueError(
                "The Word document contains invalid content."
            ) from error

        namespace = {
            "word": "http://schemas.openxmlformats.org/"
            "wordprocessingml/2006/main"
        }
        paragraphs = []
        for paragraph in root.findall(".//word:p", namespace):
            text = "".join(
                node.text or ""
                for node in paragraph.findall(".//word:t", namespace)
            )
            if text:
                paragraphs.append(text)
        result = "\n".join(paragraphs)
        return (
            result[:MAX_TEXT_CHARS]
            or "No readable text was found in this document."
        )

    raise ValueError("Unsupported document format.")


def image_to_data_url(uploaded_file):
    """Prepare an uploaded image for Groq vision."""

    raw = uploaded_file.getvalue()

    if len(raw) > MAX_IMAGE_BYTES:
        raise ValueError("Image must be 10 MB or smaller.")

    with Image.open(BytesIO(raw)) as image:
        image = image.convert("RGB")
        image.thumbnail((1600, 1600))

        output = BytesIO()
        image.save(output, format="JPEG", quality=85)
        encoded = base64.b64encode(output.getvalue()).decode("utf-8")

    return f"data:image/jpeg;base64,{encoded}"

def is_image(uploaded_file):
    return Path(uploaded_file.name).suffix.lower() in {
        ".png", ".jpg", ".jpeg"
    }