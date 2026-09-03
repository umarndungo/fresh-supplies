"""Structured logging + request observability.

Configures Python's stdlib logging with a structured key=value formatter so
each log line is greppable / indexable (e.g. by Datadog or Loki agent), and
exposes an ASGI middleware that records one structured line per HTTP request
(method, path, status, duration_ms, client, user-agent).

No third-party dependency: uses only ``logging`` (stdlib). Swap the formatter
or add a Sentry hook in ``configure_logging`` if desired.
"""

import logging
import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

LOG_LEVEL = logging.INFO


def _escape(v: object) -> str:
    s = str(v)
    if any(ch in s for ch in ' "'):
        return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return s


class KeyValueFormatter(logging.Formatter):
    """Formats records as: level  logger  key=value ...  message."""

    def format(self, record: logging.LogRecord) -> str:
        base = f"{record.levelname:<7} {record.name}: "
        kv = record.__dict__.get("kv", {})
        parts = [base]
        for k in sorted(kv):
            parts.append(f"{k}={_escape(kv[k])}")
        parts.append(_escape(record.getMessage()))
        return " ".join(parts)


def configure_logging(level: int = LOG_LEVEL) -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(KeyValueFormatter())
    root = logging.getLogger()
    root.setLevel(level)
    # Avoid stacking duplicate handlers if configure_logging is re-run (tests).
    root.handlers = [h for h in root.handlers if isinstance(h, logging.StreamHandler)]
    root.addHandler(handler)


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "-"


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Logs a structured line per request with status + latency."""

    def __init__(self, app, logger: logging.Logger | None = None):
        super().__init__(app)
        self._logger = logger or logging.getLogger("freshroute.http")

    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            self._logger.error(
                "unhandled server error",
                extra={"kv": {"method": request.method, "path": request.url.path,
                              "client": _client_ip(request)}},
            )
            raise
        duration_ms = (time.perf_counter() - start) * 1000.0
        self._logger.info(
            f"{request.method} {request.url.path} -> {response.status_code}",
            extra={"kv": {
                "method": request.method,
                "path": request.url.path,
                "status": response.status_code,
                "duration_ms": f"{duration_ms:.1f}",
                "client": _client_ip(request),
            }},
        )
        return response
