"""
Sense.lk adapter for PCFinder LK.

MOCK IMPLEMENTATION
-------------------
Sense.lk is an online-first IT retailer. Their WooCommerce / custom storefront
would be scraped with httpx + BeautifulSoup:

    async with httpx.AsyncClient(headers={"User-Agent": get_random_ua()}) as client:
        await asyncio.sleep(random.uniform(0.5, 1.5))
        resp = await client.get(
            f"https://sense.lk/?s={quote_plus(query)}&post_type=product",
            timeout=15,
        )
        soup = BeautifulSoup(resp.text, "html.parser")
        for item in soup.select("div.product-item"):
            title    = item.select_one("h3.product-title").get_text(strip=True)
            price_el = item.select_one("span.price")
            price    = price_el.get_text(strip=True) if price_el else None
            link     = item.select_one("a.product-link")["href"]
            img_el   = item.select_one("img.product-image")
            img_url  = img_el["src"] if img_el else None
            # … parse + yield Listing(...)
"""

from __future__ import annotations

import asyncio
import random
import re
from typing import List
from urllib.parse import quote_plus

from adapters.base import BaseAdapter
from models import Listing
from utils import format_price, generate_id

_LOCATION = "Colombo"

_WARRANTY_OPTIONS = [
    "1 Year Sense.lk Warranty",
    "1 Year Sense.lk Warranty",
    "2 Years Official Warranty",
    "3 Years Official Warranty",
    "6 Months Sense.lk Warranty",
]

_COMPONENT_DATA: dict[str, tuple[list[str], tuple[int, int]]] = {
    "rtx 5090": (["MSI GeForce RTX 5090 32G SUPRIM LIQUID", "ZOTAC GAMING RTX 5090 Solid OC 32GB GDDR7"], (950_000, 1_250_000)),
    "rtx 5080": (["MSI GeForce RTX 5080 16G GAMING TRIO OC", "ZOTAC GAMING RTX 5080 Solid 16GB GDDR7"], (480_000, 590_000)),
    "rtx 5070 ti": (["MSI RTX 5070 Ti 16G VENTUS 3X OC", "ASUS TUF RTX 5070 Ti 16GB GDDR7"], (320_000, 395_000)),
    "rtx 5070": (["MSI RTX 5070 12G VENTUS 2X OC", "ZOTAC RTX 5070 Solid 12GB GDDR7"], (235_000, 290_000)),
    "rtx 5060 ti": (["MSI RTX 5060 Ti 16G VENTUS 2X OC Plus", "ASUS Dual RTX 5060 Ti 8GB GDDR7"], (215_000, 265_000)),
    "rtx 5060": (["MSI GeForce RTX 5060 8G VENTUS 2X OC GDDR7", "ZOTAC GAMING RTX 5060 Twin Edge 8GB GDDR7", "MSI RTX 5060 8G GAMING OC GDDR7"], (155_000, 185_000)),
    "rtx 4090": (["ZOTAC GAMING RTX 4090 AMP Extreme AIRO 24GB", "ASUS TUF Gaming RTX 4090 OC 24GB"], (370_000, 490_000)),
    "rtx 4080": (["ZOTAC GAMING RTX 4080 AMP Extreme AIRO 16GB", "MSI RTX 4080 Ventus 3X OC 16GB"], (282_000, 362_000)),
    "rtx 4070 ti": (["ZOTAC RTX 4070 Ti AMP AIRO 12GB", "MSI RTX 4070 Ti Gaming X Trio 12GB"], (240_000, 302_000)),
    "rtx 4070": (["ZOTAC RTX 4070 AMP AIRO 12GB", "MSI RTX 4070 Ventus 2X 12GB OC"], (178_000, 232_000)),
    "rtx 4060 ti": (["ZOTAC RTX 4060 Ti AMP 8GB", "MSI RTX 4060 Ti Ventus 2X 8GB OC"], (122_000, 168_000)),
    "rtx 4060": (["ZOTAC RTX 4060 Twin Edge OC 8GB", "MSI RTX 4060 Ventus 2X OC 8GB"], (96_000, 130_000)),
    "rtx 3080": (["ZOTAC RTX 3080 Trinity OC 10GB LHR", "MSI RTX 3080 Ventus 3X 10G OC LHR"], (180_000, 238_000)),
    "rtx 3070": (["ZOTAC RTX 3070 Twin Edge OC 8GB LHR", "MSI RTX 3070 Ventus 2X OC 8GB LHR"], (118_000, 158_000)),
    "rtx 3060 ti": (["ZOTAC RTX 3060 Ti Twin Edge OC 8GB LHR", "MSI RTX 3060 Ti Ventus 2X OC 8GB"], (90_000, 126_000)),
    "rtx 3060": (["ZOTAC RTX 3060 Twin Edge OC 12GB", "MSI GeForce RTX 3060 Ventus 2X 12GB OC"], (84_000, 114_000)),
    "gtx 1660": (["ZOTAC GTX 1660 Super Twin Fan 6GB", "MSI GTX 1660 Super Ventus XS OC 6GB"], (50_000, 67_000)),
    "rx 7900": (["XFX RX 7900 XTX Speedster MERC 310 24GB"], (225_000, 295_000)),
    "rx 6800": (["XFX RX 6800 XT Speedster MERC 319 Core 16GB"], (148_000, 198_000)),
    "rx 6700": (["XFX RX 6700 XT QICK 319 Black 12GB"], (104_000, 142_000)),
    "rx 6600": (["XFX RX 6600 XT Speedster SWFT 210 Core 8GB"], (64_000, 88_000)),
    "ryzen 9 5900x": (["AMD Ryzen 9 5900X 12-Core 24-Thread OEM"], (87_000, 122_000)),
    "ryzen 7 5800x": (["AMD Ryzen 7 5800X 8-Core 16-Thread OEM"], (59_000, 88_000)),
    "ryzen 5 5600x": (["AMD Ryzen 5 5600X 6-Core 12-Thread OEM"], (40_000, 63_000)),
    "ryzen 5 5600g": (["AMD Ryzen 5 5600G with Vega 7 Graphics OEM"], (39_000, 58_000)),
    "ryzen 5 7600x": (["AMD Ryzen 5 7600X AM5 6-Core OEM"], (57_000, 84_000)),
    "i9-13900k": (["Intel Core i9-13900K 24-Core OEM"], (97_000, 142_000)),
    "i7-13700k": (["Intel Core i7-13700K 16-Core OEM"], (70_000, 103_000)),
    "i5-13600k": (["Intel Core i5-13600K 14-Core OEM"], (52_000, 78_000)),
    "i5-13400": (["Intel Core i5-13400F 10-Core OEM"], (36_000, 54_000)),
    "i5-12400": (["Intel Core i5-12400F 6-Core OEM", "Intel Core i5-12600K 10-Core OEM"], (30_000, 48_000)),
    "16gb ddr4": (["Team T-Force Vulcan Z 16GB DDR4 3200MHz Kit", "ADATA XPG SPECTRIX D35G 16GB DDR4 3200MHz"], (13_000, 21_000)),
    "32gb ddr4": (["Team T-Force Vulcan Z 32GB DDR4 3200MHz Kit", "ADATA XPG D35G 32GB DDR4 3200MHz Kit"], (24_000, 38_000)),
    "16gb ddr5": (["Team T-Force Delta RGB 16GB DDR5 5200MHz", "ADATA XPG LANCER 16GB DDR5 5200MHz"], (22_000, 35_000)),
    "1tb nvme": (["Team MP44 1TB PCIe 4.0 NVMe M.2", "ADATA LEGEND 960 1TB PCIe 4.0 NVMe M.2"], (16_500, 29_000)),
    "gaming pc": (["Sense.lk Custom Build - i5-13400F + RTX 4060 + 16GB + 1TB", "Sense.lk Pro Build - Ryzen 7 7700X + RTX 4070 + 32GB DDR5 + 2TB NVMe"], (142_000, 415_000)),
    "laptop": (["Acer Predator Helios 16 i7-13700HX RTX 4060 165Hz", "ASUS ROG Strix G16 2024 i9-14900HX RTX 4080"], (158_000, 380_000)),
    "monitor": (["ASUS TUF Gaming VG28UQL1A 28-inch 4K 144Hz IPS", "Gigabyte M27F A 27-inch FHD 165Hz IPS"], (52_000, 158_000)),
}

