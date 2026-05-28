"""Bounded HTTP fetcher for tenant-approved website ingestion."""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urljoin

import httpx

from app.core.config import Settings
from app.rag.web_security import SafeUrl, validate_public_http_url


HTML_CONTENT_TYPES = {
    "text/html",
    "application/xhtml+xml",
    "text/plain",
}
SITEMAP_CONTENT_TYPES = {
    "application/xml",
    "text/xml",
    "application/rss+xml",
    "application/x-xml",
    "text/plain",
}


class WebFetchError(RuntimeError):
    """Raised when a safe fetch fails."""


@dataclass(frozen=True)
class FetchResult:
    """Fetched HTTP response data after redirect validation and byte limits."""

    url: str
    status_code: int
    content_type: str | None
    content: bytes


class SafeWebFetcher:
    """HTTP client that validates every URL and redirect before fetching."""

    def __init__(
        self,
        settings: Settings,
        *,
        client: httpx.Client | None = None,
        resolve_dns: bool = True,
    ) -> None:
        self.settings = settings
        self.client = client or httpx.Client(timeout=settings.website_crawl_timeout_seconds)
        self.resolve_dns = resolve_dns

    def fetch_html(self, url: str, *, allowed_domain: str) -> FetchResult:
        """Fetch one HTML-like page from an approved public domain."""
        return self.fetch(
            url,
            allowed_domain=allowed_domain,
            accepted_content_types=HTML_CONTENT_TYPES,
        )

    def fetch_sitemap(self, url: str, *, allowed_domain: str) -> FetchResult:
        """Fetch one XML sitemap from an approved public domain."""
        return self.fetch(
            url,
            allowed_domain=allowed_domain,
            accepted_content_types=SITEMAP_CONTENT_TYPES,
        )

    def fetch(
        self,
        url: str,
        *,
        allowed_domain: str,
        accepted_content_types: set[str],
    ) -> FetchResult:
        """Fetch content after validating the URL, DNS, redirects, and size."""
        current = validate_public_http_url(
            url,
            allowed_domain=allowed_domain,
            resolve_dns=self.resolve_dns,
        )
        for _redirect_count in range(self.settings.website_crawl_max_redirects + 1):
            response = self._request(current)
            if response.status_code in {301, 302, 303, 307, 308}:
                location = response.headers.get("location")
                response.close()
                if not location:
                    raise WebFetchError("Redirect response did not include a location")
                current = validate_public_http_url(
                    urljoin(current.url, location),
                    allowed_domain=allowed_domain,
                    resolve_dns=self.resolve_dns,
                )
                continue
            content_type = normalized_content_type(response.headers.get("content-type"))
            if response.status_code >= 400:
                response.close()
                raise WebFetchError(f"HTTP {response.status_code} while fetching source")
            if content_type and content_type not in accepted_content_types:
                response.close()
                raise WebFetchError(f"Unsupported content type: {content_type}")
            content = self._read_limited(response)
            return FetchResult(
                url=str(response.url),
                status_code=response.status_code,
                content_type=content_type,
                content=content,
            )
        raise WebFetchError("Too many redirects while fetching source")

    def _request(self, safe_url: SafeUrl) -> httpx.Response:
        try:
            request = self.client.build_request(
                "GET",
                safe_url.url,
                headers={
                    "User-Agent": self.settings.website_crawl_user_agent,
                    "Accept": "text/html,application/xhtml+xml,application/xml,text/xml;q=0.9,*/*;q=0.1",
                },
            )
            return self.client.send(request, follow_redirects=False, stream=True)
        except httpx.HTTPError as exc:
            raise WebFetchError(str(exc)) from exc

    def _read_limited(self, response: httpx.Response) -> bytes:
        maximum = self.settings.website_crawl_max_bytes
        content_length = response.headers.get("content-length")
        if content_length is not None:
            try:
                if int(content_length) > maximum:
                    response.close()
                    raise WebFetchError("Fetched content exceeds configured byte limit")
            except ValueError:
                pass
        chunks: list[bytes] = []
        total_bytes = 0
        try:
            for chunk in response.iter_bytes():
                total_bytes += len(chunk)
                if total_bytes > maximum:
                    raise WebFetchError("Fetched content exceeds configured byte limit")
                chunks.append(chunk)
        finally:
            response.close()
        return b"".join(chunks)


def normalized_content_type(value: str | None) -> str | None:
    """Normalize a Content-Type header to its media type."""
    if value is None:
        return None
    media_type = value.split(";")[0].strip().lower()
    return media_type or None
