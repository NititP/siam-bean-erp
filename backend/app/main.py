import os

import httpx
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Tests load .env.test first; load_dotenv never overrides a variable already set.
load_dotenv()

from app.auth import get_current_user  # noqa: E402
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
    users,
)

app = FastAPI(title="Siam Bean Mini ERP")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.environ.get("FRONTEND_ORIGIN", "http://localhost:5173")],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(httpx.TransportError)
def supabase_out_of_reach(request: Request, exc: httpx.TransportError) -> JSONResponse:
    return JSONResponse(
        status_code=503,
        content={"detail": "Cannot reach the database right now. Try again in a minute."},
    )


@app.get("/health")
def health():
    return {"status": "ok"}


# Every module's router is registered here once, so Parts 1 and 2 never edit
# this file. Part 3: me, accounting, users. Part 1: products, customers, stock,
# dashboard, purchasing. Part 2: orders, invoices.
# Every endpoint in them needs a login; owners add require_roles(...) where a
# role limit applies.
for module in (me, products, customers, stock, dashboard, purchasing, orders, invoices, accounting, users):
    app.include_router(module.router, dependencies=[Depends(get_current_user)])
