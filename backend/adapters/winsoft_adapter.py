"""
Winsoft Computers live scraper adapter for PCFinder LK.
Scrapes live inventory from winsoft.lk (Colombo 04) with direct links.
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


class WinsoftAdapter(BaseAdapter):
    name = "Winsoft"
    seller_type = "Verified Store"
    source_type = "retail"

    async def search(self, query: str) -> List[Listing]:
        listings: List[Listing] = []
        search_url = f"https://www.winsoft.lk/?s={quote_plus(query)}&post_type=product"

        headers = {
            "User-Agent": get_random_ua(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        }

        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True, headers=headers) as client:
                resp = await client.get(search_url)
                if resp.status_code != 200:
                    logger.warning(f"Winsoft returned status {resp.status_code}")
                    return []

                soup = BeautifulSoup(resp.text, "html.parser")
                product_links = soup.find_all("a", href=lambda h: h and "/product/" in h)

                seen_urls = set()
                for a in product_links:
                    href = a.get("href", "")
                    if href in seen_urls:
                        continue
                    seen_urls.add(href)

                    # Extract card container
                    parent = a.find_parent("div")
                    if not parent:
                        continue

                    # Title from h2/h1 or anchor text
                    title_el = a.find(["h2", "h1", "h3"]) or parent.find(["h2", "h1", "h3"])
                    title = title_el.get_text(strip=True) if title_el else a.get_text(strip=True)
                    if not title or len(title) < 4:
                        continue

                    # Filter for relevance to query words
                    q_words = [w.lower() for w in query.split() if len(w) > 2]
                    if q_words and not any(w in title.lower() for w in q_words):
                        continue

                    # Price
                    price_el = parent.find("span", class_="ty-price") or parent.find(class_=lambda c: c and "price" in c)
                    price_lkr = _clean_price(price_el.get_text(strip=True)) if price_el else None

                    img_el = a.find("img") or parent.find("img")
                    img_url = img_el.get("src") if img_el else None

                    listings.append(
                        Listing(
                            id=generate_id(),
                            title=title,
                            price_lkr=price_lkr,
                            price_display=format_price(price_lkr),
                            condition="Brand New",
                            warranty="Official Distributor Warranty",
                            source_platform=self.name,
                            seller_type=self.seller_type,
                            location="Colombo 04",
                            url=href,
                            date_posted=None,
                            last_updated=None,
                            image_url=img_url,
                            category="Computer Hardware",
                        )
                    )

        except Exception as e:
            logger.error(f"Error scraping Winsoft: {e}")

        return listings
