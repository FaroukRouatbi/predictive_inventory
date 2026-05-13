# Predictive Inventory Management System

A full-stack inventory management system with an AI-powered demand forecasting engine that automatically selects the optimal prediction model from 4 algorithms based on backtested accuracy.

Built with **FastAPI**, **React**, **PostgreSQL**, **Redis**, and **Docker**.

---

## Features

- **Product & Inventory Management** — Full CRUD API for products and real-time stock tracking
- **Demand Forecasting Engine** — Automated model selection across 4 algorithms (Simple Moving Average, Weighted Moving Average, Linear Trend, Seasonal Decomposition) using backtested MAE accuracy
- **Factor Detection** — Trend detection (R²), seasonality detection (CV), and volatility/risk scoring with industry-standard safety stock formula (Z × σ × √lead_time)
- **Automated Reorder Alerts** — Background tasks trigger forecast-based reorder recommendations when stock drops below threshold
- **Sales Tracking** — Historical sales recording with revenue reporting and date-window queries
- **Authentication** — JWT authentication + Google OAuth2 SSO
- **Redis Caching** — Forecast responses cached with 5-minute TTL
- **Rate Limiting** — Per-endpoint rate limiting (5–60 requests/minute based on cost)
- **Synthetic Data Seeder** — Generates 120 days of realistic sales history across 4 products with distinct demand patterns (stable trend, seasonal cycles, high volatility, flat demand) designed to validate each forecasting model
- **Dockerized** — Full stack runs with a single `docker-compose up` command

---

## Tech Stack

### Backend
| Technology | Purpose |
|---|---|
| Python 3.12 | Language |
| FastAPI | API framework |
| SQLAlchemy 2.0 | ORM |
| PostgreSQL | Primary database |
| Alembic | Database migrations |
| Pydantic v2 | Data validation |
| Redis | Caching + rate limiting |
| JWT + OAuth2 | Authentication |
| Docker + Nginx | Containerization + reverse proxy |

### Frontend
| Technology | Purpose |
|---|---|
| React 19 + TypeScript | UI framework |
| Vite | Build tool |
| TanStack Query | Server state management |
| Recharts | Data visualization |
| Tailwind CSS | Styling |
| Axios | HTTP client |

---

## Architecture

The backend follows a **modular layered architecture**:

```
API Layer (endpoints/)     → HTTP request/response, error handling
Service Layer (services/)  → Business logic (forecasting engine, alerts)
CRUD Layer (crud/)         → Database operations, returns None on miss
Model Layer (models/)      → SQLAlchemy DB models
Schema Layer (schemas/)    → Pydantic validation schemas
```

Key architectural decisions:
- **CRUD/Endpoint separation** — CRUD functions are framework-agnostic (no FastAPI imports), making them independently testable
- **UUIDs** over integers for all primary keys
- **Price in cents** (integer) to avoid floating-point errors
- **Atomic stock updates** via SQL-level UPDATE to prevent race conditions
- **RESTRICT vs CASCADE** on foreign keys based on data importance (sales history is protected, operational alerts cascade)

---

## Forecasting Engine

The forecasting pipeline runs automatically for each product:

```
1. Load sales history from DB (fills missing days with 0)
2. Detect factors: trend (R² threshold), seasonality (CV threshold), volatility
3. Select candidate models based on detected factors
4. Backtest all candidates — pick lowest MAE
5. Generate forecast + safety stock recommendation
6. Return report with full reasoning
```

### Models
| Model | Best For |
|---|---|
| Simple Moving Average | Stable, flat demand |
| Weighted Moving Average | Gradual trends (recent data weighted higher) |
| Linear Trend | Consistent growth or decline |
| Seasonal Decomposition | Weekly/periodic patterns |

---

## Getting Started

### Prerequisites
- Docker Desktop
- Git

### Run with Docker (recommended)

```bash
git clone https://github.com/FaroukRouatbi/predictive_inventory.git
cd predictive_inventory
```

