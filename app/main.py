import logging
import os
import time
from fastapi import FastAPI, HTTPException
from redis import Redis
import psycopg2

# Configure Structured Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("devops-app")

app = FastAPI(title="Production DevOps API", version="1.0.0")

# Fetch environment variables
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
DATABASE_URL = os.getenv("DATABASE_URL")

@app.get("/")
def read_root():
    logger.info("Root endpoint hit")
    return {"status": "running", "environment": os.getenv("ENV", "production")}

@app.get("/health")
def health_check():
    health_status = {"status": "healthy", "checks": {}}
    
    # 1. Check Redis
    try:
        r = Redis(host=REDIS_HOST, port=6379, socket_connect_timeout=2)
        r.ping()
        health_status["checks"]["redis"] = "UP"
    except Exception as e:
        logger.error(f"Healthcheck failed for Redis: {str(e)}")
        health_status["checks"]["redis"] = "DOWN"
        health_status["status"] = "unhealthy"

    # 2. Check PostgreSQL
    try:
        conn = psycopg2.connect(DATABASE_URL, connect_timeout=2)
        conn.close()
        health_status["checks"]["database"] = "UP"
    except Exception as e:
        logger.error(f"Healthcheck failed for Database: {str(e)}")
        health_status["checks"]["database"] = "DOWN"
        health_status["status"] = "unhealthy"

    if health_status["status"] == "unhealthy":
        raise HTTPException(status_code=503, detail=health_status)
        
    return health_status