import time

from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from .database import Base, engine
from .admin import setup_admin
from .routers import cities, shops, parts, search, feedback

app = FastAPI(title="Zapchastop API")


def wait_for_db(retries: int = 30, delay: float = 1.0):
    for _ in range(retries):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return
        except OperationalError:
            time.sleep(delay)
    raise RuntimeError("Database is not reachable")


@app.on_event("startup")
def on_startup():
    wait_for_db()
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
        conn.commit()
    Base.metadata.create_all(bind=engine)


app.include_router(cities.router)
app.include_router(shops.router)
app.include_router(parts.router)
app.include_router(search.router)
app.include_router(feedback.router)

setup_admin(app, engine)


@app.get("/health")
def health():
    return {"status": "ok"}