Create a `.env` file at the project root (use `.env.example` as reference):

```bash
cp .env.example .env
# Fill in your values
```

Start everything:

```bash
docker-compose up --build
```

Run migrations and seed data:

```bash
docker-compose exec backend alembic upgrade head
docker-compose exec backend python scripts/seed_data.py
```

This generates 4 sample products with 120 days of synthetic sales history, each with a distinct demand pattern to demonstrate the forecasting engine's model selection logic:

| Product | Pattern | Model Selected |
|---|---|---|
| Wireless Headphones | Stable + slight trend | Weighted Moving Average |
| Winter Jacket | Weekly seasonal spike | Seasonal Decomposition |
| Protein Powder | High volume + noise | Weighted Moving Average |
| Air Purifier | Flat, slow mover | Weighted Moving Average |

Access:
- **Dashboard:** http://localhost
- **API docs:** http://localhost/docs

### Run Locally (without Docker)

**Backend:**
```bash
cd backend
pip install -r ../requirements.txt
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

---

## API Documentation

Interactive Swagger docs available at `/docs` when running.

### Key Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/auth/register` | Register a new user |
| POST | `/api/v1/auth/login` | Login with JWT |
| GET | `/api/v1/auth/google/login` | Google OAuth2 SSO |
| GET | `/api/v1/products/` | List all products |
| POST | `/api/v1/products/` | Create a product |
| GET | `/api/v1/inventory/` | List all inventory |
| POST | `/api/v1/sales/` | Record a sale |
| POST | `/api/v1/forecast/{product_id}` | Generate demand forecast |
| GET | `/api/v1/alerts/` | Get active reorder alerts |

---

## Testing

```bash
cd backend
pytest -v
```

**88 tests** across unit, integration, and forecasting layers:

```
unit/test_crud_product.py         — Product CRUD unit tests
unit/test_crud_inventory.py       — Inventory CRUD unit tests
unit/test_crud_user.py            — User CRUD unit tests
integration/test_products_api.py  — Product API integration + edge cases
integration/test_inventory_api.py — Inventory API integration + edge cases
integration/test_auth_api.py      — Auth API integration + edge cases
integration/test_sales_api.py     — Sales API integration + edge cases
forecasting/test_models.py        — Forecasting model accuracy tests
forecasting/test_engine.py        — Factor detector tests
```

---

## Project Structure

```
predictive_inventory/
├── backend/
│   ├── app/
│   │   ├── api/endpoints/     ← Route handlers
│   │   ├── core/              ← Security, caching, rate limiting
│   │   ├── crud/              ← Database operations
│   │   ├── models/            ← SQLAlchemy models
│   │   ├── schemas/           ← Pydantic validation schemas
│   │   └── services/
│   │       ├── forecasting/   ← Forecasting engine + models
│   │       └── alerts/        ← Reorder alert service
│   ├── tests/                 ← 88 tests
│   └── scripts/               ← Database seeder
├── frontend/
│   └── src/
│       ├── pages/             ← Inventory, Forecast, Alerts
│       ├── components/        ← Reusable UI components
│       └── api/               ← Axios API client
├── Dockerfile                 ← Backend container
├── Dockerfile.nginx           ← Frontend + Nginx container
├── docker-compose.yml         ← Full stack orchestration
└── nginx.conf                 ← Reverse proxy config
```

---

## Environment Variables

See `.env.example` for all required variables:

```
DATABASE_URL          — PostgreSQL connection string
SECRET_KEY            — JWT signing key
GOOGLE_CLIENT_ID      — Google OAuth2 client ID
GOOGLE_CLIENT_SECRET  — Google OAuth2 client secret
GOOGLE_REDIRECT_URI   — Google OAuth2 redirect URI
REDIS_URL             — Redis connection string
POSTGRES_USER         — PostgreSQL username (Docker)
POSTGRES_PASSWORD     — PostgreSQL password (Docker)
POSTGRES_DB           — PostgreSQL database name (Docker)
```

---

## License

MIT