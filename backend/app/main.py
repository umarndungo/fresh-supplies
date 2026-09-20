from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.application.ml_service import MLServiceError, load_market_prices, load_model_bundle
from app.core.config import settings
from app.core.exceptions import AppError
from app.core.logging import RequestLoggingMiddleware, configure_logging

configure_logging()
logger = logging.getLogger("freshroute.startup")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Observability: log whether the ML artifacts are present at startup so an
    # operator immediately knows if /ml inference will work. Missing artifacts
    # are a warning (config issue), not a reason to refuse to boot the API.
    try:
        load_model_bundle()
        load_market_prices()
        logger.info("ML artifacts loaded", extra={"kv": {"model": "food_model_inference.joblib"}})
    except Exception as exc:  # MLServiceError / FileNotFoundError
        logger.warning("ML artifacts NOT loaded: %s", exc)
    yield


app = FastAPI(title=settings.APP_NAME, version="0.1.0", lifespan=lifespan)

app.add_middleware(RequestLoggingMiddleware)
# Only load-bearing for local dev (frontend/backend on different ports) and
# any direct cross-origin caller (e.g. Swagger UI hosted elsewhere). The
# deployed site no longer needs this: Caddy now serves frontend and backend
# under one origin (see Caddyfile), so the browser's own calls are
# same-origin and never hit this middleware at all.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    errors = [{"field": exc.field, "message": exc.message}] if exc.field else None
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.message, "errors": errors, "statusCode": exc.status_code},
    )


@app.exception_handler(MLServiceError)
async def ml_error_handler(request: Request, exc: MLServiceError) -> JSONResponse:
    # Unknown crops / missing model artifacts -> clean 422 instead of a raw 500.
    return JSONResponse(
        status_code=422,
        content={"message": str(exc), "errors": None, "statusCode": 422},
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    errors = [
        {"field": ".".join(str(part) for part in err["loc"][1:]), "message": err["msg"]} for err in exc.errors()
    ]
    return JSONResponse(
        status_code=422,
        content={"message": "Validation failed.", "errors": errors, "statusCode": 422},
    )


_error_logger = logging.getLogger("freshroute.errors")


@app.exception_handler(Exception)
async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    # Anything that reaches here is a bug or an unmapped failure (e.g. an
    # IntegrityError a service forgot to catch) — without this, FastAPI's
    # default response skips the {message, errors, statusCode} envelope
    # every client (web, mobile) actually parses, and can leak a raw
    # traceback if debug mode is ever on. Full detail still goes to the
    # server log; the client only ever sees a generic, safe message.
    _error_logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"message": "Something went wrong. Please try again.", "errors": None, "statusCode": 500},
    )


app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}

