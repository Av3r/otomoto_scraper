import time
from typing import List, Dict, Set

from .fetcher import fetch_page
from .parser import parse_listings
from .storage import LocalJSONLStorage
from .config import BASE_URL

def scrape_pages(
    base_url: str = BASE_URL,
    max_pages: int = 50,
    delay: float = 1.0,
    stop_on_empty: bool = True,
) -> List[Dict]:
    """
    Simple sequential crawler:
      - page 1: base_url
      - page N: base_url + "?page=N"
    Returns a list of new, unique offers from a single run.
    """
    page = 1
    seen_ids: Set[str] = set()
    collected: List[Dict] = []
    storage = LocalJSONLStorage(folder="data")

    while page <= max_pages:
        if page == 1:
            url = base_url
        else:
            sep = "&" if "?" in base_url else "?"
            url = f"{base_url}{sep}page={page}"

        print(f"[scrape] Fetching page {page}: {url}")
        try:
            html = fetch_page(url, timeout=15)
        except Exception as e:
            print(f"[scrape] Fetch error on page {page}: {e}")
            break

        offers = parse_listings(html, base_url)
        print(f"[scrape] Found {len(offers)} offers on page {page}")

        # dedupe in this run and collect new offers
        new_offers = []
        for off in offers:
            off_id = str(off.get("id") or off.get("url") or "")
            if not off_id:
                # fallback: skip if no id/url
                continue
            if off_id in seen_ids:
                continue
            seen_ids.add(off_id)
            new_offers.append(off)

        if new_offers:
            storage.save(new_offers, filename="all_offers.jsonl")
            collected.extend(new_offers)
            print(f"[scrape] Saved {len(new_offers)} new offers (total collected: {len(collected)})")
        else:
            print("[scrape] No new offers on this page.")

        if stop_on_empty and len(offers) == 0:
            print(f"[scrape] No offers on page {page} — stopping.")
            break

        page += 1
        time.sleep(delay)

    return collected