"""
MSK Computers live scraper adapter for PCFinder LK.
Scrapes mskcomputers.lk product catalog for hardware components.
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
    m = re.search(r"(?:LKR|Rs\.?)\s*([\d,]+)", raw_text, re.IGNORECASE)
    if m:
        digits = re.sub(r"[^\d]", "", m.group(1))
        return int(digits) if digits else None
    digits = re.sub(r"[^\d]", "", raw_text.split(".")[0])
    return int(digits) if digits else None


class MSKAdapter(BaseAdapter):
    name = "MSK Computers"
    seller_type = "Verified Store"
    source_type = "retail"

    async def search(self, query: str) -> List[Listing]:
        listings: List[Listing] = []
        search_url = f"https://mskcomputers.lk/products/search?search={quote_plus(query)}"

        headers = {
            "User-Agent": get_random_ua(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        }

        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True, headers=headers) as client:
                resp = await client.get(search_url)
                if resp.status_code != 200:
                    logger.warning(f"MSK Computers returned status {resp.status_code}")
                    return []

                soup = BeautifulSoup(resp.text, "html.parser")
                headers_el = soup.find_all(["h2", "h3", "h4", "h5"])

                seen_urls = set()
                q_words = [w.lower() for w in query.split() if len(w) > 2]

                for h in headers_el:
                    a = h.find("a")
                    if not a:
                        continue

                    title = h.get_text(strip=True)
                    href = a.get("href", "")
                    if href in seen_urls or len(title) < 4:
                        continue
                    seen_urls.add(href)

                    # Only keep listings relevant to query
                    if q_words and not any(w in title.lower() for w in q_words):
                        continue

                    parent = h.find_parent("div")
                    price_lkr = None
                    if parent:
                        full_txt = parent.get_text(" ", strip=True)
                        price_lkr = _clean_price(full_txt)

                    img_el = parent.find("img") if parent else None
                    img_url = img_el.get("src") if img_el else None

                    listings.append(
                        Listing(
                            id=generate_id(),
                            title=title,
                            price_lkr=price_lkr,
                            price_display=format_price(price_lkr) if price_lkr else "Contact Store",
                            condition="Brand New",
                            warranty="1 Year MSK Warranty",
                            source_platform=self.name,
                            seller_type=self.seller_type,
                            location="Colombo",
                            url=href,
                            date_posted=None,
                            last_updated=None,
                            image_url=img_url,
                            category="Computer Hardware",
                        )
                    )

        except Exception as e:
            logger.error(f"Error scraping MSK Computers: {e}")

        return listings
