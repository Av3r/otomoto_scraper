"""Small helper utilities used by the parser and tests.

Helpers perform small, well-defined transformations and intentionally
return `None` when parsing fails.
"""

import hashlib
import re
from typing import Optional
from urllib.parse import urljoin


def parse_float_from_text(s: Optional[str]) -> Optional[float]:
    """Parse a localized number string and return a float or None.

    Examples: "89 000 zł" -> 89000.0, "48 500 PLN" -> 48500.0
    """
    if not s:
        return None
    # "89 000 zł" -> "89000"
    digits = re.sub(r"[^\d.,]", "", s).replace(",", ".")
    # remove thousand separators (spaces)
    digits = re.sub(r"\s+", "", digits)
    try:
        return float(digits)
    except ValueError:
        return None


def parse_int_from_text(s: Optional[str]) -> Optional[int]:
    """Return integer parsed from a string or None if parsing fails."""
    if not s:
        return None
    digits = re.sub(r"[^\d]", "", s)
    try:
        return int(digits) if digits else None
    except ValueError:
        return None


def extract_currency(s: Optional[str]) -> Optional[str]:
    """Extract currency code from a string if present (e.g. PLN, EUR)."""
    if not s:
        return None
    s = s.strip()
    m = re.search(r"([A-Z]{2,4}|zł|PLN|EUR|USD)", s, re.I)
    if m:
        cur = m.group(0).upper()
        if cur == "ZŁ":
            return "PLN"
        return cur
    return None


def make_id_from_url_or_hash(url: Optional[str], title: Optional[str]) -> str:
    """Return an ID parsed from an Otomoto URL or a stable short hash."""
    if url:
        m = re.search(r"/oferta/(\d+)", url)
        if m:
            return m.group(1)
    # fallback stable short hash
    raw = (url or "") + "|" + (title or "")
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:12]


def absolute_url(base: str, href: Optional[str]) -> Optional[str]:
    """Return an absolute URL given a base and a possibly-relative href."""
    if not href:
        return None
    return urljoin(base, href)
