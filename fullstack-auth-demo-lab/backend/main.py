"""
The FastAPI application. Run it with:

    uvicorn main:app --reload

This file is deliberately thin: it creates the app, sets up CORS, and
wires in the routers. The actual endpoints live in the routes/ folder,
one file per area of the API:

    routes/auth.py   -- POST /auth/register, POST /auth/login   (public)
    routes/users.py  -- GET /users/me, /users/profile           (any logged-in user)
    routes/admin.py  -- GET /admin/users, /admin/stats          (admins only)

Splitting routes into modules like this is how real FastAPI projects
are organized -- main.py would get unreadable fast with everything in
one file. Interactive docs at http://localhost:8000/docs show all of
them grouped by tag.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine
from routes import admin, auth, users

# Creates the tables defined in models.py if they don't exist yet.
# Fine for a demo; real projects use a migration tool like Alembic so
# schema changes are versioned instead of just bolted on at startup.
Base.metadata.create_all(bind=engine)

app = FastAPI(title="JWT + RBAC demo")

# The React dev server runs on a different port (5173) than this API
# (8000). Browsers block cross-origin requests by default, so we have
# to explicitly allow our frontend's origin. Without this, every fetch
# from React would fail with a CORS error in the console.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Each router brings its own prefix ("/auth", "/users", "/admin"), so
# this is all the wiring main.py needs.
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(admin.router)
