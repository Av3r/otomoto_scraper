from .crawler import scrape_pages
from .config import BASE_URL

def main():
    print("Start scraping Otomoto (simple crawler).")
    offers = scrape_pages(base_url=BASE_URL, max_pages=50, delay=1.0, stop_on_empty=True)
    print(f"Finished. Collected {len(offers)} offers in this run.")

if __name__ == "__main__":
    main()




# from bs4 import BeautifulSoup
# import requests
# from .fetcher import fetch_page
# from .parser import parse_listings
# from .storage import LocalJSONLStorage
# from .config import BASE_URL
# import time


# def scrape_all_pages(base_url: str = BASE_URL, max_pages: int = 2, delay: float = 1.0):
#     page = 1
#     all_offers = []

#     while page <= max_pages:
#         # Budowanie adresu strony
#         if page == 1:
#             url = base_url
#         else:
#             url = f"{base_url}?page={page}"

#         print(f"Fetching {url}")
#         try:
#             html = fetch_page(url)
#         except Exception as e:
#             print(f"Fetch error on page {page}: {e}")
#             break

#         offers = parse_listings(html, base_url)
#         if not offers:
#             print(f"No offers found on page {page}, stopping.")
#             break

#         all_offers.extend(offers)
#         print(f"Page {page}: {len(offers)} offers found (total {len(all_offers)})")

#         page += 1
#         time.sleep(delay)

#     return all_offers




# def test_articles_on_page(url):
#     response = requests.get(url)
#     html = response.text

#     soup = BeautifulSoup(html, "html.parser")
#     articles = soup.find_all("article")
#     print(f"Znaleziono {len(articles)} elementów <article>")
#     for i, article in enumerate(articles[:5], 1):
#         print(f"Element {i} klasy: {article.get('class')}")
#         # dla szybkiego podglądu tekstu, pierwsze 200 znaków:
#         print(article.get_text(strip=True)[:200])


# if __name__ == "__main__":

#     url = f"{BASE_URL}"#/osobowe/bmw/seria-5"
#     headers = {
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
#     }
#     r = requests.get(url, headers=headers)
#     offers = parse_listings(r.text, base_url=BASE_URL)

#     print(f"Pobrano {len(offers)} ofert")
#     for offer in offers:
#         print(offer)








# if __name__ == "__main__":
#     #test_articles_on_page("https://www.otomoto.pl/osobowe/bmw/seria-5")

#     url = "https://www.otomoto.pl/osobowe/bmw/seria-5"
#     headers = {
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
#     }

#     response = requests.get(url, headers=headers)

#     print(f"Response URL: {response.url}")
#     print(f"Response status: {response.status_code}")
#     print(f"Response length: {len(response.text)}")

#     if response.status_code == 200:
#         soup = BeautifulSoup(response.text, "html.parser")
#         offers = soup.find_all("article", attrs={"data-id": True})
#         for offer in offers:
#             title_el = offer.select_one("h2.etydmma0 > a")
#             if title_el:
#                 title = title_el.get_text(strip=True)
#                 url = title_el['href']
#                 print(f"Tytuł: {title}")
#                 print(f"URL: {url}")
#             else:
#                 print("Brak tytułu")
#         #print(f"Znaleziono ofert: {len(offers)}")
#     else:
#         print("Błąd pobierania strony")

# def main():
#     offers = scrape_all_pages()
#     print(f'offers {[len(offers)]}')
#     storage = LocalJSONLStorage()
#     path = storage.save(offers, filename="all_offers.jsonl")
#     print("Saved", len(offers), "offers to", path)

# if __name__ == "__main__":
#     main()