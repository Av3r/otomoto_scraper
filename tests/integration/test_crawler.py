import json
from pathlib import Path

import pytest

import src.scraper.crawler as crawler_mod


def load_fixture(name):
    """Helper to load HTML fixture files from tests/fixtures/"""
    path = Path(__file__).parents[1] / "fixtures" / name
    if not path.exists():
        raise FileNotFoundError(f"Fixture not found: {path}")
    return path.read_text(encoding="utf-8")


@pytest.fixture
def sample_html():
    """Main fixture with two BMW listings"""
    return load_fixture("sample_page.html")


@pytest.fixture
def empty_html():
    """HTML page with zero listings"""
    return """
    <!DOCTYPE html>
    <html><body>
        <div class="ooa-1hab6wx er8sc6m0">
            <!-- no articles/listings -->
        </div>
    </body></html>
    """


@pytest.fixture
def invalid_html():
    """Broken HTML to test error handling"""
    return "<not-valid></html>"


def test_scrape_one_page_monkeypatched(monkeypatch, tmp_path, sample_html):
    """Test basic crawling with two valid listings"""

    # fake fetch_page that returns our static sample
    def fake_fetch(url, timeout=10, save_snapshot=None):
        return sample_html

    monkeypatch.setattr(crawler_mod, "fetch_page", fake_fetch)

    # temporary storage that writes to tmp_path
    class TmpStorage:
        def __init__(self, folder="data"):
            self.folder = tmp_path
            self.folder.mkdir(parents=True, exist_ok=True)

        def save(self, offers, filename="all_offers.jsonl"):
            path = self.folder / filename
            with path.open("a", encoding="utf-8") as f:
                for o in offers:
                    f.write(json.dumps(o, ensure_ascii=False) + "\n")
            return str(path)

    monkeypatch.setattr(crawler_mod, "LocalJSONLStorage", TmpStorage)

    # run crawler for a single page
    offers = crawler_mod.scrape_pages(
        base_url="https://www.otomoto.pl/osobowe/bmw/seria-5",
        max_pages=1,
        delay=0,
        stop_on_empty=True,
    )

    assert isinstance(offers, list)
    assert len(offers) > 0

    # verify specific fields from the fixture
    first = next(o for o in offers if o["id"] == "6FRsVn")
    assert first["car_brand"] == "BMW"
    assert first["model"] == "Seria 5 530i xDrive"
    assert first["year"] == 2021
    assert first["price"] == 239900.0
    assert first["price_currency"] == "PLN"
    assert first["engine_capacity"] == 1998.0
    assert first["engine_power"] == 252
    assert first["mileage_km"] == 45275
    assert first["location"] == "Warszawa, Mokotów"
    assert first["fuel_type"] == "Benzyna"

    # check file output
    out_file = tmp_path / "all_offers.jsonl"
    assert out_file.exists()

    lines = out_file.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2  # exactly two offers from our fixture
    saved = [json.loads(line) for line in lines]
    assert {o["id"] for o in saved} == {"6FRsVn", "6FRt2m"}


def test_scrape_empty_page(monkeypatch, tmp_path, empty_html):
    """Test crawler behavior with a page containing zero listings"""

    def fake_fetch(url, timeout=10, save_snapshot=None):
        return empty_html

    monkeypatch.setattr(crawler_mod, "fetch_page", fake_fetch)
    monkeypatch.setattr(
        crawler_mod, "LocalJSONLStorage", lambda folder: None
    )  # no storage needed

    offers = crawler_mod.scrape_pages(
        base_url="https://www.otomoto.pl/empty",
        max_pages=3,  # try multiple pages
        delay=0,
        stop_on_empty=True,
    )

    assert isinstance(offers, list)
    assert len(offers) == 0  # no offers found


def test_scrape_invalid_html(monkeypatch, tmp_path, invalid_html):
    """Test crawler error handling with invalid HTML"""

    def fake_fetch(url, timeout=10, save_snapshot=None):
        return invalid_html

    monkeypatch.setattr(crawler_mod, "fetch_page", fake_fetch)
    monkeypatch.setattr(crawler_mod, "LocalJSONLStorage", lambda folder: None)

    offers = crawler_mod.scrape_pages(
        base_url="https://www.otomoto.pl/invalid",
        max_pages=1,
        delay=0,
    )

    assert isinstance(offers, list)
    assert len(offers) == 0  # graceful handling of invalid HTML


def test_scrape_deduplication(monkeypatch, tmp_path, sample_html):
    """Test that crawler deduplicates offers by ID"""

    def fake_fetch(url, timeout=10, save_snapshot=None):
        return sample_html  # return same offers on every page

    monkeypatch.setattr(crawler_mod, "fetch_page", fake_fetch)

    class CountingStorage:
        def __init__(self, folder="data"):
            self.saved_offers = []
            self.folder = tmp_path

        def save(self, offers, filename="all_offers.jsonl"):
            self.saved_offers.extend(offers)
            return str(self.folder / filename)

    storage = CountingStorage()
    monkeypatch.setattr(crawler_mod, "LocalJSONLStorage", lambda folder: storage)

    # crawl multiple pages that return the same listings
    offers = crawler_mod.scrape_pages(
        base_url="https://www.otomoto.pl/osobowe/bmw/seria-5",
        max_pages=3,  # try to get same offers 3 times
        delay=0,
        stop_on_empty=False,
    )

    # should only get unique offers despite seeing them multiple times
    assert len(offers) == 2
    assert len(storage.saved_offers) == 2
    assert {o["id"] for o in offers} == {"6FRsVn", "6FRt2m"}
