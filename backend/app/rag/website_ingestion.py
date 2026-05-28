"""Tenant-safe website and sitemap ingestion orchestration."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from urllib.parse import urlsplit, urlunsplit

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.db.base import utc_now
from app.models.knowledge import KnowledgeDocument, WebsiteCrawlPage, WebsiteSource
from app.models.tenant import Business
from app.providers.ai.base import EmbeddingProvider
from app.rag.ingestion import RagIngestionService
from app.rag.robots import RobotsPolicy
from app.rag.web_extraction import ExtractedPage, extract_html_page, parse_sitemap
from app.rag.web_fetcher import FetchResult, SafeWebFetcher, WebFetchError
from app.rag.web_security import UnsafeUrlError, domain_matches, validate_public_http_url
from app.usage import UsageService


SOURCE_TYPE_WEBSITE = "website"
SOURCE_TYPE_SITEMAP = "sitemap"
SOURCE_TYPES = {SOURCE_TYPE_WEBSITE, SOURCE_TYPE_SITEMAP}

WEBSITE_SOURCE_STATUS_QUEUED = "queued"
WEBSITE_SOURCE_STATUS_RUNNING = "running"
WEBSITE_SOURCE_STATUS_COMPLETED = "completed"
WEBSITE_SOURCE_STATUS_FAILED = "failed"

CRAWL_PAGE_STATUS_INGESTED = "ingested"
CRAWL_PAGE_STATUS_FAILED = "failed"
CRAWL_PAGE_STATUS_SKIPPED = "skipped"

DOCUMENT_SOURCE_TYPE_WEBSITE_PAGE = "website_page"
DOCUMENT_SOURCE_TYPE_SITEMAP_PAGE = "sitemap_page"


@dataclass(frozen=True)
class CrawlResult:
    """Summary of one website source crawl."""

    source_id: str
    status: str
    pages_discovered: int
    pages_ingested: int
    pages_failed: int
    pages_skipped: int


class WebsiteIngestionService:
    """Create, queue, crawl, and delete tenant-approved website sources."""

    def __init__(
        self,
        session: Session,
        *,
        settings: Settings | None = None,
        fetcher: SafeWebFetcher | None = None,
        embedding_provider: EmbeddingProvider | None = None,
        resolve_dns: bool = True,
    ) -> None:
        self.session = session
        self.settings = settings or get_settings()
        self.fetcher = fetcher or SafeWebFetcher(self.settings, resolve_dns=resolve_dns)
        self.embedding_provider = embedding_provider
        self.resolve_dns = resolve_dns

    def list_sources(self, tenant_id: str) -> list[WebsiteSource]:
        """List website/sitemap sources for a tenant."""
        return list(
            self.session.scalars(
                select(WebsiteSource)
                .where(WebsiteSource.tenant_id == tenant_id)
                .order_by(WebsiteSource.created_at.desc())
            )
        )

    def get_source(self, tenant_id: str, source_id: str) -> WebsiteSource | None:
        """Return one tenant-owned source."""
        return self.session.scalars(
            select(WebsiteSource).where(
                WebsiteSource.tenant_id == tenant_id,
                WebsiteSource.id == source_id,
            )
        ).first()

    def list_pages(self, tenant_id: str, source_id: str) -> list[WebsiteCrawlPage]:
        """List crawl page history for a tenant-owned source."""
        return list(
            self.session.scalars(
                select(WebsiteCrawlPage)
                .where(
                    WebsiteCrawlPage.tenant_id == tenant_id,
                    WebsiteCrawlPage.source_id == source_id,
                )
                .order_by(WebsiteCrawlPage.created_at.desc())
            )
        )

    def create_source(
        self,
        *,
        tenant_id: str,
        url: str,
        source_type: str,
        max_pages: int | None = None,
        max_depth: int | None = None,
    ) -> WebsiteSource:
        """Create a tenant-approved source after URL and domain validation."""
        if source_type not in SOURCE_TYPES:
            raise ValueError("source_type must be website or sitemap")
        requested_pages = bounded_int(max_pages, self.settings.website_crawl_max_pages, 1, 100)
        requested_depth = bounded_int(max_depth, self.settings.website_crawl_max_depth, 0, 5)
        safe_url = validate_public_http_url(url, resolve_dns=self.resolve_dns)
        approved_domain = self.approved_business_domain(tenant_id)
        if approved_domain and not domain_matches(safe_url.normalized_domain, approved_domain):
            raise ValueError("URL domain must match the business website domain")

        existing = self.session.scalars(
            select(WebsiteSource).where(
                WebsiteSource.tenant_id == tenant_id,
                WebsiteSource.root_url == safe_url.url,
            )
        ).first()
        if existing is not None:
            existing.source_type = source_type
            existing.max_pages = requested_pages
            existing.max_depth = requested_depth
            existing.status = WEBSITE_SOURCE_STATUS_QUEUED
            existing.last_error = None
            self.session.flush()
            return existing

        source = WebsiteSource(
            tenant_id=tenant_id,
            source_type=source_type,
            root_url=safe_url.url,
            normalized_domain=safe_url.normalized_domain,
            status=WEBSITE_SOURCE_STATUS_QUEUED,
            max_pages=requested_pages,
            max_depth=requested_depth,
        )
        self.session.add(source)
        self.session.flush()
        return source

    def set_source_job(self, source: WebsiteSource, job_id: str) -> WebsiteSource:
        """Attach the latest crawl job id to a source."""
        source.last_job_id = job_id
        source.status = WEBSITE_SOURCE_STATUS_QUEUED
        source.last_error = None
        self.session.flush()
        return source

    def delete_source(self, tenant_id: str, source_id: str) -> int:
        """Delete a tenant-owned source, pages, and generated knowledge documents."""
        source = self.get_source(tenant_id, source_id)
        if source is None:
            return 0
        documents = list(
            self.session.scalars(
                select(KnowledgeDocument).where(
                    KnowledgeDocument.tenant_id == tenant_id,
                    KnowledgeDocument.website_source_id == source_id,
                )
            )
        )
        pages = self.list_pages(tenant_id, source_id)
        deleted_count = len(documents) + len(pages) + 1
        for page in pages:
            self.session.delete(page)
        for document in documents:
            self.session.delete(document)
        self.session.delete(source)
        self.session.flush()
        return deleted_count

    def process_source(self, tenant_id: str, source_id: str) -> CrawlResult:
        """Fetch, extract, and ingest pages for a tenant-owned source."""
        source = self.get_source(tenant_id, source_id)
        if source is None:
            raise ValueError("Website source does not exist for this tenant")
        source.status = WEBSITE_SOURCE_STATUS_RUNNING
        source.last_error = None
        self.session.flush()

        try:
            if source.source_type == SOURCE_TYPE_SITEMAP:
                result = self._process_sitemap_source(source)
            else:
                result = self._process_website_source(source)
            if result.pages_ingested == 0:
                raise ValueError("No pages were safely ingested from this source")
        except Exception as exc:
            source.status = WEBSITE_SOURCE_STATUS_FAILED
            source.last_error = str(exc)[:2000]
            source.last_crawled_at = utc_now()
            self.session.flush()
            raise

        source.status = WEBSITE_SOURCE_STATUS_COMPLETED
        source.last_error = None
        source.last_crawled_at = utc_now()
        self.session.flush()
        return CrawlResult(
            source_id=result.source_id,
            status=WEBSITE_SOURCE_STATUS_COMPLETED,
            pages_discovered=result.pages_discovered,
            pages_ingested=result.pages_ingested,
            pages_failed=result.pages_failed,
            pages_skipped=result.pages_skipped,
        )

    def _process_website_source(self, source: WebsiteSource) -> CrawlResult:
        robots = self._load_robots(source)
        queue: list[tuple[str, int]] = [(source.root_url, 0)]
        seen: set[str] = set()
        ingested = failed = skipped = 0

        while queue and len(seen) < source.max_pages:
            url, depth = queue.pop(0)
            normalized = self._normalize_candidate_url(url, source.normalized_domain)
            if normalized is None or normalized in seen:
                continue
            seen.add(normalized)
            if robots is not None and not robots.allows(normalized):
                self._record_failed_page(
                    source,
                    url=normalized,
                    canonical_url=normalized,
                    status=CRAWL_PAGE_STATUS_SKIPPED,
                    error_message="Blocked by robots.txt",
                )
                skipped += 1
                continue

            try:
                fetch_result = self.fetcher.fetch_html(
                    normalized,
                    allowed_domain=source.normalized_domain,
                )
                page = extract_html_page(fetch_result.content, fetch_result.url)
                canonical = self._canonical_url(page, fetch_result.url, source.normalized_domain)
                self._ingest_page(
                    source,
                    fetch_result=fetch_result,
                    page=page,
                    canonical_url=canonical,
                    document_source_type=DOCUMENT_SOURCE_TYPE_WEBSITE_PAGE,
                )
                ingested += 1
                if depth < source.max_depth:
                    for link in page.links:
                        candidate = self._normalize_candidate_url(link, source.normalized_domain)
                        if candidate and candidate not in seen:
                            queue.append((candidate, depth + 1))
            except Exception as exc:
                self._record_failed_page(
                    source,
                    url=normalized,
                    canonical_url=normalized,
                    status=CRAWL_PAGE_STATUS_FAILED,
                    error_message=str(exc),
                )
                failed += 1

        return CrawlResult(source.id, source.status, len(seen), ingested, failed, skipped)

    def _process_sitemap_source(self, source: WebsiteSource) -> CrawlResult:
        page_urls = self._collect_sitemap_page_urls(source)
        robots = self._load_robots(source)
        ingested = failed = skipped = 0
        seen: set[str] = set()
        for url in page_urls[: source.max_pages]:
            normalized = self._normalize_candidate_url(url, source.normalized_domain)
            if normalized is None or normalized in seen:
                continue
            seen.add(normalized)
            if robots is not None and not robots.allows(normalized):
                self._record_failed_page(
                    source,
                    url=normalized,
                    canonical_url=normalized,
                    status=CRAWL_PAGE_STATUS_SKIPPED,
                    error_message="Blocked by robots.txt",
                )
                skipped += 1
                continue
            try:
                fetch_result = self.fetcher.fetch_html(
                    normalized,
                    allowed_domain=source.normalized_domain,
                )
                page = extract_html_page(fetch_result.content, fetch_result.url)
                canonical = self._canonical_url(page, fetch_result.url, source.normalized_domain)
                self._ingest_page(
                    source,
                    fetch_result=fetch_result,
                    page=page,
                    canonical_url=canonical,
                    document_source_type=DOCUMENT_SOURCE_TYPE_SITEMAP_PAGE,
                )
                ingested += 1
            except Exception as exc:
                self._record_failed_page(
                    source,
                    url=normalized,
                    canonical_url=normalized,
                    status=CRAWL_PAGE_STATUS_FAILED,
                    error_message=str(exc),
                )
                failed += 1
        return CrawlResult(source.id, source.status, len(seen), ingested, failed, skipped)

    def _collect_sitemap_page_urls(self, source: WebsiteSource) -> list[str]:
        sitemap_queue = [source.root_url]
        seen_sitemaps: set[str] = set()
        page_urls: list[str] = []
        while sitemap_queue and len(page_urls) < source.max_pages:
            sitemap_url = sitemap_queue.pop(0)
            normalized = self._normalize_candidate_url(sitemap_url, source.normalized_domain)
            if normalized is None or normalized in seen_sitemaps:
                continue
            seen_sitemaps.add(normalized)
            result = self.fetcher.fetch_sitemap(normalized, allowed_domain=source.normalized_domain)
            parsed = parse_sitemap(result.content)
            for nested_sitemap in parsed.sitemap_urls:
                nested = self._normalize_candidate_url(nested_sitemap, source.normalized_domain)
                if nested and nested not in seen_sitemaps:
                    sitemap_queue.append(nested)
            for page_url in parsed.page_urls:
                normalized_page = self._normalize_candidate_url(page_url, source.normalized_domain)
                if normalized_page and normalized_page not in page_urls:
                    page_urls.append(normalized_page)
                if len(page_urls) >= source.max_pages:
                    break
        return page_urls

    def _ingest_page(
        self,
        source: WebsiteSource,
        *,
        fetch_result: FetchResult,
        page: ExtractedPage,
        canonical_url: str,
        document_source_type: str,
    ) -> KnowledgeDocument:
        if not page.text:
            raise ValueError("Fetched page did not contain extractable text")
        content_hash = hashlib.sha256(page.text.encode("utf-8")).hexdigest()
        document = self._get_or_create_document(
            source,
            canonical_url=canonical_url,
            title=page.title,
            document_source_type=document_source_type,
            content_hash=content_hash,
        )
        RagIngestionService(
            self.session,
            embedding_provider=self.embedding_provider,
            settings=self.settings,
        ).process_document_bytes(
            document=document,
            content=page.text.encode("utf-8"),
            content_type="text/plain",
            raise_on_failure=True,
        )
        UsageService(self.session).record_document_ingestion(
            tenant_id=source.tenant_id,
            document_id=document.id,
            status=document.status,
            chunk_count=len(document.chunks),
        )
        self._record_ingested_page(
            source,
            url=fetch_result.url,
            canonical_url=canonical_url,
            title=page.title,
            http_status=fetch_result.status_code,
            document_id=document.id,
            content_hash=content_hash,
        )
        return document

    def _get_or_create_document(
        self,
        source: WebsiteSource,
        *,
        canonical_url: str,
        title: str | None,
        document_source_type: str,
        content_hash: str,
    ) -> KnowledgeDocument:
        document = self.session.scalars(
            select(KnowledgeDocument).where(
                KnowledgeDocument.tenant_id == source.tenant_id,
                KnowledgeDocument.website_source_id == source.id,
                KnowledgeDocument.source_url == canonical_url,
            )
        ).first()
        filename = source_filename(canonical_url, title)
        if document is None:
            document = RagIngestionService(
                self.session,
                embedding_provider=None,
                settings=self.settings,
            ).create_pending_document(
                tenant_id=source.tenant_id,
                filename=filename,
                content_type="text/plain",
                status="processing",
            )
        document.filename = filename
        document.content_type = "text/plain"
        document.source_type = document_source_type
        document.source_url = canonical_url
        document.source_title = title
        document.source_hash = content_hash
        document.website_source_id = source.id
        self.session.flush()
        return document

    def _record_ingested_page(
        self,
        source: WebsiteSource,
        *,
        url: str,
        canonical_url: str,
        title: str | None,
        http_status: int,
        document_id: str,
        content_hash: str,
    ) -> WebsiteCrawlPage:
        page = self._get_or_create_page(source, canonical_url)
        page.url = url
        page.title = title
        page.status = CRAWL_PAGE_STATUS_INGESTED
        page.http_status = http_status
        page.error_message = None
        page.document_id = document_id
        page.content_hash = content_hash
        page.crawled_at = utc_now()
        self.session.flush()
        return page

    def _record_failed_page(
        self,
        source: WebsiteSource,
        *,
        url: str,
        canonical_url: str,
        status: str,
        error_message: str,
    ) -> WebsiteCrawlPage:
        page = self._get_or_create_page(source, canonical_url)
        page.url = url
        page.status = status
        page.error_message = error_message[:2000]
        page.crawled_at = utc_now()
        self.session.flush()
        return page

    def _get_or_create_page(self, source: WebsiteSource, canonical_url: str) -> WebsiteCrawlPage:
        page = self.session.scalars(
            select(WebsiteCrawlPage).where(
                WebsiteCrawlPage.tenant_id == source.tenant_id,
                WebsiteCrawlPage.source_id == source.id,
                WebsiteCrawlPage.canonical_url == canonical_url,
            )
        ).first()
        if page is None:
            page = WebsiteCrawlPage(
                tenant_id=source.tenant_id,
                source_id=source.id,
                url=canonical_url,
                canonical_url=canonical_url,
                status="queued",
            )
            self.session.add(page)
        return page

    def _load_robots(self, source: WebsiteSource) -> RobotsPolicy | None:
        if not self.settings.website_crawl_respect_robots:
            return None
        robots_url = robots_url_for(source.root_url)
        if robots_url is None:
            return None
        try:
            result = self.fetcher.fetch_html(robots_url, allowed_domain=source.normalized_domain)
        except (UnsafeUrlError, WebFetchError):
            return RobotsPolicy()
        return RobotsPolicy.parse(result.content)

    def _normalize_candidate_url(self, url: str, allowed_domain: str) -> str | None:
        try:
            safe = validate_public_http_url(
                strip_fragment(url),
                allowed_domain=allowed_domain,
                resolve_dns=self.resolve_dns,
            )
        except UnsafeUrlError:
            return None
        return safe.url

    def _canonical_url(
        self,
        page: ExtractedPage,
        fallback_url: str,
        allowed_domain: str,
    ) -> str:
        if not page.canonical_url:
            return self._normalize_candidate_url(fallback_url, allowed_domain) or fallback_url
        normalized = self._normalize_candidate_url(page.canonical_url, allowed_domain)
        return normalized or (self._normalize_candidate_url(fallback_url, allowed_domain) or fallback_url)

    def approved_business_domain(self, tenant_id: str) -> str | None:
        """Return the tenant's business website domain when configured."""
        business = self.session.scalars(
            select(Business)
            .where(Business.tenant_id == tenant_id, Business.website_url.is_not(None))
            .order_by(Business.created_at.asc())
        ).first()
        if business is None or not business.website_url:
            return None
        try:
            return validate_public_http_url(
                business.website_url,
                resolve_dns=False,
            ).normalized_domain
        except UnsafeUrlError:
            return None


def robots_url_for(root_url: str) -> str | None:
    """Return the robots.txt URL for a source root URL."""
    parts = urlsplit(root_url)
    if not parts.scheme or not parts.netloc:
        return None
    return urlunsplit((parts.scheme, parts.netloc, "/robots.txt", "", ""))


def strip_fragment(url: str) -> str:
    """Remove URL fragments before crawl deduplication."""
    parts = urlsplit(url)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, parts.query, ""))


def bounded_int(value: int | None, default: int, minimum: int, maximum: int) -> int:
    """Clamp optional integer settings to a safe range."""
    if value is None:
        candidate = default
    else:
        candidate = value
    return min(max(candidate, minimum), maximum)


def source_filename(url: str, title: str | None) -> str:
    """Create a readable bounded filename for a crawled page."""
    if title:
        base = title
    else:
        parts = urlsplit(url)
        base = parts.path.strip("/") or parts.hostname or "website-page"
    safe = "".join(
        character if character.isalnum() or character in " ._-" else "-" for character in base
    )
    safe = " ".join(safe.split()).strip(" ._-") or "website-page"
    return f"{safe[:220]}.txt"
