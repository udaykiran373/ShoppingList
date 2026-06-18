"""
Shopping List Management API - Main Application Entry Point.

Initializes FastAPI, registers routers, lifecycle events,
and global exception handlers.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.database.mongodb import MongoDB
from app.routers import shopping_lists, shopping_items
from app.utils.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown."""
    await MongoDB.connect()
    yield
    await MongoDB.disconnect()


app = FastAPI(
    title="Shopping List Management API",
    description=(
        "A RESTful API to manage multiple shopping lists and their items. "
        "Built with FastAPI and MongoDB (Motor async driver)."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(shopping_lists.router)
app.include_router(shopping_items.router)


# ── Global Exception Handlers ─────────────────────────────────────────────────

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Return a clean 422 response for Pydantic validation failures."""
    errors = exc.errors()
    logger.error(f"Validation error on {request.url}: {errors}")
    first_msg = errors[0].get("msg", "Validation error") if errors else "Validation error"
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"message": first_msg, "error_code": "VALIDATION_ERROR", "details": errors},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Catch-all handler for unexpected server errors."""
    logger.error(f"Unexpected error on {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"message": "An unexpected error occurred", "error_code": "INTERNAL_SERVER_ERROR"},
    )


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint.

    Returns:
        API status.
    """
    return {"status": "ok", "service": "Shopping List API"}
