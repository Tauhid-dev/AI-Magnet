import socket

import httpx
import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from app.core.config import Settings, get_settings
from app.core.passwords import hash_password
from app.core.rate_limit import rate_limiter
from app.db.base import Base, utc_now
from app.db.session import get_db_session
from app.jobs.service import JOB_TYPE_RAG_WEBSITE_CRAWL
from app.main import create_app
from app.models import BusinessUser, KnowledgeDocument, WebsiteCrawlPage, WebsiteSource
from app.providers.ai.factory import get_embedding_provider
from app.rag.web_fetcher import FetchResult, SafeWebFetcher, WebFetchError
from app.rag.web_security import UnsafeUrlError, validate_public_http_url
from app.rag.website_ingestion import WebsiteIngestionService
from app.tenants.service import TenantService
from fastapi.testclient import TestClient


class FakeFetcher:
    def __init__(self, responses: dict[str, FetchResult]) -> None:
        self.responses = responses

    def fetch_html(self, url: str, *, allowed_domain: str) -> FetchResult:
        del allowed_domain
        result = self.responses.get(url)
        if result is None:
            raise RuntimeError(f"missing fake response for {url}")
        return result

    def fetch_sitemap(self, url: str, *, allowed_domain: str) -> FetchResult:
        return self.fetch_html(url, allowed_domain=allowed_domain)


def create_test_session():
    engine = create_engine(
        "sqlite:///:memory:",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, future=True, expire_on_commit=False)
    return session_factory()


def seed_business_user(session, *, website_url: str | None = "https://example.com"):
    tenant_service = TenantService(session)
    tenant = tenant_service.create_tenant("Demo Plumbing", "demo-plumbing")
    business = tenant_service.create_business(
        tenant_id=tenant.id,
        name="Demo Plumbing",
        email="owner@example.test",
        website_url=website_url,
    )
    user = BusinessUser(
        tenant_id=tenant.id,
        business_id=business.id,
        email="owner@example.test",
        full_name="Demo Owner",
        role="owner",
        status="active",
        password_hash=hash_password("correct-password"),
        password_updated_at=utc_now(),
    )
    session.add(user)
    session.flush()
    return tenant, user


def create_client(session, monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "test")
    monkeypatch.setenv("AI_EMBEDDING_DIMENSIONS", "16")
    monkeypatch.setenv("BUSINESS_PORTAL_SESSION_SECRET", "test-secret")
    monkeypatch.setattr("app.jobs.redis_queue.RedisWakeQueue.notify", lambda *_args: True)
    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda *_args, **_kwargs: [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 0))],
    )
    rate_limiter.reset()
    get_settings.cache_clear()
    app = create_app()

    def override_db():
        yield session

    app.dependency_overrides[get_db_session] = override_db
    return TestClient(app)


def login(client: TestClient) -> str:
    response = client.post(
        "/business-portal/auth/login",
        json={
            "tenant_slug": "demo-plumbing",
            "email": "owner@example.test",
            "password": "correct-password",
        },
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.parametrize(
    "url",
    [
        "file:///etc/passwd",
        "http://localhost/admin",
        "http://127.0.0.1/admin",
        "http://[::1]/admin",
        "http://169.254.169.254/latest/meta-data",
        "ftp://example.com/file",
    ],
)
def test_validate_public_http_url_rejects_unsafe_targets(url):
    with pytest.raises(UnsafeUrlError):
        validate_public_http_url(url, resolve_dns=False)


def test_validate_public_http_url_rejects_private_dns_resolution(monkeypatch):
    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda *_args, **_kwargs: [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("10.0.0.5", 0))],
    )

    with pytest.raises(UnsafeUrlError):
        validate_public_http_url("https://customer.example")


def test_safe_fetcher_rejects_redirect_to_private_address():
    def handler(request: httpx.Request) -> httpx.Response:
        assert str(request.url) == "https://example.com/start"
        return httpx.Response(302, headers={"location": "http://127.0.0.1/private"})

    settings = Settings(website_crawl_max_redirects=1)
    fetcher = SafeWebFetcher(
        settings,
        client=httpx.Client(transport=httpx.MockTransport(handler)),
        resolve_dns=False,
    )

    with pytest.raises(UnsafeUrlError):
        fetcher.fetch_html("https://example.com/start", allowed_domain="example.com")


def test_safe_fetcher_enforces_response_byte_limit():
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, headers={"content-type": "text/html"}, content=b"12345")

    settings = Settings(website_crawl_max_bytes=4)
    fetcher = SafeWebFetcher(
        settings,
        client=httpx.Client(transport=httpx.MockTransport(handler)),
        resolve_dns=False,
    )

    with pytest.raises(WebFetchError):
        fetcher.fetch_html("https://example.com/", allowed_domain="example.com")


