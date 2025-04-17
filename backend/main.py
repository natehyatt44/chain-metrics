from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os
import asyncio
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import httpx
from typing import List
from pydantic import BaseModel

# Load environment variables
load_dotenv()

# Database setup
DATABASE_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database models
class Metric(Base):
    __tablename__ = "metrics"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    value = Column(Float)
    source = Column(String)

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic models
class MetricResponse(BaseModel):
    timestamp: datetime
    value: float
    source: str

    class Config:
        from_attributes = True

# API clients
class HederaClient:
    def __init__(self):
        self.base_url = "https://mainnet-public.mirrornode.hedera.com/api/v1"

    async def get_transaction_count(self) -> int:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/transactions")
            data = response.json()
            return len(data.get("transactions", []))

    async def get_usdc_balance(self) -> float:
        usdc_token_id = "0.0.456858"
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/tokens/{usdc_token_id}")
            data = response.json()
            return float(data.get("total_supply", 0))

class CryptoClient:
    def __init__(self):
        self.base_url = "https://api.alternative.me/fng/"

    async def get_fear_greed_index(self) -> int:
        async with httpx.AsyncClient() as client:
            response = await client.get(self.base_url)
            data = response.json()
            if not data.get("data"):
                raise HTTPException(status_code=500, detail="No data available")
            return int(data["data"][0]["value"])

# Initialize FastAPI app
app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize clients
hedera_client = HederaClient()
crypto_client = CryptoClient()

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def collect_metrics():
    """Background task to collect metrics every 5 minutes"""
    while True:
        try:
            # Collect Hedera transaction count
            count = await hedera_client.get_transaction_count()
            db = SessionLocal()
            metric = Metric(value=float(count), source="hedera_tx_count")
            db.add(metric)
            db.commit()
            print(f"Collected Hedera transaction count: {count}")

            # Collect USDC balance
            balance = await hedera_client.get_usdc_balance()
            metric = Metric(value=balance, source="hedera_usdc")
            db.add(metric)
            db.commit()
            print(f"Collected USDC balance: {balance}")

            # Collect Greed/Fear Index
            index = await crypto_client.get_fear_greed_index()
            metric = Metric(value=float(index), source="crypto_greed_fear")
            db.add(metric)
            db.commit()
            print(f"Collected Greed/Fear Index: {index}")

        except Exception as e:
            print(f"Error collecting metrics: {str(e)}")

        # Wait for 5 minutes before next collection
        await asyncio.sleep(300)  # 300 seconds = 5 minutes

@app.on_event("startup")
async def startup_event():
    """Start the background task when the application starts"""
    asyncio.create_task(collect_metrics())

# API endpoints
@app.get("/api/metrics/hedera/tx-count", response_model=List[MetricResponse])
async def get_hedera_tx_count():
    try:
        db = SessionLocal()
        metrics = db.query(Metric).filter(Metric.source == "hedera_tx_count").order_by(Metric.timestamp.desc()).limit(100).all()
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/metrics/hedera/usdc-minted", response_model=List[MetricResponse])
async def get_hedera_usdc():
    try:
        db = SessionLocal()
        metrics = db.query(Metric).filter(Metric.source == "hedera_usdc").order_by(Metric.timestamp.desc()).limit(100).all()
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/metrics/crypto/greed-fear", response_model=List[MetricResponse])
async def get_greed_fear_index():
    try:
        db = SessionLocal()
        metrics = db.query(Metric).filter(Metric.source == "crypto_greed_fear").order_by(Metric.timestamp.desc()).limit(100).all()
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/metrics/debug/raw")
async def get_raw_metrics():
    """Debug endpoint to view raw database contents"""
    try:
        db = SessionLocal()
        metrics = db.query(Metric).order_by(Metric.timestamp.desc()).limit(10).all()
        return [
            {
                "id": m.id,
                "timestamp": m.timestamp.isoformat(),
                "value": m.value,
                "source": m.source
            }
            for m in metrics
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080) 