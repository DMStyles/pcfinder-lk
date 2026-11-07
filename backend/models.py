"""
Pydantic data models for PCFinder LK.
"""

from __future__ import annotations

from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class Listing(BaseModel):
    id: str                                     # uuid4 string
    title: str
    price_lkr: Optional[int] = None             # raw integer price in LKR
    price_display: str                          # e.g. "Rs. 45,000"
    condition: Literal["Brand New", "Used / Secondhand", "Unknown"]
    warranty: str                               # e.g. "3 Years Nanotek Warranty" or "No Warranty"
    source_platform: str                        # e.g. "ikman.lk", "Nanotek", "Facebook Marketplace"
    seller_type: Literal["Verified Store", "Individual Seller"]
    location: str
    url: str
    date_posted: Optional[str] = None           # ISO-8601 date string or human label
    last_updated: Optional[str] = None
    image_url: Optional[str] = None
    category: Optional[str] = None


class SearchRequest(BaseModel):
    q: str = Field(..., min_length=1, max_length=200)
    condition: Optional[str] = None
    min_price: Optional[int] = None
    max_price: Optional[int] = None
    location: Optional[str] = None
    source_type: Optional[str] = None          # "retail" | "classifieds" | None
    warranty: Optional[str] = None
    sort: Optional[str] = "relevance"          # "price_asc" | "price_desc" | "recent" | "relevance"


class SearchResponse(BaseModel):
    query: str
    total: int
    results: List[Listing]
    cached: bool
    sources_queried: List[str]
