"""
PC Builders LK live scraper adapter for PCFinder LK.
Scrapes pcbuilders.lk (Yakkala / Islandwide) for custom gaming rigs, laptops, and components.
"""

from __future__ import annotations

import asyncio
import logging
import re
from typing import List
from urllib.parse import quote_plus

import httpx
from bs4 import BeautifulSoup

from adapters.base import BaseAdapter
from models import Listing
from utils import format_price, generate_id, get_random_ua

logger = logging.getLogger(__name__)


def _clean_price(raw_text: str | None) -> int | None:
    if not raw_text:
        return None
    # Matches LKR 63,000.00 or Rs. 63,000
    m = re.search(r"(?:LKR|Rs\.?)\s*([\d,]+(?:\.\d+)?)", raw_text, re.IGNORECASE)
    if m:
        num_str = m.group(1).split(".")[0]
        digits = re.sub(r"[^\d]", "", num_str)
        return int(digits) if digits else None
    digits = re.sub(r"[^\d]", "", raw_text.split(".")[0])
    return int(digits) if digits else None


class PCBuildersAdapter(BaseAdapter):
    name = "PC Builders LK"
    seller_type = "Verified Store"
    source_type = "retail"

    async def search(self, query: str) -> List[Listing]:
        listings: List[Listing] = []
        search_url = f"https://pcbuilders.lk/?s={quote_plus(query)}&post_type=product&product_cat=0"

        headers = {
            "User-Agent": get_random_ua(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        }

        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True, headers=headers) as client:
                resp = await client.get(search_url)
                if resp.status_code != 200:
                    logger.warning(f"PC Builders LK returned status {resp.status_code}")
                    return []

                soup = BeautifulSoup(resp.text, "html.parser")
                cards = soup.select(".pcb-card-block")

                seen_urls = set()
                q_words = [w.lower() for w in query.split() if len(w) > 2]

                for card in cards:
                    a = card.find("a", href=lambda href: href and href.startswith("https://pcbuilders.lk/"))
                    if not a:
                        continue

                    title_el = card.find(["h2", "h3", "h4"])
                    title = title_el.get_text(strip=True) if title_el else a.get_text(strip=True)
                    href = a.get("href", "")

                    if href in seen_urls or len(title) < 4:
                        continue
                    seen_urls.add(href)

                    # Title relevance filter:
                    # Prevent false positives like B650 motherboard showing up for "Ryzen 5 5600"
                    # because of RAM speed "5600(OC)" in the product description.
                    t_lower = title.lower()
                    if q_words:
                        # If searching specifically for CPU like ryzen, don't show motherboards unless query has 'b650' or 'motherboard'
                        if "ryzen" in q_words and "motherboard" in t_lower and not any(m in query.lower() for m in ["motherboard", "b650", "b550", "a520", "board", "mb"]):
                            continue
                        if not any(w in t_lower for w in q_words):
                            continue

                    # Condition
                    condition = "Brand New"
                    if "used" in t_lower or "pre-owned" in t_lower:
                        condition = "Used / Secondhand"

                    # Price extraction: looks for "LKR 63,000.00" in card text
                    card_text = card.get_text(" ", strip=True)
                    price_lkr = _clean_price(card_text)

                    # Image
                    img_el = card.find("img")
                    img_url = img_el.get("src") if img_el else None

                    # Warranty
                    warranty = "Official Distributor Warranty"
                    if "(3 years warranty)" in t_lower or "3 years" in t_lower:
                        warranty = "3 Years Official Warranty"
                    elif "used" in t_lower:
                        warranty = "Checking Warranty"

                    listings.append(
                        Listing(
                            id=generate_id(),
                            title=title,
                            price_lkr=price_lkr,
                            price_display=format_price(price_lkr) if price_lkr else "Contact Store",
                            condition=condition,
                            warranty=warranty,
                            source_platform=self.name,
                            seller_type=self.seller_type,
                            location="Yakkala / Western Province",
                            url=href,
                            date_posted=None,
                            last_updated=None,
                            image_url=img_url,
                            category="PC Hardware",
                        )
                    )

        except Exception as e:
            logger.error(f"Error scraping PC Builders LK: {e}")

        return listings
