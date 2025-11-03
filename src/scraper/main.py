"""Command-line entrypoint for running the scraper.

This module exposes a simple `main()` function that runs the crawler once.
"""

from .crawler import scrape_pages
from .config import BASE_URL


def main() -> None:
    """Run a single scraping session and print a short summary.

    This function exists so the package can be executed with
    `python -m src.scraper.main` during development.
    """
    print("Start scraping Otomoto (simple crawler).")
    offers = scrape_pages(base_url=BASE_URL, max_pages=5, delay=1.0, stop_on_empty=True)
    print(f"Finished. Collected {len(offers)} offers in this run.")


if __name__ == "__main__":
    main()