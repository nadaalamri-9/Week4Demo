from fastapi import FastAPI
from database import engine, Base
import models  # register models with Base
from routes import users_router, posts_router, profiles_router

app = FastAPI(
    title="ORM Fundamentals with SQLAlchemy",
    description="A beginner-friendly FastAPI project setup tutorial.",
    version="1.0.0",
)

@app.get("/")
def root():
    return {
        "message": "ORM Fundamentals with SQLAlchemy"
    }

@app.get("/health")
def health_check():
    return {
        "status": "ok"
    }

@app.on_event("startup")
def on_startup():
    # ensure tables exist when the app starts
    Base.metadata.create_all(bind=engine)
    # register API routers
    app.include_router(users_router)
    app.include_router(posts_router)
    app.include_router(profiles_router)
