from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import engine
from app.models.base import Base
# Import models to ensure they are registered with Base
from app.models import user, ticket, analytics
from app.api import users, tickets, auth
from app.api import analytics as analytics_api

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    with open("routes.txt", "w") as f:
        for route in app.routes:
            f.write(f"ROUTE: {route.path} {route.name}\n")
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, tags=["login"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(tickets.router, prefix="/tickets", tags=["tickets"])
app.include_router(analytics_api.router, prefix="/admin", tags=["analytics"])

@app.get("/")
async def root():
    return {"message": "Welcome to Doxa Customer Support System"}
