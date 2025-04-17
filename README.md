# Chain Metrics Dashboard

A real-time blockchain metrics dashboard that tracks various on-chain metrics including:
- Hedera Hashgraph Transaction Count
- USDC Minted on Hedera
- Crypto Greed/Fear Index

## Tech Stack
- Backend: Python/FastAPI
- Frontend: TypeScript/React
- Database: PostgreSQL
- Containerization: Docker

## Project Structure
```
.
├── backend/           # Python FastAPI backend service
├── frontend/         # React frontend
├── database/         # Database migrations and schemas
└── docker/           # Docker configuration
```

## Setup Instructions

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker and Docker Compose
- PostgreSQL 15+

### Development Setup
1. Clone the repository
2. Run `docker compose up --build` to start all services
3. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8080
   - API Documentation: http://localhost:8080/docs

## API Endpoints
- `/api/metrics/hedera/tx-count` - Hedera transaction count
- `/api/metrics/hedera/usdc-minted` - USDC minted on Hedera
- `/api/metrics/crypto/greed-fear` - Crypto Greed/Fear Index

## License
MIT
