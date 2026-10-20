import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Tests load .env.test first; load_dotenv never overrides a variable already set.
load_dotenv()

from app.routers import (  # noqa: E402
    accounting,
    customers,
    dashboard,
    invoices,
    me,
    orders,
    products,
    purchasing,
    stock,
)

app = FastAPI(title="Siam Bean Mini ERP")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.environ.get("FRONTEND_ORIGIN", "http://localhost:5173")],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


# Every module's router is registered here once, so Parts 1 and 2 never edit
# this file. Part 3: me, accounting. Part 1: products, customers, stock,
# dashboard, purchasing. Part 2: orders, invoices.
for module in (me, products, customers, stock, dashboard, purchasing, orders, invoices, accounting):
    app.include_router(module.router)
