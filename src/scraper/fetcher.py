import requests
import time
from typing import Optional

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
            print(f"[fetch] HTTP error {e} (attempt {attempt}/{tries})")
            if resp.status_code in (403, 429):
                # 403 or rate-limit -> don't hammer, wait longer
                time.sleep(5 * attempt)
            else:
                time.sleep(1)
        except Exception as e:
            print(f"[fetch] network/error {e} (attempt {attempt}/{tries})")
            time.sleep(1 * attempt)
    raise RuntimeError(f"Failed to fetch {url} after {tries} tries")