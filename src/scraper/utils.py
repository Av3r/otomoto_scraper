import re
from typing import Optional
from urllib.parse import urljoin
import hashlib

def parse_float_from_text(s: Optional[str]) -> Optional[float]:
    if not s:
        return None
    # "89 000 zł" -> "89000"
    digits = re.sub(r"[^\d.,]", "", s).replace(",", ".")
    # remove thousand separators (spaces)
    digits = re.sub(r"\s+", "", digits)
    try:
        return float(digits)
    except Exception:
        return None

def parse_int_from_text(s: Optional[str]) -> Optional[int]:
    if not s:
        return None
    digits = re.sub(r"[^\d]", "", s)
    return int(digits) if digits else None

def extract_currency(s: Optional[str]) -> Optional[str]:
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
    if url:
        m = re.search(r"/oferta/(\d+)", url)
        if m:
            return m.group(1)
    # fallback stable short hash
    raw = (url or "") + "|" + (title or "")
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:12]

def absolute_url(base: str, href: Optional[str]) -> Optional[str]:
    if not href:
        return None
    return urljoin(base, href)