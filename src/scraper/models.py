"""Pydantic models used to validate parsed car offers.

Only a single `CarModel` is defined for the current test-suite and
parser output validation.
"""

from typing import Optional

from pydantic import BaseModel


class CarModel(BaseModel):
    """Schema for a scraped car offer.

    Fields are simple and intentionally permissive to allow lenient
    parsing from imperfect HTML.
    """

    id: str
    url: str
    car_brand: str
    model: str
    year: int
    price: float
    price_currency: Optional[str] = None
    engine_capacity: Optional[float] = None
    engine_power: Optional[int] = None
    mileage_km: Optional[int] = None
    location: Optional[str] = None
    fuel_type: Optional[str] = None
