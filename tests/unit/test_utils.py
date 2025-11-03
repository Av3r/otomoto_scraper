import pytest

# from src.scraper.utils import some_utility_function
from src.scraper.models import CarModel
from src.scraper.utils import (extract_currency, parse_float_from_text,
                               parse_int_from_text)


def test_parse_int_from_text():
    assert parse_int_from_text("225 275 km") == 225275
    assert parse_int_from_text("120000") == 120000
    assert parse_int_from_text("brak") is None


def test_parse_float_and_currency():
    assert parse_float_from_text("48 500") == 48500.0
    assert parse_float_from_text("48 500 PLN") == 48500.0
    assert extract_currency("48 500 PLN") == "PLN"
    assert extract_currency("EUR 10 000") == "EUR"


def test_valid_car_model_creation():
    car = CarModel(
        id="1",
        url="http://example.com/car/1",
        car_brand="Toyota",
        model="Corolla",
        year=2020,
        price=20000.0,
        price_currency="USD",
        engine_capacity=1.8,
        engine_power=140,
        mileage_km=15000,
        location="New York",
        fuel_type="Petrol",
    )
    assert car.id == "1"
    assert car.car_brand == "Toyota"
    assert car.price == 20000.0
