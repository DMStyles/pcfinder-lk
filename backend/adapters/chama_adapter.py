"""
Chama Computers adapter for PCFinder LK.

MOCK IMPLEMENTATION
-------------------
Chama Computers is a well-known retailer in Nugegoda / Colombo.  Their site
would be scraped with httpx + BeautifulSoup in the same WooCommerce pattern:

    async with httpx.AsyncClient(headers={"User-Agent": get_random_ua()}) as client:
        await asyncio.sleep(random.uniform(0.5, 1.5))
        resp = await client.get(
            f"https://chama.lk/?s={quote_plus(query)}&post_type=product",
            timeout=15,
        )
        soup = BeautifulSoup(resp.text, "html.parser")
        for item in soup.select("li.product"):
            title = item.select_one(".woocommerce-loop-product__title").get_text(strip=True)
            price = item.select_one("span.woocommerce-Price-amount").get_text(strip=True)
            link  = item.select_one("a.woocommerce-LoopProduct-link")["href"]
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

_LOCATIONS = ["Nugegoda", "Colombo"]

_WARRANTY_OPTIONS = [
    "1 Year Chama Warranty",
    "1 Year Chama Warranty",
    "2 Years Official Warranty",
    "3 Years Official Warranty",
    "6 Months Chama Warranty",
]

_COMPONENT_DATA: dict[str, tuple[list[str], tuple[int, int]]] = {
    "rtx 4090": (["ASUS TUF RTX 4090 OC 24GB GDDR6X - Chama"], (372_000, 492_000)),
    "rtx 4080": (["MSI RTX 4080 Gaming X Trio 16GB - Chama"], (288_000, 368_000)),
    "rtx 4070 ti": (["ASUS TUF RTX 4070 Ti OC 12GB"], (242_000, 308_000)),
    "rtx 4070": (["MSI RTX 4070 Ventus 3X OC 12GB", "Gigabyte RTX 4070 Eagle OC 12GB"], (182_000, 238_000)),
    "rtx 4060 ti": (["MSI RTX 4060 Ti Ventus 2X Black 8GB"], (126_000, 172_000)),
    "rtx 4060": (["MSI RTX 4060 Ventus 2X Black OC 8GB", "Zotac RTX 4060 Twin Edge OC 8GB"], (99_000, 134_000)),
    "rtx 3080": (["MSI RTX 3080 Ventus 3X OC 10GB"], (182_000, 242_000)),
    "rtx 3070": (["MSI RTX 3070 Ventus 3X OC 8GB"], (120_000, 162_000)),
    "rtx 3060 ti": (["MSI RTX 3060 Ti Ventus 2X OC 8GB"], (92_000, 128_000)),
    "rtx 3060": (["MSI RTX 3060 Ventus 2X OC 12GB", "Zotac RTX 3060 Twin Edge OC 12GB"], (86_000, 116_000)),
    "gtx 1660": (["MSI GTX 1660 Super Ventus XS OC 6GB"], (52_000, 69_000)),
    "rx 7900": (["Sapphire Nitro+ RX 7900 XTX 24GB"], (228_000, 298_000)),
    "rx 6800": (["Sapphire Nitro+ RX 6800 XT 16GB OC SE"], (152_000, 200_000)),
    "rx 6700": (["Sapphire Pulse RX 6700 XT 12GB"], (106_000, 144_000)),
    "rx 6600": (["Sapphire Pulse RX 6600 XT 8GB"], (66_000, 90_000)),
    "ryzen 9 5900x": (["AMD Ryzen 9 5900X 12-Core BOX - Chama"], (88_000, 124_000)),
    "ryzen 7 5800x": (["AMD Ryzen 7 5800X 8-Core BOX"], (60_000, 90_000)),
    "ryzen 5 5600x": (["AMD Ryzen 5 5600X 6-Core BOX"], (41_000, 64_000)),
    "ryzen 5 5600g": (["AMD Ryzen 5 5600G with Radeon Graphics BOX"], (40_000, 59_000)),
    "ryzen 5 7600x": (["AMD Ryzen 5 7600X AM5 BOX - Chama"], (58_000, 85_000)),
    "i9-13900k": (["Intel Core i9-13900K BOX - Chama"], (99_000, 144_000)),
    "i7-13700k": (["Intel Core i7-13700K BOX"], (71_000, 104_000)),
    "i5-13600k": (["Intel Core i5-13600K BOX"], (53_000, 79_000)),
    "i5-13400": (["Intel Core i5-13400F BOX"], (37_000, 56_000)),
    "i5-12400": (["Intel Core i5-12400F BOX"], (31_000, 47_000)),
    "16gb ddr4": (["Kingston FURY Beast 16GB DDR4 3200MHz Kit", "HyperX Fury 16GB DDR4 3200MHz"], (13_000, 21_500)),
    "32gb ddr4": (["Kingston FURY Beast 32GB DDR4 3200MHz Kit"], (24_000, 39_000)),
    "1tb nvme": (["Kingston NV2 1TB PCIe 4.0 NVMe M.2", "Kingston KC3000 1TB PCIe 4.0 NVMe M.2"], (16_000, 30_000)),
    "gaming pc": (["Chama Special Build - Ryzen 5 5600G + 16GB + 512GB (Office/Light Gaming)", "Chama Gaming PC - Ryzen 5 5600X + RTX 3060 + 16GB DDR4 + 1TB SSD"], (95_000, 320_000)),
    "laptop": (["Acer Nitro V15 i5-13420H RTX 3050 FHD 144Hz", "HP Omen 16 i7-13700H RTX 4060 165Hz"], (120_000, 310_000)),
    "monitor": (["Acer Nitro XV272U 27-inch QHD 165Hz IPS", "BenQ GW2780 27-inch FHD IPS"], (45_000, 130_000)),
}

_GENERIC_TEMPLATES = [
    "{query} Brand New - Chama Computers",
    "Chama {query} - Sealed Box with Warranty",
    "{query} - Chama Authorized",
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
    return generic_names, (20_000, 180_000)


class ChamaAdapter(BaseAdapter):
    name = "Chama Computers"
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
                    location=random.choice(_LOCATIONS),
                    url=f"https://www.chamacomputers.lk/products/all?search={quote_plus(query)}",
                    date_posted=None,
                    last_updated=None,
                    image_url=None,
                    category="Computer Hardware",
                )
            )

        return listings
