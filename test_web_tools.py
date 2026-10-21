import io
import unittest
from unittest.mock import patch

from web_tools import WebSearchError, _DuckDuckGoResultsParser, web_search


class WebSearchTests(unittest.TestCase):
    def test_parser_extracts_results_and_unwraps_provider_links(self):
        parser = _DuckDuckGoResultsParser()
        parser.feed(
            '<div class="result">'
            '<a class="result__a" href="/l/?uddg='
            'https%3A%2F%2Fexample.com%2Farticle">Example <b>Title</b></a>'
            '<div class="result__snippet">Useful <b>summary</b> text</div>'
            '</div>'
        )

        self.assertEqual(
            parser.results,
            [{
                "title": "Example Title",
                "url": "https://example.com/article",
                "snippet": "Useful summary text",
            }],
        )

    def test_search_returns_bounded_results(self):
        markup = (
            '<a class="result__a" href="https://example.com/1">One</a>'
            '<div class="result__snippet">First result</div>'
            '<a class="result__a" href="https://example.com/2">Two</a>'
            '<div class="result__snippet">Second result</div>'
        ).encode()
        with patch("web_tools.urlopen", return_value=io.BytesIO(markup)):
            results = web_search("test query", max_results=1)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "One")
        self.assertEqual(results[0]["snippet"], "First result")

    def test_search_rejects_invalid_input_and_reports_provider_errors(self):
        with self.assertRaisesRegex(ValueError, "search query"):
            web_search("")

        with patch(
            "web_tools.urlopen",
            side_effect=TimeoutError("provider timed out"),
        ):
            with self.assertRaisesRegex(WebSearchError, "provider timed out"):
                web_search("test query")


if __name__ == "__main__":
    unittest.main()
