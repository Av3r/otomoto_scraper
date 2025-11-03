from .config import BASE_URL
from .crawler import scrape_pages


def main():
    print("Start scraping Otomoto (simple crawler).")
    offers = scrape_pages(base_url=BASE_URL, max_pages=5, delay=1.0, stop_on_empty=True)
    print(f"Finished. Collected {len(offers)} offers in this run.")


if __name__ == "__main__":
    main()
