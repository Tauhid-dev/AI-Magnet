"""Minimal robots.txt policy support for safe crawler ingestion."""

from __future__ import annotations

from dataclasses import dataclass, field
from urllib.parse import urlsplit


@dataclass(frozen=True)
class RobotsPolicy:
    """Simple User-agent:* Disallow policy."""

    disallowed_paths: tuple[str, ...] = field(default_factory=tuple)

    def allows(self, url: str) -> bool:
        """Return whether a URL is allowed under the parsed disallow rules."""
        path = urlsplit(url).path or "/"
        for rule in self.disallowed_paths:
            if rule == "/":
                return False
            if rule and path.startswith(rule):
                return False
        return True

    @classmethod
    def parse(cls, content: bytes) -> "RobotsPolicy":
        """Parse a small, conservative subset of robots.txt."""
        lines = content.decode("utf-8", errors="replace").splitlines()
        active_for_star = False
        disallowed: list[str] = []
        for raw_line in lines:
            line = raw_line.split("#", 1)[0].strip()
            if not line or ":" not in line:
                continue
            key, value = [part.strip() for part in line.split(":", 1)]
            key = key.lower()
            if key == "user-agent":
                active_for_star = value == "*"
                continue
            if key == "disallow" and active_for_star and value:
                disallowed.append(value)
        return cls(tuple(disallowed))
