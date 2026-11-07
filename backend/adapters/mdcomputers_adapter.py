"""
MD Computers LK live scraper adapter for PCFinder LK.
Scrapes mdcomputers.lk for live PC components and graphics cards.
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
    # MD computers formats: "Rs:142,000.00or 3 XRs:..."
    m = re.search(r"(?:Rs:?|LKR)\s*([\d,]+)", raw_text, re.IGNORECASE)
    if m:
        digits = re.sub(r"[^\d]", "", m.group(1))
        return int(digits) if digits else None
    digits = re.sub(r"[^\d]", "", raw_text.split(".")[0])
    return int(digits) if digits else None


class MDComputersAdapter(BaseAdapter):
    name = "MD Computers"
    seller_type = "Verified Store"
    source_type = "retail"

    async def search(self, query: str) -> List[Listing]:
        listings: List[Listing] = []
        search_url = f"https://mdcomputers.lk/?s={quote_plus(query)}&post_type=product"

        headers = {
            "User-Agent": get_random_ua(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        }

        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True, headers=headers) as client:
                resp = await client.get(search_url)
                if resp.status_code != 200:
                    logger.warning(f"MD Computers returned status {resp.status_code}")
                    return []

                soup = BeautifulSoup(resp.text, "html.parser")
                cards = soup.select("li.product, div.product, article.product, div.type-product")

                seen_urls = set()
                for card in cards:
                    a = card.find("a", href=lambda h: h and "/product/" in h)
                    if not a:
                        continue

                    href = a.get("href", "")
                    if href in seen_urls:
                        continue
                    seen_urls.add(href)

                    title_el = card.select_one(".woocommerce-loop-product__title, h2, h3, .name")
                    title = title_el.get_text(strip=True) if title_el else a.get_text(strip=True)
                    if not title or len(title) < 4:
                        continue

                    # Condition: Brand new vs Used
                    condition = "Brand New"
                    if any(w in title.lower() for w in ["used", "pre-owned", "refurbished", "pre owned"]):
                        condition = "Used / Secondhand"

                    price_el = card.select_one(".price, span.woocommerce-Price-amount, bdi")
                    price_lkr = _clean_price(price_el.get_text(strip=True)) if price_el else None

                    img_el = card.find("img")
                    img_url = img_el.get("src") if img_el else None

                    warranty = "1 Year MD Computers Warranty"
                    if "used" in title.lower():
                        warranty = "3 Months Checking Warranty"
                    elif "3y" in title.lower() or "3 year" in title.lower():
                        warranty = "3 Years Official Warranty"

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
                            location="Colombo",
                            url=href,
                            date_posted=None,
                            last_updated=None,
                            image_url=img_url,
                            category="Computer Hardware",
                        )
                    )

        except Exception as e:
            logger.error(f"Error scraping MD Computers: {e}")

        return listings
