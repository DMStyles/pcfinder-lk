"""
Facebook Marketplace adapter for PCFinder LK.

MOCK IMPLEMENTATION
-------------------
Facebook Marketplace requires a logged-in session and uses a heavy GraphQL
API — real scraping would require Playwright with cookie authentication:

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False)  # headless often blocked
        ctx = await browser.new_context(
            storage_state="fb_cookies.json",   # pre-saved login session
            user_agent=get_random_ua(),
        )
        page = await ctx.new_page()
        await page.goto(
            f"https://www.facebook.com/marketplace/112800595398985/search?query={query}",
            wait_until="networkidle",
        )
        # Facebook renders listings as <div aria-label="Marketplace item"> elements:
        items = await page.query_selector_all('[aria-label="Marketplace item"]')
        for item in items:
            title    = await (await item.query_selector("span.x1lliihq")).inner_text()
            price_el = await item.query_selector("span.x193iq5w")
            price    = await price_el.inner_text() if price_el else None
            location = await (await item.query_selector("span.x1nxh6w3")).inner_text()
            img_el   = await item.query_selector("img")
            img_url  = await img_el.get_attribute("src") if img_el else None
            link_el  = await item.query_selector("a")
            url      = await link_el.get_attribute("href")
            # … parse + yield Listing(...)
        await browser.close()

NOTE: Rotating cookies from multiple accounts and randomising scroll/click
      behaviour is essential to avoid detection and account suspension.
"""

from __future__ import annotations

import asyncio
import random
from datetime import datetime, timedelta
from typing import List
from urllib.parse import quote_plus

from adapters.base import BaseAdapter
from models import Listing
from utils import format_price, generate_id

# ---------------------------------------------------------------------------
# Data pools
# ---------------------------------------------------------------------------

_FB_LOCATIONS = [
    "Negombo", "Colombo", "Gampaha", "Wattala", "Ja-Ela",
    "Kelaniya", "Ragama", "Kandana", "Seeduwa", "Katunayake",
    "Marawila", "Minuwangoda",
]

_FB_WARRANTIES = [
    "No Warranty",
    "No Warranty",
    "No Warranty",
    "3 Months Checking Warranty",
    "Seller Warranty 6 Months",
]

_COMPONENT_DATA: dict[str, tuple[list[str], tuple[int, int]]] = {
    "rtx 5090": (["RTX 5090 32GB GDDR7 - Like New with Box", "GeForce RTX 5090 OC 32GB"], (850_000, 1_100_000)),
    "rtx 5080": (["RTX 5080 16GB GDDR7 - 1 Month Used", "ASUS TUF RTX 5080 16GB"], (420_000, 520_000)),
    "rtx 5070 ti": (["RTX 5070 Ti 16GB GDDR7 Sealed", "ZOTAC RTX 5070 Ti 16GB"], (280_000, 340_000)),
    "rtx 5070": (["RTX 5070 12GB GDDR7 - Brand New", "MSI RTX 5070 Ventus 2X 12GB"], (210_000, 260_000)),
    "rtx 5060 ti": (["RTX 5060 Ti 16GB GDDR7 - 2 Months Old", "ASUS Dual RTX 5060 Ti 8GB"], (185_000, 235_000)),
    "rtx 5060": (["RTX 5060 8GB GDDR7 - Sealed Box", "MSI RTX 5060 8GB GDDR7 Like New", "ASUS Dual RTX 5060 8GB GDDR7"], (140_000, 175_000)),
    "rtx 4090": (["RTX 4090 24GB GDDR6X - Slight Use", "GeForce RTX 4090 OC 24GB"], (340_000, 470_000)),
    "rtx 4080": (["RTX 4080 16GB - Used 6 Months", "ASUS ROG RTX 4080 16GB OC"], (260_000, 340_000)),
    "rtx 4070 ti": (["RTX 4070 Ti 12GB GDDR6X Lightly Used"], (220_000, 280_000)),
    "rtx 4070": (["RTX 4070 12GB DDR6 - 1 Month Old", "ASUS Dual RTX 4070 12GB Used"], (160_000, 210_000)),
    "rtx 4060 ti": (["RTX 4060 Ti 8GB - Good Condition"], (115_000, 155_000)),
    "rtx 4060": (["RTX 4060 8GB - Like New", "MSI RTX 4060 Gaming X 8GB Used"], (85_000, 118_000)),
    "rtx 3090": (["RTX 3090 24GB GDDR6X - Mined Very Little", "ASUS Strix RTX 3090 24GB"], (210_000, 290_000)),
    "rtx 3080": (["RTX 3080 10GB Used", "MSI RTX 3080 Gaming Trio 10GB"], (155_000, 215_000)),
    "rtx 3070": (["RTX 3070 8GB DDR6 - Used 1 Year", "ASUS TUF RTX 3070 OC 8GB"], (100_000, 145_000)),
    "rtx 3060 ti": (["RTX 3060 Ti 8GB Used", "Gigabyte RTX 3060 Ti OC 8GB"], (80_000, 115_000)),
    "rtx 3060": (["RTX 3060 12GB Used - Working Fine", "ASUS Dual RTX 3060 12GB OC Used", "Zotac RTX 3060 Twin Edge 12GB"], (68_000, 98_000)),
    "gtx 1660": (["GTX 1660 Super 6GB Used", "MSI GTX 1660 Ti Ventus 6GB"], (38_000, 60_000)),
    "rx 6800": (["RX 6800 XT 16GB Used", "Sapphire Nitro RX 6800 XT 16GB"], (120_000, 170_000)),
    "rx 6700": (["RX 6700 XT 12GB Used", "ASUS TUF RX 6700 XT OC"], (88_000, 125_000)),
    "rx 6600": (["RX 6600 8GB Used Condition Good", "Sapphire Pulse RX 6600 8GB"], (55_000, 80_000)),
    "ryzen 9 5900x": (["Ryzen 9 5900X 12-Core - Selling Upgrade"], (75_000, 110_000)),
    "ryzen 7 5800x": (["Ryzen 7 5800X 8-Core Used", "AMD Ryzen 7 5800X3D Gaming CPU"], (50_000, 75_000)),
    "ryzen 5 5600x": (["Ryzen 5 5600X 6-Core Used", "AMD Ryzen 5 5600X BOX"], (35_000, 55_000)),
    "ryzen 5 5600g": (["Ryzen 5 5600G with Radeon Graphics Used"], (32_000, 50_000)),
    "i9-13900k": (["Intel i9-13900K 24-Core Used"], (85_000, 125_000)),
    "i7-13700k": (["Intel i7-13700K Used - Upgrade Sale", "Core i7-13700KF Unlocked BOX"], (60_000, 92_000)),
    "i5-13600k": (["Intel i5-13600K 14-Core Used"], (45_000, 68_000)),
    "i5-13400": (["Intel i5-13400F 10-Core Used Good Condition"], (32_000, 50_000)),
    "i5-12400": (["Intel i5-12400F 6-Core Used"], (25_000, 40_000)),
    "16gb ddr4": (["16GB DDR4 3200MHz RAM Used", "Corsair 16GB DDR4 RAM"], (10_000, 18_000)),
    "32gb ddr4": (["32GB DDR4 3200MHz Kit Used", "G.Skill 32GB DDR4 Kit"], (19_000, 32_000)),
    "1tb nvme": (["1TB NVMe SSD Used - Samsung/WD", "Samsung 970 EVO Plus 1TB NVMe"], (13_000, 25_000)),
    "gaming pc": (["Full Custom Gaming PC i5-12400F + GTX 1660 Super + 16GB DDR4", "Gaming PC Ryzen 5 5600X + RTX 3060 12GB + 16GB + 512GB SSD", "Budget Gaming PC Negotiable Price"], (95_000, 360_000)),
    "laptop": (["Gaming Laptop Ryzen 7 RTX 3060 Used - Good Condition", "HP Victus 15 i5-12450H GTX 1650 Used", "ASUS ROG G15 Used 1 Year"], (100_000, 270_000)),
    "monitor": (["24-inch 144Hz FHD Monitor Used", "27-inch 1440p Gaming Monitor Used"], (35_000, 125_000)),
    "keyboard": (["Mechanical Gaming Keyboard Used - Razer/Corsair"], (5_000, 28_000)),
    "mouse": (["Gaming Mouse Used - Logitech/Razer"], (3_000, 18_000)),
}

