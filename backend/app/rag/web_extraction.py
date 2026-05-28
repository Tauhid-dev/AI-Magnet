"""HTML and sitemap extraction helpers for website ingestion."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from html.parser import HTMLParser
from urllib.parse import urljoin

from defusedxml import ElementTree as ET


WHITESPACE_RE = re.compile(r"\s+")


@dataclass(frozen=True)
class ExtractedPage:
    """Text, title, canonical URL, and links extracted from one HTML page."""

    title: str | None
    text: str
    links: list[str]
    canonical_url: str | None


@dataclass(frozen=True)
class SitemapParseResult:
    """URLs discovered from a sitemap document."""

    page_urls: list[str] = field(default_factory=list)
    sitemap_urls: list[str] = field(default_factory=list)


class PageTextParser(HTMLParser):
    """Small HTML parser that extracts visible text and discoverable URLs."""

    def __init__(self, base_url: str) -> None:
        super().__init__(convert_charrefs=True)
        self.base_url = base_url
        self._ignored_depth = 0
        self._in_title = False
        self._title_parts: list[str] = []
        self._text_parts: list[str] = []
        self.links: list[str] = []
        self.canonical_url: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag_name = tag.lower()
        attr_map = {key.lower(): value for key, value in attrs if value}
        if tag_name in {"script", "style", "noscript", "svg", "canvas"}:
            self._ignored_depth += 1
            return
        if tag_name == "title":
            self._in_title = True
            return
        if tag_name == "a" and attr_map.get("href"):
            self.links.append(urljoin(self.base_url, attr_map["href"]))
            return
        if tag_name == "link":
            rel = {item.strip().lower() for item in (attr_map.get("rel") or "").split()}
            href = attr_map.get("href")
            if href and "canonical" in rel:
                self.canonical_url = urljoin(self.base_url, href)

    def handle_endtag(self, tag: str) -> None:
        tag_name = tag.lower()
        if tag_name in {"script", "style", "noscript", "svg", "canvas"}:
            self._ignored_depth = max(self._ignored_depth - 1, 0)
            return
        if tag_name == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        if self._ignored_depth:
            return
        text = sanitize_text(data)
        if not text:
            return
        if self._in_title:
            self._title_parts.append(text)
        self._text_parts.append(text)

    @property
    def title(self) -> str | None:
        title = sanitize_text(" ".join(self._title_parts))
        return title[:500] if title else None

    @property
    def text(self) -> str:
        return sanitize_text(" ".join(self._text_parts))


def extract_html_page(content: bytes, base_url: str) -> ExtractedPage:
    """Extract human-readable page text and links from HTML bytes."""
    html = content.decode("utf-8", errors="replace")
    parser = PageTextParser(base_url)
    parser.feed(html)
    return ExtractedPage(
        title=parser.title,
        text=parser.text,
        links=dedupe_preserve_order(parser.links),
        canonical_url=parser.canonical_url,
    )


def parse_sitemap(content: bytes) -> SitemapParseResult:
    """Parse a sitemap urlset or sitemapindex document."""
    try:
        root = ET.fromstring(content)
    except ET.ParseError as exc:
        raise ValueError("Sitemap XML could not be parsed") from exc

    page_urls: list[str] = []
    sitemap_urls: list[str] = []
    root_name = local_name(root.tag)
    for child in root:
        child_name = local_name(child.tag)
        loc = first_child_text(child, "loc")
        if not loc:
            continue
        if root_name == "sitemapindex" or child_name == "sitemap":
            sitemap_urls.append(loc.strip())
        elif root_name == "urlset" or child_name == "url":
            page_urls.append(loc.strip())
    return SitemapParseResult(
        page_urls=dedupe_preserve_order(page_urls),
        sitemap_urls=dedupe_preserve_order(sitemap_urls),
    )


def local_name(tag: str) -> str:
    """Return an XML tag's local name without namespace."""
    return tag.rsplit("}", 1)[-1].lower()


def first_child_text(element: ET.Element, child_name: str) -> str | None:
    """Return text from the first direct child matching a local tag name."""
    for child in element:
        if local_name(child.tag) == child_name and child.text:
            return child.text
    return None


def sanitize_text(value: str) -> str:
    """Collapse whitespace and strip text extracted from untrusted HTML."""
    return WHITESPACE_RE.sub(" ", value.replace("\x00", " ")).strip()


def dedupe_preserve_order(values: list[str]) -> list[str]:
    """Return values once in first-seen order."""
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result
