"""
Shared utility helpers for PCFinder LK.
"""

from __future__ import annotations

import hashlib
import json
import random
import uuid
from typing import Any, Dict, Optional


# ---------------------------------------------------------------------------
# User-Agent rotation
# ---------------------------------------------------------------------------

USER_AGENTS: list[str] = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.6533.72 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 OPR/110.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:127.0) Gecko/20100101 Firefox/127.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0",
    "Mozilla/5.0 (iPad; CPU OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 13; Samsung Galaxy S23) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.122 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Brave/127",
    "Mozilla/5.0 (Linux; Android 14; OnePlus 12) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.6533.84 Mobile Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:128.0) Gecko/20100101 Firefox/128.0",
]


def get_random_ua() -> str:
    """Return a random User-Agent string from the pool."""
    return random.choice(USER_AGENTS)


# ---------------------------------------------------------------------------
# Price formatting
# ---------------------------------------------------------------------------

def format_price(price_int: Optional[int]) -> str:
    """Convert an integer LKR price to a human-readable display string."""
    if price_int is None:
        return "Price not listed"
    return f"Rs. {price_int:,}"


# ---------------------------------------------------------------------------
# Condition normalisation
# ---------------------------------------------------------------------------

_CONDITION_MAP: dict[str, str] = {
    "brand new": "Brand New",
    "new": "Brand New",
    "sealed": "Brand New",
    "used": "Used / Secondhand",
    "secondhand": "Used / Secondhand",
    "second hand": "Used / Secondhand",
    "refurbished": "Used / Secondhand",
    "reconditioned": "Used / Secondhand",
    "pre-owned": "Used / Secondhand",
    "pre owned": "Used / Secondhand",
}


def normalize_condition(raw: str) -> str:
    """Map a raw condition string to one of the three canonical values."""
    key = raw.strip().lower()
    return _CONDITION_MAP.get(key, "Unknown")


# ---------------------------------------------------------------------------
# ID generation
# ---------------------------------------------------------------------------

def generate_id() -> str:
    """Return a UUID4 string suitable for use as a listing id."""
    return str(uuid.uuid4())


# ---------------------------------------------------------------------------
# Cache key
# ---------------------------------------------------------------------------

def generate_query_hash(query: str, filters: Dict[str, Any]) -> str:
    """
    Generate a stable MD5 hex digest from the search query and all active
    filter parameters.  ``None`` values are excluded so that
    ``search("gpu")`` and ``search("gpu", condition=None)`` share the same key.
    """
    canonical: Dict[str, Any] = {"q": query.strip().lower()}
    for key, value in sorted(filters.items()):
        if value is not None:
            canonical[key] = value
    payload = json.dumps(canonical, sort_keys=True)
    return hashlib.md5(payload.encode()).hexdigest()


# ---------------------------------------------------------------------------
# Autocomplete product suggestions
# ---------------------------------------------------------------------------

PRODUCT_SUGGESTIONS: list[str] = [
    # CPUs — AMD
    "AMD Ryzen 5 5600X",
    "AMD Ryzen 5 5600G",
    "AMD Ryzen 5 7600X",
    "AMD Ryzen 7 5700X",
    "AMD Ryzen 7 5800X",
    "AMD Ryzen 7 7700X",
    "AMD Ryzen 9 5900X",
    "AMD Ryzen 9 5950X",
    "AMD Ryzen 9 7900X",
    "AMD Ryzen 9 7950X",
    # CPUs — Intel
    "Intel Core i5-12400F",
    "Intel Core i5-13400F",
    "Intel Core i5-12600K",
    "Intel Core i5-13600K",
    "Intel Core i7-12700K",
    "Intel Core i7-13700K",
    "Intel Core i9-13900K",
    "Intel Core i9-12900K",
    # GPUs — NVIDIA
    "NVIDIA GeForce RTX 3060 12GB",
    "NVIDIA GeForce RTX 3060 Ti",
    "NVIDIA GeForce RTX 3070",
    "NVIDIA GeForce RTX 3070 Ti",
    "NVIDIA GeForce RTX 3080 10GB",
    "NVIDIA GeForce RTX 3090",
    "NVIDIA GeForce RTX 4060",
    "NVIDIA GeForce RTX 4060 Ti",
    "NVIDIA GeForce RTX 4070",
    "NVIDIA GeForce RTX 4070 Ti",
    "NVIDIA GeForce RTX 4080",
    "NVIDIA GeForce RTX 4090",
    "NVIDIA GeForce GTX 1660 Super",
    "NVIDIA GeForce GTX 1660 Ti",
    # GPUs — AMD
    "AMD Radeon RX 6600",
    "AMD Radeon RX 6600 XT",
    "AMD Radeon RX 6700 XT",
    "AMD Radeon RX 6800 XT",
    "AMD Radeon RX 7600",
    "AMD Radeon RX 7900 XT",
    # RAM
    "Corsair Vengeance 16GB DDR4 3200MHz",
    "G.Skill Trident Z 16GB DDR4 3600MHz",
    "Kingston HyperX Fury 8GB DDR4",
    "Samsung 8GB DDR4 3200MHz",
    "32GB DDR4 3200MHz Kit",
    "16GB DDR5 4800MHz",
    # Storage
    "Samsung 970 EVO Plus 1TB NVMe",
    "Samsung 870 EVO 1TB SSD",
    "WD Blue SN570 1TB NVMe",
    "Seagate Barracuda 2TB HDD",
    "Kingston NV2 1TB NVMe",
    "WD Green 240GB SSD",
    # Motherboards
    "ASUS ROG Strix B550-F",
    "MSI MAG B550 TOMAHAWK",
    "Gigabyte B660M DS3H",
    "ASUS Prime Z690-P",
    # Power Supplies
    "Corsair RM750x 750W 80+ Gold",
    "EVGA SuperNOVA 650W G6",
    "Cooler Master MWE Gold 650W",
    # Cases
    "NZXT H510",
    "Lian Li Lancool 215",
    "Cooler Master MasterBox Q300L",
    # Monitors
    "LG 27-inch 1440p IPS 144Hz",
    "Samsung Odyssey G5 27-inch",
    "ASUS TUF Gaming 24-inch 165Hz",
    # Laptops
    "ASUS ROG Strix G15",
    "Lenovo Legion 5 Ryzen 7",
    "HP Victus 15 RTX 3050",
    "Dell G15 Gaming Laptop",
    # Peripherals
    "Logitech G502 Hero Gaming Mouse",
    "Razer BlackWidow V3 Keyboard",
    "Corsair K70 RGB Keyboard",
    "HyperX Cloud II Headset",
]
