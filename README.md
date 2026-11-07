# PCFinder LK 🇱🇰
### Sri Lanka's PC Hardware Price Aggregator

> Find and compare PC hardware prices from local Sri Lankan retailers and second-hand marketplaces — Nanotek, Redline, Barclays, ikman.lk, Facebook Marketplace, and more.

---

## 📦 Project Structure

```
pcfinder-lk/
├── frontend/          # Next.js 14 App Router (TypeScript + Tailwind)
│   ├── src/
│   │   ├── app/       # Next.js pages & API routes
│   │   ├── components/# React UI components
│   │   ├── lib/       # API client & utilities
│   │   └── types/     # TypeScript interfaces
│   └── Dockerfile
├── backend/           # Python FastAPI service
│   ├── adapters/      # Modular scraper/mock adapters per source
│   ├── main.py        # FastAPI app + endpoints
│   ├── models.py      # Pydantic data models
│   ├── database.py    # SQLite caching layer
│   ├── utils.py       # Shared utilities & UA rotation
│   └── Dockerfile
└── docker-compose.yml
```

---

## 🚀 Quick Start (Local Development)

### Prerequisites
- Node.js 20+
- Python 3.11+
- pip

### 1. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy env file
cp .env.example .env

# Start the backend server
uvicorn main:app --reload --port 8000
```

Backend will be running at: **http://localhost:8000**
API docs (Swagger UI): **http://localhost:8000/docs**

### 2. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start Next.js dev server
npm run dev
```

Frontend will be running at: **http://localhost:3000**

---

## 🐳 Docker Compose (Full Stack)

```bash
# Build and run everything
docker-compose up --build

# Run in background
docker-compose up -d --build
```

| Service  | URL                          |
|----------|------------------------------|
| Frontend | http://localhost:3000        |
| Backend  | http://localhost:8000        |
| API Docs | http://localhost:8000/docs   |

---

## 🔌 API Endpoints

### `GET /api/search`
Search for PC hardware listings across all sources.

**Query Parameters:**
| Param        | Type   | Description                                      |
|--------------|--------|--------------------------------------------------|
| `q`          | string | Search query (e.g., "RTX 3060", "Ryzen 5 5600")  |
| `condition`  | string | `Brand New` / `Used / Secondhand`                |
| `min_price`  | int    | Minimum price in LKR                             |
| `max_price`  | int    | Maximum price in LKR                             |
| `location`   | string | Location filter (e.g., "Colombo", "Negombo")     |
| `source_type`| string | `retail` / `classifieds`                         |
| `warranty`   | string | `any_warranty` / `1year` / `official`            |
| `sort`       | string | `relevance` / `price_asc` / `price_desc` / `recent` |

**Example:**
```
GET /api/search?q=rtx+3060&condition=Brand+New&sort=price_asc&min_price=50000&max_price=120000
```

### `GET /api/autocomplete`
Returns autocomplete suggestions.

```
GET /api/autocomplete?q=rtx
→ ["RTX 3060", "RTX 3060 Ti", "RTX 3070", "RTX 3080", "RTX 4060"]
```

### `GET /api/health`
Health check endpoint.

---

## 📡 Data Sources & Adapters

| Source               | Type         | Seller Type        | Adapter File            |
|----------------------|--------------|--------------------|-------------------------|
| ikman.lk             | Classifieds  | Individual Seller  | `ikman_adapter.py`      |
| Facebook Marketplace | Classifieds  | Individual Seller  | `facebook_adapter.py`   |
| Nanotek              | Retail Store | Verified Store     | `nanotek_adapter.py`    |
| Redline Technologies | Retail Store | Verified Store     | `redline_adapter.py`    |
| Barclays Computers   | Retail Store | Verified Store     | `barclays_adapter.py`   |
| Chama Computers      | Retail Store | Verified Store     | `chama_adapter.py`      |
| Sense.lk             | Retail Store | Verified Store     | `sense_adapter.py`      |

> **Note:** All adapters currently return realistic mock data. See adapter files for comments explaining real Playwright/Cheerio scraping implementation.

---

## 🏗️ Architecture

```
User Browser
     │
     ▼
Next.js Frontend (Port 3000)
     │  API proxy routes
     ▼
FastAPI Backend (Port 8000)
     │
     ├──► SQLite Cache (1 hour TTL)
     │
     ├──► ikman.lk Adapter
     ├──► Facebook Marketplace Adapter
     ├──► Nanotek Adapter
     ├──► Redline Adapter
     ├──► Barclays Adapter
     ├──► Chama Adapter
     └──► Sense Adapter
```

---

## 🔧 Adding a New Source Adapter

1. Create `backend/adapters/mystore_adapter.py`:

```python
from adapters.base import BaseAdapter
from models import Listing
from utils import generate_id, format_price
import httpx
from bs4 import BeautifulSoup

class MyStoreAdapter(BaseAdapter):
    name = "MyStore"
    seller_type = "Verified Store"
    
    async def search(self, query: str) -> list[Listing]:
        # Real implementation with httpx + BeautifulSoup:
        async with httpx.AsyncClient(headers={"User-Agent": get_random_ua()}) as client:
            resp = await client.get(f"https://mystore.lk/search?q={query}")
            soup = BeautifulSoup(resp.text, "html.parser")
            # Parse listings...
        
        return listings
```

2. Register in `main.py`:
```python
from adapters.mystore_adapter import MyStoreAdapter
adapters = [..., MyStoreAdapter()]
```

---

## 🛡️ Scraping Resilience Features

- **User-Agent Rotation**: 20+ real browser UA strings rotated per request
- **Request Delays**: Random 1-3s delay between requests per adapter
- **SQLite Cache**: 1-hour query result cache prevents repeated scraping
- **Async Concurrency**: All adapters run in parallel via `asyncio.gather`
- **Graceful Fallback**: Failed adapters log errors and return empty list (don't crash search)

---

## 🗺️ Roadmap

- [ ] Real Playwright scraping for ikman.lk
- [ ] Facebook Marketplace scraping (requires auth cookie)
- [ ] Product image fetching & caching
- [ ] Price history tracking & charts
- [ ] Price drop alerts via email/Telegram
- [ ] Mobile app (React Native)
- [ ] Browser extension for inline price comparison
- [ ] Admin dashboard for adapter health monitoring

---

## 📄 License

MIT License — Free to use and modify.
