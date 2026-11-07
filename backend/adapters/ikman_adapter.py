"""
Ikman.lk real scraper adapter for PCFinder LK.
Scrapes live advertisements from ikman.lk using httpx and BeautifulSoup.
"""

from __future__ import annotations

import asyncio
import logging
import random
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


class IkmanAdapter(BaseAdapter):
    name = "ikman.lk"
    seller_type = "Individual Seller"
    source_type = "classifieds"

    async def search(self, query: str) -> List[Listing]:
        listings: List[Listing] = []
        search_url = f"https://ikman.lk/en/ads?query={quote_plus(query)}"

        headers = {
            "User-Agent": get_random_ua(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }

        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True, headers=headers) as client:
                resp = await client.get(search_url)
                if resp.status_code != 200:
                    logger.warning(f"Ikman returned status {resp.status_code}")
                    return []

                soup = BeautifulSoup(resp.text, "html.parser")
                # Every ad link matches /en/ad/
                ad_links = soup.find_all("a", href=lambda h: h and "/en/ad/" in h)

                seen_urls = set()
                for a in ad_links:
                    href = a.get("href", "")
                    if href in seen_urls:
                        continue
                    seen_urls.add(href)

                    # Build direct full URL to the actual advertisement
                    actual_url = href if href.startswith("http") else f"https://ikman.lk{href}"

                    # Extract all text tokens inside card
                    tokens = [t.strip() for t in a.stripped_strings if t.strip()]
                    if not tokens:
                        continue

                    title = tokens[0]

                    # Parse condition, location, price, time
                    condition = "Used / Secondhand"
                    location = "Sri Lanka"
                    price_lkr = None
                    date_posted = None

                    for token in tokens:
                        if token.lower() in ["brand new", "new"]:
                            condition = "Brand New"
                        elif token.lower() in ["used", "reconditioned"]:
                            condition = "Used / Secondhand"

                        if "Rs" in token or "LKR" in token:
                            price_lkr = _clean_price(token)

                        if any(c in token for c in ["ago", "day", "days", "hour", "hours", "month", "months", "week", "weeks"]):
                            date_posted = token

                        # Location token often has format: "City, Category"
                        if "," in token and any(cat in token.lower() for cat in ["computer", "accessories", "laptop", "tablet", "electronic", "desktop"]):
                            location = token.split(",")[0].strip()

                    # Image
                    img_tag = a.find("img")
                    img_url = img_tag.get("src") if img_tag else None

                    # Infer warranty from title if mentioned
                    warranty = "Checking Warranty"
                    if "warranty" in title.lower():
                        match = re.search(r"(\d+\s*(?:year|years|month|months)\s*warranty)", title, re.IGNORECASE)
                        warranty = match.group(1).title() if match else "Seller Warranty"
                    else:
                        warranty = "Checking Warranty (Contact Seller)"

                    listings.append(
                        Listing(
                            id=generate_id(),
                            title=title,
                            price_lkr=price_lkr,
                            price_display=format_price(price_lkr),
                            condition=condition,
                            warranty=warranty,
                            source_platform=self.name,
                            seller_type=self.seller_type,
                            location=location,
                            url=actual_url,
                            date_posted=date_posted,
                            last_updated=None,
                            image_url=img_url,
                            category="Classifieds",
                        )
                    )

        except Exception as e:
            logger.error(f"Error scraping ikman.lk: {e}")

        return listings
