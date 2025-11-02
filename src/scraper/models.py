from pydantic import BaseModel
from typing import List, Optional

class CarModel(BaseModel):   
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