def test_website_source_processes_pages_into_tenant_documents():
    settings = Settings(
        ai_provider="test",
        ai_embedding_dimensions=16,
        rag_chunk_size=8,
        rag_chunk_overlap=2,
        website_crawl_respect_robots=True,
    )
    with create_test_session() as session:
        tenant, _user = seed_business_user(session)
        service = WebsiteIngestionService(
            session,
            settings=settings,
            fetcher=FakeFetcher(
                {
                    "https://example.com/robots.txt": FetchResult(
                        url="https://example.com/robots.txt",
                        status_code=200,
                        content_type="text/plain",
                        content=b"",
                    ),
                    "https://example.com/": FetchResult(
                        url="https://example.com/",
                        status_code=200,
                        content_type="text/html",
                        content=(
                            b"<html><head><title>Demo Plumbing</title></head>"
                            b"<body><h1>Emergency plumbing</h1>"
                            b"<p>Blocked drains hot water repairs Bondi Sydney service.</p>"
                            b"</body></html>"
                        ),
                    ),
                }
            ),
            embedding_provider=get_embedding_provider(settings),
            resolve_dns=False,
        )
        source = service.create_source(
            tenant_id=tenant.id,
            url="https://example.com/",
            source_type="website",
        )
        result = service.process_source(tenant.id, source.id)
        session.commit()

        documents = list(session.scalars(select(KnowledgeDocument)))
        pages = list(session.scalars(select(WebsiteCrawlPage)))

        assert result.pages_ingested == 1
        assert source.status == "completed"
        assert documents[0].tenant_id == tenant.id
        assert documents[0].source_type == "website_page"
        assert documents[0].source_url == "https://example.com/"
        assert documents[0].source_title == "Demo Plumbing"
        assert documents[0].status == "ingested"
        assert pages[0].status == "ingested"
        assert pages[0].document_id == documents[0].id


def test_sitemap_source_indexes_only_approved_domain_pages():
    settings = Settings(
        ai_provider="test",
        ai_embedding_dimensions=16,
        rag_chunk_size=8,
        rag_chunk_overlap=2,
        website_crawl_respect_robots=False,
    )
    with create_test_session() as session:
        tenant, _user = seed_business_user(session)
        service = WebsiteIngestionService(
            session,
            settings=settings,
            fetcher=FakeFetcher(
                {
                    "https://example.com/sitemap.xml": FetchResult(
                        url="https://example.com/sitemap.xml",
                        status_code=200,
                        content_type="application/xml",
                        content=(
                            b"<urlset><url><loc>https://example.com/services</loc></url>"
                            b"<url><loc>https://evil.example/services</loc></url></urlset>"
                        ),
                    ),
                    "https://example.com/services": FetchResult(
                        url="https://example.com/services",
                        status_code=200,
                        content_type="text/html",
                        content=b"<html><title>Services</title><p>Drain cleaning and tap repairs.</p></html>",
                    ),
                }
            ),
            embedding_provider=get_embedding_provider(settings),
            resolve_dns=False,
        )
        source = service.create_source(
            tenant_id=tenant.id,
            url="https://example.com/sitemap.xml",
            source_type="sitemap",
        )
        result = service.process_source(tenant.id, source.id)
        session.commit()

        pages = list(session.scalars(select(WebsiteCrawlPage)))

        assert result.pages_ingested == 1
        assert len(pages) == 1
        assert pages[0].canonical_url == "https://example.com/services"


def test_business_website_domain_authorizes_source_submission():
    with create_test_session() as session:
        tenant, _user = seed_business_user(session, website_url="https://approved.example")
        service = WebsiteIngestionService(session, resolve_dns=False)

        with pytest.raises(ValueError):
            service.create_source(
                tenant_id=tenant.id,
                url="https://other.example",
                source_type="website",
            )


def test_business_portal_website_source_api_queues_tenant_job(monkeypatch):
    with create_test_session() as session:
        tenant, _user = seed_business_user(session)
        session.commit()
        client = create_client(session, monkeypatch)
        token = login(client)

        response = client.post(
            "/business-portal/website-sources",
            headers=auth_header(token),
            json={
                "source_type": "sitemap",
                "url": "https://example.com/sitemap.xml",
                "max_pages": 5,
                "max_depth": 0,
            },
        )
        jobs_response = client.get("/business-portal/jobs", headers=auth_header(token))

        assert response.status_code == 200
        payload = response.json()
        assert payload["status"] == "queued"
        assert payload["last_job_id"]
        assert payload["normalized_domain"] == "example.com"
        assert jobs_response.json()[0]["job_type"] == JOB_TYPE_RAG_WEBSITE_CRAWL
        source = session.scalars(select(WebsiteSource)).one()
        assert source.tenant_id == tenant.id
        assert source.last_job_id == payload["last_job_id"]
