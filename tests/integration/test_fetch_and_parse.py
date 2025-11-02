import pytest
from datetime import datetime
from src.scraper.fetcher import fetch_data
from src.scraper.parser import parse_data
from src.models import CarModel


def test_fetch_and_parse():
    data = fetch_data("http://example.com/data")
    parsed = parse_data(data)
    assert parsed is not None
    assert isinstance(parsed, list)
    assert len(parsed) > 0

    current_year = datetime.now().year
    for car in parsed:
        assert isinstance(car, CarModel)  # Ensure each item is a CarModel
        assert car.price > 0  # Price should be greater than 0
        assert car.year <= current_year  # Year should not be greater than current year
