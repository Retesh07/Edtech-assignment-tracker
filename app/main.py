"""Main FastAPI application factory."""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncEngine

from .database import engine
from .models import Base
from .routers import auth as auth_routes, assignments, submissions

app = FastAPI(title="EdTech Assignment Tracker", version="0.1.0")


@app.on_event("startup")
async def create_tables():
    async with engine.begin() as conn:  # type: AsyncEngine
        await conn.run_sync(Base.metadata.create_all)


app.include_router(auth_routes.router)
app.include_router(assignments.router)
app.include_router(submissions.router)

# Static front-end assets
app.mount("/static", StaticFiles(directory="static"), name="static")
# Serve uploaded files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.get("/")
async def root():
    return {"msg": "Hello, welcome to the EdTech Assignment Tracker API"}
