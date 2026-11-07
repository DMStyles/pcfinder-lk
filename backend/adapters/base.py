"""
Abstract base class for all PCFinder LK adapters.

Each concrete adapter must:
  - Set a class-level ``name`` string (display name shown to the user).
  - Set a class-level ``seller_type`` string ("Verified Store" | "Individual Seller").
  - Set a class-level ``source_type`` string ("retail" | "classifieds").
  - Implement the async ``search`` method which returns a list of Listing objects.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from models import Listing


class BaseAdapter(ABC):
    name: str = "Unknown"
    seller_type: str = "Individual Seller"
    source_type: str = "classifieds"

    @abstractmethod
    async def search(self, query: str) -> List[Listing]:
        """
        Run a product search for *query* and return a list of Listing objects.
        Implementations must be async-safe (use ``asyncio.sleep`` for delays,
        not ``time.sleep``).
        """
        ...
