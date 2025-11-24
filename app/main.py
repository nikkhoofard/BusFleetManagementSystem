from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.database import Database
from app.api.v1.router import api_router
from app.tasks.reservation_cleanup import start_reservation_cleanup_task
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await Database.create_pool()
    start_reservation_cleanup_task()
    yield
    # Shutdown
    await Database.close_pool()


app = FastAPI(
    title=settings.app_name,
    description="Bus Fleet Management System API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"message": "Bus Fleet Management System API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

