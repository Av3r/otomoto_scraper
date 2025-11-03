"""HTTP fetching helpers used by the scraper.

This module provides a small retrying `fetch_page` helper which returns
the HTML body or raises on repeated failures.
"""

import time
from typing import Optional

import requests
from requests import RequestException

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": "https://www.google.com/",
}


def fetch_page(url: str, timeout: int = 10, save_snapshot: Optional[str] = None) -> str:
    """Fetch a URL with a small retry loop and return the response text.

    On repeated failures a RuntimeError is raised.
    """
    tries = 3
    for attempt in range(1, tries + 1):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=timeout)
            # print status for debug
            print(f"[fetch] {url} -> {resp.status_code}")
            resp.raise_for_status()
            text = resp.text
            if save_snapshot:
                with open(save_snapshot, "w", encoding="utf-8") as f:
                    f.write(text)
            return text
        except requests.HTTPError as e:
            # HTTP errors from raise_for_status
            print(f"[fetch] HTTP error {e} (attempt {attempt}/{tries})")
            status = getattr(resp, "status_code", None)
            if status in (403, 429):
                # 403 or rate-limit -> don't hammer, wait longer
                time.sleep(5 * attempt)
            else:
                time.sleep(1)
        except RequestException as e:
            # network-level errors (timeouts, connection errors, etc.)
            print(f"[fetch] network/error {e} (attempt {attempt}/{tries})")
            time.sleep(1 * attempt)
    raise RuntimeError(f"Failed to fetch {url} after {tries} tries")