_GENERIC_TEMPLATES = [
    "{query} Brand New - Sense.lk Official Store",
    "Sense.lk {query} - Sealed with Full Warranty",
    "{query} - Sense.lk Genuine Product",
]


def _make_slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def _resolve_component(query: str) -> tuple[list[str], tuple[int, int]]:
    q_lower = query.lower()
    best_key = ""
    for key in _COMPONENT_DATA:
        if key in q_lower and len(key) > len(best_key):
            best_key = key
    if best_key:
        return _COMPONENT_DATA[best_key]
    generic_names = [t.format(query=query.title()) for t in _GENERIC_TEMPLATES]
    return generic_names, (20_000, 185_000)


class SenseAdapter(BaseAdapter):
    name = "Sense.lk"
    seller_type = "Verified Store"
    source_type = "retail"

    async def search(self, query: str) -> List[Listing]:
        await asyncio.sleep(random.uniform(0.05, 0.25))

        name_pool, (price_min, price_max) = _resolve_component(query)
        num_results = random.randint(2, 4)
        listings: List[Listing] = []

        for _ in range(num_results):
            title = random.choice(name_pool)
            price = random.randint(price_min // 1000, price_max // 1000) * 1000
            listing_id = generate_id()
            slug = _make_slug(title[:50])

            listings.append(
                Listing(
                    id=listing_id,
                    title=title,
                    price_lkr=price,
                    price_display=format_price(price),
                    condition="Brand New",
                    warranty=random.choice(_WARRANTY_OPTIONS),
                    source_platform=self.name,
                    seller_type=self.seller_type,
                    location=_LOCATION,
                    url=f"https://www.sense.lk/?s={quote_plus(query)}&post_type=product",
                    date_posted=None,
                    last_updated=None,
                    image_url=None,
                    category="Computer Hardware",
                )
            )

        return listings
