import io
import unittest
from zipfile import ZipFile

from file_tools import extract_file_text


class FileToolTests(unittest.TestCase):
    def test_extracts_supported_code_and_json_files(self):
        code_file = io.BytesIO(b"print('hello')")
        code_file.name = "example.py"
        self.assertEqual(extract_file_text(code_file), "print('hello')")

        json_file = io.BytesIO(b'{"ok": true}')
        json_file.name = "data.json"
        self.assertEqual(extract_file_text(json_file), '{"ok": true}')

    def test_extracts_docx_paragraph_text(self):
        document_bytes = io.BytesIO()
        with ZipFile(document_bytes, "w") as document:
            document.writestr(
                "word/document.xml",
                '<w:document xmlns:w="http://schemas.openxmlformats.org/'
                'wordprocessingml/2006/main"><w:body>'
                '<w:p><w:r><w:t>First paragraph</w:t></w:r></w:p>'
                '<w:p><w:r><w:t>Second paragraph</w:t></w:r></w:p>'
                '</w:body></w:document>',
            )

        uploaded_file = io.BytesIO(document_bytes.getvalue())
        uploaded_file.name = "notes.docx"
        self.assertEqual(
            extract_file_text(uploaded_file),
            "First paragraph\nSecond paragraph",
        )

    def test_rejects_invalid_docx_and_unsupported_formats(self):
        invalid_docx = io.BytesIO(b"not a zip")
        invalid_docx.name = "broken.docx"
        with self.assertRaisesRegex(ValueError, "could not be read"):
            extract_file_text(invalid_docx)

        unsupported = io.BytesIO(b"data")
        unsupported.name = "archive.zip"
        with self.assertRaisesRegex(ValueError, "Unsupported"):
            extract_file_text(unsupported)


if __name__ == "__main__":
    unittest.main()
