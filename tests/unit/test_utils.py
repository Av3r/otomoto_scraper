import pytest
from src.scraper.utils import some_utility_function
from src.scraper.models import CarModel


def test_some_utility_function():
    assert some_utility_function(1, 2) == 3
    assert some_utility_function(-1, 1) == 0
    assert some_utility_function(0, 0) == 0


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


def test_invalid_car_model_creation():
    with pytest.raises(ValueError):
        CarModel(
            id="2",
            url="http://example.com/car/2",
            car_brand="Honda",
            model="Civic",
            year="not_a_year",  # Invalid year
            price=18000.0,
        )

    with pytest.raises(ValueError):
        CarModel(
            id="3",
            url="http://example.com/car/3",
            car_brand="",
            model="Civic",
            year=2020,
            price=18000.0,
        )
