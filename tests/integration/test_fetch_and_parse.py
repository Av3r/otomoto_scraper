from datetime import datetime
from pathlib import Path

import pytest

from src.scraper.fetcher import fetch_page
from src.scraper.models import CarModel
from src.scraper.parser import parse_listings


@pytest.fixture
def sample_html():
    """Load sample page HTML from fixtures"""
    fixture = Path(__file__).parents[1] / "fixtures" / "sample_page.html"
    return fixture.read_text(encoding="utf-8")


def test_fetch_and_parse_integration(monkeypatch, sample_html):
    """Test that fetcher and parser work together with sample data"""

    from src.scraper import fetcher

    # Setup the mock
    def fake_fetch(url, timeout=10, save_snapshot=None):
        print(f"[test] Returning sample HTML for {url}")
        return sample_html

    # Patch the function object itself
    monkeypatch.setattr(fetcher, "fetch_page", fake_fetch)

    # Fetch and parse the sample page
    html = fetcher.fetch_page("https://www.otomoto.pl/osobowe/bmw")
    print("[test] Sample HTML length:", len(html))
    print("[test] Sample HTML preview:", html[:200])

    listings = parse_listings(html)

    assert listings is not None
    assert isinstance(listings, list)
    assert (
        len(listings) > 0
    )  # should find at least one listing    # Find our known test cases from the fixture
    bmw_530i = next((car for car in listings if car["id"] == "6FRsVn"), None)
    bmw_520d = next((car for car in listings if car["id"] == "6FRt2m"), None)

    assert bmw_530i is not None, "Should find BMW 530i listing"
    assert bmw_520d is not None, "Should find BMW 520d listing"

    # Verify specific fields from known fixtures
    assert bmw_530i["car_brand"] == "BMW"
    assert bmw_530i["model"] == "Seria 5 530i xDrive"
    assert bmw_530i["year"] == 2021
    assert bmw_530i["price"] == 239900.0
    assert bmw_530i["price_currency"] == "PLN"
    assert bmw_530i["engine_power"] == 252
    assert bmw_530i["location"] == "Warszawa, Mokotów"
    assert bmw_530i["fuel_type"] == "Benzyna"

    assert bmw_520d["car_brand"] == "BMW"
    assert bmw_520d["model"] == "Seria 5 520d Comfort"
    assert bmw_520d["year"] == 2020
    assert bmw_520d["price"] == 159900.0
    assert bmw_520d["engine_power"] == 190
    assert bmw_520d["location"] == "Kraków, Krowodrza"
    assert bmw_520d["fuel_type"] == "Diesel"
