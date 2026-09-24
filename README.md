# Fintech Payment Service

Production-ready microservice for handling digital wallet transactions, ledger auditing, and merchant payment processing deployed on Vercel.

## Features & Architecture
- **Interactive UI**: Clean, dark-mode fintech management dashboard served directly at `/`
- **Framework**: FastAPI (Python 3.10+) running serverless via `@vercel/python`
- **ORM / Database**: SQLAlchemy (SQLite for dev / PostgreSQL for production)
- **Data Validation**: Pydantic v2
- **Testing**: Complete pytest & TestClient suite

## Endpoints
- `GET /` - Interactive Payment Service Web UI Dashboard
- `GET /health` - Service health & Vercel deployment status
- `POST /api/v1/wallets` - Create / issue a customer digital wallet
- `GET /api/v1/wallets/{wallet_id}` - Retrieve wallet details and current balance
- `POST /api/v1/charges` - Initiate an authorized payment charge against a wallet
- `GET /docs` - Interactive Swagger OpenAPI documentation

## Running Locally
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
Navigate to `http://localhost:8000` to interact with the UI.

## Testing
```bash
pytest tests/
```
