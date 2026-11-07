"""
PCFinder LK — FastAPI Backend
==============================
Entry point for the PCFinder LK price aggregator API.

Endpoints
---------
GET /api/health                          → Health check
GET /api/autocomplete?q=<query>          → Product name suggestions
GET /api/search?q=<query>[&filters...]  → Aggregated listings from all adapters
"""

from __future__ import annotations

import asyncio
import json
import sys
import os
from contextlib import asynccontextmanager
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

# ---------------------------------------------------------------------------
# Ensure the backend directory is on sys.path so relative imports work when
# the app is launched from any working directory.
# ---------------------------------------------------------------------------
sys.path.insert(0, os.path.dirname(__file__))

import database
from models import Listing, SearchResponse
from utils import PRODUCT_SUGGESTIONS, generate_query_hash
from relevance import is_strictly_relevant

# Adapters
from adapters.ikman_adapter import IkmanAdapter
from adapters.facebook_adapter import FacebookAdapter
from adapters.nanotek_adapter import NanotekAdapter
from adapters.redline_adapter import RedlineAdapter
from adapters.barclays_adapter import BarclaysAdapter
from adapters.chama_adapter import ChamaAdapter
from adapters.sense_adapter import SenseAdapter
from adapters.winsoft_adapter import WinsoftAdapter
from adapters.mdcomputers_adapter import MDComputersAdapter
from adapters.pentiumcity_adapter import PentiumCityAdapter
from adapters.pcbuilders_adapter import PCBuildersAdapter
from adapters.msk_adapter import MSKAdapter

# ---------------------------------------------------------------------------
# Adapter registry
# ---------------------------------------------------------------------------

ALL_ADAPTERS = [
    IkmanAdapter(),
    NanotekAdapter(),
    RedlineAdapter(),
    BarclaysAdapter(),
    WinsoftAdapter(),
    MDComputersAdapter(),
    PentiumCityAdapter(),
    PCBuildersAdapter(),
    MSKAdapter(),
    ChamaAdapter(),
    SenseAdapter(),
    FacebookAdapter(),
]


