"""
Barclays Computers live scraper adapter for PCFinder LK.
Queries Barclays search system (barclays.lk/searchresult.asp) and asynchronously
fetches live prices for matching items.
"""

from __future__ import annotations

import asyncio
import logging
import re
from typing import List

import httpx
from bs4 import BeautifulSoup

from adapters.base import BaseAdapter
from models import Listing
from utils import format_price, generate_id, get_random_ua

logger = logging.getLogger(__name__)


def _clean_price(raw_text: str | None) -> int | None:
    if not raw_text:
        return None
    # e.g. "464,650.00 per unit" -> 464650
    cleaned = raw_text.split(".")[0]
    digits = re.sub(r"[^\d]", "", cleaned)
    return int(digits) if digits else None


class BarclaysAdapter(BaseAdapter):
    name = "Barclays Computers"
    seller_type = "Verified Store"
    source_type = "retail"

    async def _fetch_item_price(self, client: httpx.AsyncClient, url: str) -> tuple[int | None, str | None]:
        """Fetch the exact product page to extract real price and image."""
        try:
            resp = await client.get(url, timeout=6.0)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                
                # Check for <span class="price">
                price_el = soup.find("span", class_="price")
                if not price_el:
                    # Fallback: look for span with 'per unit' or numbers
                    for s in soup.find_all("span"):
                        if "per" in s.get_text() and ("unit" in s.get_text() or any(c.isdigit() for c in s.get_text())):
                            price_el = s
                            break
                
                price_lkr = _clean_price(price_el.get_text(strip=True)) if price_el else None

                # Image
                img_el = soup.find("img", src=lambda s: s and ("/mmBC/Images/" in s or "item" in s.lower()))
                img_url = None
                if img_el and img_el.get("src"):
                    src = img_el.get("src")
                    img_url = src if src.startswith("http") else f"https://www.barclays.lk/{src.lstrip('/')}"

                return price_lkr, img_url
        except Exception as e:
            logger.debug(f"Error fetching Barclays item {url}: {e}")
        return None, None

    async def search(self, query: str) -> List[Listing]:
        listings: List[Listing] = []
        search_url = "https://www.barclays.lk/searchresult.asp"

        form_data = {
            "SearchWord": query,
            "FrmSearchWords": query,
            "hidSearchStringType": "2",
        }

        headers = {
            "User-Agent": get_random_ua(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True, headers=headers) as client:
                resp = await client.post(search_url, data=form_data)
                if resp.status_code != 200:
                    logger.warning(f"Barclays returned status {resp.status_code}")
                    return []

                soup = BeautifulSoup(resp.text, "html.parser")
                product_links = soup.find_all("a", href=lambda h: h and "itemdesc.asp" in h)

                items_to_fetch = []
                seen_urls = set()

                for a in product_links:
                    title = a.get_text(strip=True)
                    if not title or len(title) < 4:
                        continue

                    href = a.get("href", "")
                    if href in seen_urls:
                        continue
                    seen_urls.add(href)

                    actual_url = href if href.startswith("http") else f"https://www.barclays.lk/{href.lstrip('/')}"
                    items_to_fetch.append((title, actual_url))

                # Limit to top 10 relevant items for quick response
                items_to_fetch = items_to_fetch[:10]

                # Fetch real prices concurrently
                price_tasks = [self._fetch_item_price(client, url) for _, url in items_to_fetch]
                price_results = await asyncio.gather(*price_tasks, return_exceptions=True)

                for (title, actual_url), res in zip(items_to_fetch, price_results):
                    price_lkr = None
                    img_url = None
                    if isinstance(res, tuple):
                        price_lkr, img_url = res

                    # Warranty in title
                    warranty = "Official Distributor Warranty"
                    if "(3y)" in title.lower():
                        warranty = "3 Years Barclays Warranty"
                    elif "(2y)" in title.lower():
                        warranty = "2 Years Barclays Warranty"
                    elif "(1y)" in title.lower():
                        warranty = "1 Year Barclays Warranty"

                    # Category
                    category = "Computer Hardware"
                    if "laptop" in title.lower():
                        category = "Laptops"
                    elif "vga" in title.lower() or "card" in title.lower() or "rtx" in title.lower():
                        category = "Graphics Cards"
                    elif "motherboard" in title.lower():
                        category = "Motherboards"
                    elif "cpu" in title.lower() or "ryzen" in title.lower() or "intel" in title.lower():
                        category = "Processors"

                    listings.append(
                        Listing(
                            id=generate_id(),
                            title=title,
                            price_lkr=price_lkr,
                            price_display=format_price(price_lkr) if price_lkr else "Contact Store",
                            condition="Brand New",
                            warranty=warranty,
                            source_platform=self.name,
                            seller_type=self.seller_type,
                            location="Colombo 03",
                            url=actual_url,
                            date_posted=None,
                            last_updated=None,
                            image_url=img_url,
                            category=category,
                        )
                    )

        except Exception as e:
            logger.error(f"Error scraping Barclays: {e}")

        return listings
