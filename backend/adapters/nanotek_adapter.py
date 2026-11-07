"""
Nanotek Computer Systems live scraper adapter for PCFinder LK.
Scrapes nanotek.lk search results directly for real hardware stock, live prices, and direct links.
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
    digits = re.sub(r"[^\d]", "", raw_text)
    return int(digits) if digits else None


class NanotekAdapter(BaseAdapter):
    name = "Nanotek"
    seller_type = "Verified Store"
    source_type = "retail"

    async def search(self, query: str) -> List[Listing]:
        listings: List[Listing] = []
        search_url = f"https://www.nanotek.lk/search?q={quote_plus(query)}"

        headers = {
            "User-Agent": get_random_ua(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        }

        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True, headers=headers) as client:
                resp = await client.get(search_url)
                if resp.status_code != 200:
                    logger.warning(f"Nanotek returned status {resp.status_code}")
                    return []

                soup = BeautifulSoup(resp.text, "html.parser")
                product_links = soup.find_all("a", href=lambda h: h and "/product/" in h)

                seen_urls = set()
                for a in product_links:
                    href = a.get("href", "")
                    if href in seen_urls:
                        continue
                    seen_urls.add(href)

                    actual_url = href if href.startswith("http") else f"https://www.nanotek.lk{href}"

                    # Title
                    title_el = a.find("h1") or a.find("div", class_="ty-productBlock-title")
                    title = title_el.get_text(strip=True) if title_el else None
                    if not title or len(title) < 3:
                        continue

                    # Price
                    price_el = a.find("h2", class_="ty-productBlock-price-retail") or a.find("div", class_="ty-productBlock-price")
                    price_lkr = _clean_price(price_el.get_text(strip=True)) if price_el else None

                    # Category
                    cat_el = a.find("span", class_="ty-productBlock-cat")
                    category = cat_el.get_text(strip=True) if cat_el else "PC Hardware"

                    # Image
                    img_el = a.find("img")
                    img_url = img_el.get("src") if img_el else None

                    # Warranty estimation for official distributor
                    warranty = "3 Years Nanotek Warranty"
                    if "tray" in title.lower() or "used" in title.lower():
                        warranty = "1 Year Warranty"
                    elif "monitor" in title.lower() or "laptop" in title.lower():
                        warranty = "2 Years Nanotek Warranty"

                    listings.append(
                        Listing(
                            id=generate_id(),
                            title=title,
                            price_lkr=price_lkr,
                            price_display=format_price(price_lkr),
                            condition="Brand New",
                            warranty=warranty,
                            source_platform=self.name,
                            seller_type=self.seller_type,
                            location="Colombo 10",
                            url=actual_url,
                            date_posted=None,
                            last_updated=None,
                            image_url=img_url,
                            category=category,
                        )
                    )

        except Exception as e:
            logger.error(f"Error scraping Nanotek: {e}")

        return listings