# ---------------------------------------------------------------------------
# Application lifespan
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialise the SQLite database on startup."""
    await database.init_db()
    yield
    # (cleanup could go here if needed)


# ---------------------------------------------------------------------------
# App instance
# ---------------------------------------------------------------------------

app = FastAPI(
    title="PCFinder LK API",
    description="Aggregate PC hardware prices from Sri Lankan retailers and classifieds.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Helper: apply filters
# ---------------------------------------------------------------------------

def _apply_filters(
    listings: List[Listing],
    condition: Optional[str],
    min_price: Optional[int],
    max_price: Optional[int],
    location: Optional[str],
    source_type: Optional[str],
    warranty: Optional[str],
) -> List[Listing]:
    """Filter a flat list of Listing objects according to the supplied criteria."""
    result = listings

    if condition:
        result = [l for l in result if l.condition.lower() == condition.lower()]

    if min_price is not None:
        result = [l for l in result if l.price_lkr is not None and l.price_lkr >= min_price]

    if max_price is not None:
        result = [l for l in result if l.price_lkr is not None and l.price_lkr <= max_price]

    if location:
        loc_lower = location.lower()
        result = [l for l in result if loc_lower in l.location.lower()]

    if source_type:
        st_lower = source_type.lower()  # "retail" or "classifieds"
        # Map adapter source_type to seller_type shorthand
        if st_lower == "retail":
            result = [l for l in result if l.seller_type == "Verified Store"]
        elif st_lower == "classifieds":
            result = [l for l in result if l.seller_type == "Individual Seller"]

    if warranty:
        w_lower = warranty.lower()
        result = [l for l in result if w_lower in l.warranty.lower()]

    return result


# ---------------------------------------------------------------------------
# Helper: apply sorting
# ---------------------------------------------------------------------------

def _apply_sort(listings: List[Listing], sort: Optional[str]) -> List[Listing]:
    """Sort listings in-place according to the requested sort strategy."""
    if sort == "price_asc":
        # Push None-price listings to the end
        return sorted(listings, key=lambda l: (l.price_lkr is None, l.price_lkr or 0))
    if sort == "price_desc":
        return sorted(listings, key=lambda l: (l.price_lkr is None, -(l.price_lkr or 0)))
    if sort == "recent":
        # Listings with a date_posted come first (most recent first), then undated
        def _sort_key(l: Listing):
            if l.date_posted:
                return (0, l.date_posted)
            return (1, "")
        return sorted(listings, key=_sort_key, reverse=False)
    # Default: "relevance" — keep the order returned by adapters (retail first, then classifieds)
    return listings


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/api/health", tags=["Meta"])
async def health_check():
    """Simple health probe used by load balancers and the frontend."""
    return {"status": "ok", "service": "PCFinder LK API", "version": "1.0.0"}


@app.get("/api/autocomplete", tags=["Search"])
async def autocomplete(
    q: str = Query(..., min_length=1, max_length=200, description="Partial search query"),
):
    """
    Return up to 10 product name suggestions that contain the query string
    (case-insensitive).
    """
    q_lower = q.strip().lower()
    if not q_lower:
        return {"suggestions": []}

    matches = [s for s in PRODUCT_SUGGESTIONS if q_lower in s.lower()]
    return {"suggestions": matches[:10]}


@app.get("/api/search", response_model=SearchResponse, tags=["Search"])
async def search(
    q: str = Query(..., min_length=1, max_length=200, description="Product search query"),
    condition: Optional[str] = Query(None, description="'Brand New' | 'Used / Secondhand'"),
    min_price: Optional[int] = Query(None, ge=0, description="Minimum price in LKR"),
    max_price: Optional[int] = Query(None, ge=0, description="Maximum price in LKR"),
    location: Optional[str] = Query(None, description="Partial location string, e.g. 'Colombo'"),
    source_type: Optional[str] = Query(None, description="'retail' | 'classifieds'"),
    warranty: Optional[str] = Query(None, description="Partial warranty string, e.g. 'Nanotek'"),
    sort: Optional[str] = Query("relevance", description="'relevance' | 'price_asc' | 'price_desc' | 'recent'"),
):
    """
    Aggregate product listings from all configured adapters, apply optional
    filters and sorting, and return a unified JSON response.

    Results are cached in SQLite for one hour (configurable via CACHE_TTL_HOURS).
    """
    query = q.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query parameter 'q' must not be blank.")

    filters = {
        "condition": condition,
        "min_price": min_price,
        "max_price": max_price,
        "location": location,
        "source_type": source_type,
        "warranty": warranty,
        "sort": sort,
    }

    # 1. Compute cache key
    query_hash = generate_query_hash(query, filters)

    # 2. Check cache
    cached_json = await database.get_cached(query_hash)
    if cached_json is not None:
        cached_data = json.loads(cached_json)
        return SearchResponse(
            query=query,
            total=cached_data["total"],
            results=[Listing(**item) for item in cached_data["results"]],
            cached=True,
            sources_queried=cached_data["sources_queried"],
        )

    # 3. Run all adapters concurrently
    sources_queried = [adapter.name for adapter in ALL_ADAPTERS]
    adapter_results = await asyncio.gather(
        *[adapter.search(query) for adapter in ALL_ADAPTERS],
        return_exceptions=True,
    )

    # 4. Flatten results, skipping any adapters that raised an exception
    all_listings: List[Listing] = []
    for adapter, result in zip(ALL_ADAPTERS, adapter_results):
        if isinstance(result, Exception):
            # Log the error but keep going — partial results are better than none
            print(f"[WARN] Adapter '{adapter.name}' raised {type(result).__name__}: {result}")
        else:
            all_listings.extend(result)

    # 5. Apply filters & query relevance check
    # Filters out store search leaks like power supplies or screen protectors when looking for CPUs
    relevant_listings = [l for l in all_listings if is_strictly_relevant(l.title, query)]

    filtered = _apply_filters(
        relevant_listings,
        condition=condition,
        min_price=min_price,
        max_price=max_price,
        location=location,
        source_type=source_type,
        warranty=warranty,
    )

    # 6. Apply sorting
    sorted_listings = _apply_sort(filtered, sort)

    # 7. Cache results
    cache_payload = {
        "total": len(sorted_listings),
        "results": [listing.model_dump() for listing in sorted_listings],
        "sources_queried": sources_queried,
    }
    await database.set_cache(query_hash, json.dumps(cache_payload))

    # 8. Return response
    return SearchResponse(
        query=query,
        total=len(sorted_listings),
        results=sorted_listings,
        cached=False,
        sources_queried=sources_queried,
    )


# ---------------------------------------------------------------------------
# Dev entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", "8000"))
    debug = os.environ.get("DEBUG", "true").lower() == "true"

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=debug,
    )
