from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import re

from .utils import (
    parse_float_from_text,
    parse_int_from_text,
    extract_currency,
    make_id_from_url_or_hash,
    absolute_url,
)
from .models import CarModel
from .config import BASE_URL

def split_brand_and_model(title: Optional[str]) -> (str, str):
    if not title:
        return "", ""
    parts = title.split()
    if len(parts) == 1:
        return parts[0], ""
    brand = parts[0]
    model = " ".join(parts[1:])
    return brand, model


def parse_offer_element(it, base_url: str) -> Optional[Dict]:
    # id
    data_id = it.get("data-id")
    id_val = data_id or make_id_from_url_or_hash("", "")

    # title + url
    title_el = it.select_one("h2.etydmma0 > a")
    title = title_el.get_text(strip=True) if title_el else None
    href = title_el["href"] if (title_el and title_el.has_attr("href")) else None
    url = absolute_url(base_url, href) if href else None

    # price + currency
    price_el = it.select_one("h3.efzkujb1")
    currency_el = it.select_one("p.efzkujb2")
    price_raw = price_el.get_text(strip=True) if price_el else None
    price = parse_float_from_text(price_raw) if price_raw else None
    currency = currency_el.get_text(strip=True) if currency_el else None

    # parameters from <dl>
    params = {}
    dl = it.select_one("dl.ooa-x6wpd5")
    if dl:
        dts = dl.find_all("dt")
        dds = dl.find_all("dd")
        for dt, dd in zip(dts, dds):
            key = dt.get_text(strip=True).lower()
            value = dd.get_text(strip=True)
            params[key] = value

    # Extract specific parameters from params dict
    year = None
    mileage = None
    engine_capacity = None
    engine_power = None
    fuel_type = None

    # year
    if "year" in params:
        try:
            year = int(params["year"])
        except Exception:
            year = None

    # mileage, np. "225 275 km"
    if "mileage" in params:
        mileage = parse_int_from_text(params["mileage"])

    # engine capacity and power parsing from <p class="ooa-nxfgg7">
    engine_capacity = None
    engine_power = None
    extra_info_el = it.select_one("p.ooa-nxfgg7")
    if extra_info_el:
        extra_text = extra_info_el.get_text(strip=True)
        # eg.: "2996 cm3 • 204 KM • BMW 523i, Pierwszy właściciel w Polsce od 7lat."
        parts = [part.strip() for part in extra_text.split("•")]
        for part in parts:
            # capacity in cm3
            m_engine = re.search(r"(\d{3,4})\s?cm3", part, re.I)
            if m_engine:
                try:
                    engine_capacity = float(m_engine.group(1))
                except:
                    pass

            # engine power in KM or kW
            m_power = re.search(r"(\d{2,4})\s?(KM|kW)", part, re.I)
            if m_power:
                try:
                    engine_power = int(m_power.group(1))
                except:
                    pass

    # fuel type
    if "fuel_type" in params:
        fuel_type = params["fuel_type"].capitalize()

    # location
    location_el = it.select_one("ul.ooa-1o0axny li p")
    location = location_el.get_text(strip=True) if location_el else None

    # brand/model from title
    brand_guess, model_guess = split_brand_and_model(title)

    raw = {
        "id": str(id_val),
        "url": url or "",
        "car_brand": brand_guess,
        "model": model_guess,
        "year": year or 0,
        "price": price or 0.0,
        "price_currency": currency,
        "engine_capacity": engine_capacity,
        "engine_power": engine_power,
        "mileage_km": mileage,
        "location": location,
        "fuel_type": fuel_type,
    }

    try:
        car = CarModel.parse_obj(raw)
        return car.dict()
    except Exception as e:
        print("CarModel validation failed:", e, "raw:", raw)
        # Coerce minimal data if validation fails
        raw["id"] = str(raw.get("id") or make_id_from_url_or_hash(url, title))
        raw["url"] = raw.get("url") or ""
        return raw


def parse_listings(html: str, base_url: str = BASE_URL) -> List[Dict]:
    soup = BeautifulSoup(html, "html.parser")
    results = []

    # Find all <article> elements with data-id; these are the listings
    items = soup.find_all("article", attrs={"data-id": True})

    print(f"Found {len(items)} offer elements")

    for it in items:
        parsed = parse_offer_element(it, base_url)
        if parsed:
            results.append(parsed)

    return results