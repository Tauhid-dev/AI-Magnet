"""SSRF-safe URL validation helpers for website ingestion."""

from __future__ import annotations

import ipaddress
import socket
from dataclasses import dataclass
from urllib.parse import SplitResult, urlsplit, urlunsplit


BLOCKED_HOSTNAMES = {"localhost", "metadata.google.internal"}
BLOCKED_IP_ADDRESSES = {"169.254.169.254"}


class UnsafeUrlError(ValueError):
    """Raised when a URL is unsafe for crawler fetching."""


@dataclass(frozen=True)
class SafeUrl:
    """Normalized URL and host details approved for crawler use."""

    url: str
    host: str
    normalized_domain: str


def validate_public_http_url(
    raw_url: str,
    *,
    allowed_domain: str | None = None,
    resolve_dns: bool = True,
) -> SafeUrl:
    """Validate and normalize an HTTP(S) URL for server-side fetching."""
    parts = split_url(raw_url)
    if parts.scheme.lower() not in {"http", "https"}:
        raise UnsafeUrlError("Only http and https URLs are supported")
    if parts.username or parts.password:
        raise UnsafeUrlError("URLs with embedded credentials are not allowed")
    host = normalize_host(parts.hostname)
    if not host:
        raise UnsafeUrlError("URL must include a hostname")
    ensure_public_host(host, resolve_dns=resolve_dns)
    normalized_domain = host.lower()
    if allowed_domain and not domain_matches(normalized_domain, allowed_domain):
        raise UnsafeUrlError("URL host is not approved for this tenant source")

    path = parts.path or "/"
    normalized = urlunsplit(
        (
            parts.scheme.lower(),
            normalized_netloc(parts, host),
            path,
            parts.query,
            "",
        )
    )
    return SafeUrl(url=normalized, host=host, normalized_domain=normalized_domain)


def split_url(raw_url: str) -> SplitResult:
    """Split a raw URL after trimming surrounding whitespace."""
    raw = raw_url.strip()
    if len(raw) > 2000:
        raise UnsafeUrlError("URL is too long")
    try:
        return urlsplit(raw)
    except ValueError as exc:
        raise UnsafeUrlError("URL is invalid") from exc


def normalize_host(hostname: str | None) -> str:
    """Return a lowercase hostname without a trailing dot."""
    if hostname is None:
        return ""
    host = hostname.strip().rstrip(".").lower()
    if not host or len(host) > 253:
        raise UnsafeUrlError("URL hostname is invalid")
    return host


def normalized_netloc(parts: SplitResult, host: str) -> str:
    """Build a normalized netloc preserving non-default ports."""
    try:
        port = parts.port
    except ValueError as exc:
        raise UnsafeUrlError("URL port is invalid") from exc
    host_part = f"[{host}]" if ":" in host else host
    if port is None:
        return host_part
    default_port = (parts.scheme.lower() == "http" and port == 80) or (
        parts.scheme.lower() == "https" and port == 443
    )
    if default_port:
        return host_part
    return f"{host_part}:{port}"


def ensure_public_host(host: str, *, resolve_dns: bool = True) -> None:
    """Reject local, private, reserved, link-local, metadata, and unsafe DNS hosts."""
    if host in BLOCKED_HOSTNAMES or host.endswith(".localhost"):
        raise UnsafeUrlError("Local hostnames are not allowed")
    try:
        ip = ipaddress.ip_address(host.strip("[]"))
    except ValueError:
        ip = None
    if ip is not None:
        ensure_public_ip(ip)
        return
    if resolve_dns:
        addresses = resolve_host_addresses(host)
        if not addresses:
            raise UnsafeUrlError("Hostname did not resolve")
        for address in addresses:
            ensure_public_ip(address)


def resolve_host_addresses(host: str) -> list[ipaddress.IPv4Address | ipaddress.IPv6Address]:
    """Resolve all IP addresses for a host."""
    try:
        infos = socket.getaddrinfo(host, None, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise UnsafeUrlError("Hostname did not resolve") from exc
    addresses: list[ipaddress.IPv4Address | ipaddress.IPv6Address] = []
    for info in infos:
        address = info[4][0]
        try:
            addresses.append(ipaddress.ip_address(address))
        except ValueError as exc:
            raise UnsafeUrlError("Hostname resolved to an invalid address") from exc
    return addresses


def ensure_public_ip(ip: ipaddress.IPv4Address | ipaddress.IPv6Address) -> None:
    """Reject IPs that should never be reachable by the crawler."""
    if str(ip) in BLOCKED_IP_ADDRESSES:
        raise UnsafeUrlError("Cloud metadata IPs are not allowed")
    if (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_reserved
        or ip.is_unspecified
    ):
        raise UnsafeUrlError("Private or non-public IP addresses are not allowed")


def domain_matches(host: str, allowed_domain: str) -> bool:
    """Return true when host is the approved domain or one of its subdomains."""
    normalized_host = normalize_host(host)
    normalized_allowed = normalize_host(allowed_domain)
    return normalized_host == normalized_allowed or normalized_host.endswith(
        f".{normalized_allowed}"
    )
