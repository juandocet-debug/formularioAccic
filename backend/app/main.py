from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app.infrastructure.http.admin_routes import router as admin_router
from app.infrastructure.http.auth_routes import router as auth_router
from app.infrastructure.http.public_routes import router as public_router
from app.infrastructure.persistence.database import initialize_database
from app.infrastructure.postgresql.database import close_connection_pool
from app.infrastructure.settings import get_settings


settings = get_settings()

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
    expose_headers=["Content-Disposition"],
)


@app.middleware("http")
async def apply_security_headers(request: Request, call_next) -> Response:
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "camera=(), geolocation=(), microphone=()"

    if request.url.path == "/api/public/groups":
        response.headers["Cache-Control"] = "public, max-age=8, stale-while-revalidate=20"
    elif request.url.path.startswith(("/api/admin", "/api/auth")):
        response.headers["Cache-Control"] = "no-store"
    return response


@app.on_event("startup")
def startup() -> None:
    settings.validate_production_security()
    initialize_database()


@app.on_event("shutdown")
def shutdown() -> None:
    close_connection_pool()


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "environment": settings.environment}


app.include_router(public_router, prefix="/api/public", tags=["public"])
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(admin_router, prefix="/api/admin", tags=["admin"])
