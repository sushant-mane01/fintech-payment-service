# Fintech Payment Service

Production-ready microservice for handling digital wallet transactions, ledger auditing, and merchant payment processing.

## Architecture
- **Framework**: FastAPI (Python 3.10+)
- **ORM / Database**: SQLAlchemy (SQLite for dev / PostgreSQL for production)
- **Data Validation**: Pydantic v2
- **Testing**: pytest

## Endpoints
- `GET /health` - Service health status
- `POST /api/v1/wallets` - Create / manage customer wallet
- `POST /api/v1/charges` - Initiate a payment charge