_GENERIC_TITLES = [
    "{query} - Good Condition Must Sell",
    "{query} Used - Selling Due to Upgrade",
    "{query} Like New with Accessories",
    "{query} - Price Negotiable",
]


def _resolve_component(query: str) -> tuple[list[str], tuple[int, int]]:
    q_lower = query.lower()
    best_key = ""
    for key in _COMPONENT_DATA:
        if key in q_lower and len(key) > len(best_key):
            best_key = key
    if best_key:
        return _COMPONENT_DATA[best_key]
    generic_names = [t.format(query=query.title()) for t in _GENERIC_TITLES]
    return generic_names, (10_000, 150_000)


def _random_date_posted(days_back: int = 25) -> str:
    delta = timedelta(days=random.randint(0, days_back), hours=random.randint(0, 23))
    dt = datetime.utcnow() - delta
    return dt.strftime("%Y-%m-%d")


class FacebookAdapter(BaseAdapter):
    name = "Facebook Marketplace"
    seller_type = "Individual Seller"
    source_type = "classifieds"

    async def search(self, query: str) -> List[Listing]:
        await asyncio.sleep(random.uniform(0.1, 0.5))

        name_pool, (price_min, price_max) = _resolve_component(query)
        num_results = random.randint(4, 6)
        listings: List[Listing] = []

        # Colombo district marketplace node id: 112800595398985
        base_url = (
            f"https://www.facebook.com/marketplace/112800595398985/search"
            f"?query={quote_plus(query)}"
        )

        for _ in range(num_results):
            title = random.choice(name_pool)
            if random.random() < 0.25:
                title += " " + random.choice(["(Urgent)", "- Final Price", "- DM for Details"])
            price = random.randint(price_min // 1000, price_max // 1000) * 1000
            price_lkr = price if random.random() > 0.2 else None

            listing_id = generate_id()
            listings.append(
                Listing(
                    id=listing_id,
                    title=title,
                    price_lkr=price_lkr,
                    price_display=format_price(price_lkr),
                    condition="Used / Secondhand" if random.random() < 0.85 else "Brand New",
                    warranty=random.choice(_FB_WARRANTIES),
                    source_platform=self.name,
                    seller_type=self.seller_type,
                    location=random.choice(_FB_LOCATIONS),
                    url=f"https://www.facebook.com/marketplace/colombo/search/?query={quote_plus(query)}",
                    date_posted=_random_date_posted(),
                    last_updated=_random_date_posted(3),
                    image_url=None,
                    category="Electronics",
                )
            )

        return listings
