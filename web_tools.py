from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, quote_plus, urlparse
from urllib.request import Request, urlopen


SEARCH_URL = "https://html.duckduckgo.com/html/"
MAX_RESPONSE_BYTES = 2 * 1024 * 1024


class WebSearchError(RuntimeError):
    """Raised when the web search provider cannot return usable results."""


class _DuckDuckGoResultsParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.results = []
        self._capture = None
        self._text = []
        self._current = None
        self._snippet_depth = 0

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        classes = set(attributes.get("class", "").split())

        if self._capture == "snippet":
            self._snippet_depth += 1
            return

        if tag == "a" and "result__a" in classes:
            self._current = {
                "url": _normalize_result_url(attributes.get("href", "")),
                "title": "",
                "snippet": "",
            }
            self._capture = "title"
            self._text = []
        elif "result__snippet" in classes and self.results:
            self._capture = "snippet"
            self._text = []
            self._snippet_depth = 1

    def handle_data(self, data):
        if self._capture:
            self._text.append(data)

    def handle_endtag(self, tag):
        if self._capture == "title" and tag == "a" and self._current:
            self._current["title"] = " ".join("".join(self._text).split())
            if self._current["title"] and self._current["url"]:
                self.results.append(self._current)
            self._current = None
            self._capture = None
            self._text = []
            return

        if self._capture == "snippet":
            self._snippet_depth -= 1
            if self._snippet_depth == 0 and self.results:
                self.results[-1]["snippet"] = " ".join(
                    "".join(self._text).split()
                )
                self._capture = None
                self._text = []


def _normalize_result_url(raw_url):
    if not raw_url:
        return ""

    parsed = urlparse(raw_url)
    if parsed.path == "/l/":
        raw_url = parse_qs(parsed.query).get("uddg", [""])[0]
        parsed = urlparse(raw_url)

    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return ""
    return raw_url


def web_search(query, max_results=5):
    """Search the public web and return a small set of linked results."""
    if not isinstance(query, str) or not query.strip() or len(query) > 500:
        raise ValueError("A search query must be between 1 and 500 characters.")
    if not isinstance(max_results, int) or not 1 <= max_results <= 5:
        raise ValueError("The result limit must be between 1 and 5.")

    request = Request(
        f"{SEARCH_URL}?q={quote_plus(query.strip())}",
        headers={"User-Agent": "PersonalAI/1.0 (web search)"},
    )
    try:
        with urlopen(request, timeout=10) as response:
            content = response.read(MAX_RESPONSE_BYTES + 1)
    except (HTTPError, URLError, TimeoutError, OSError) as error:
        raise WebSearchError(f"Web search failed: {error}") from error

    if len(content) > MAX_RESPONSE_BYTES:
        raise WebSearchError("The web search response was unexpectedly large.")

    parser = _DuckDuckGoResultsParser()
    parser.feed(content.decode("utf-8", errors="replace"))
    results = []
    seen_urls = set()
    for result in parser.results:
        if result["url"] in seen_urls:
            continue
        seen_urls.add(result["url"])
        results.append(result)
        if len(results) == max_results:
            break
    return results
