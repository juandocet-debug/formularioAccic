from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.infrastructure.http.admin_routes import router as admin_router
from app.infrastructure.http.auth_routes import router as auth_router
from app.infrastructure.http.public_routes import router as public_router
from app.infrastructure.persistence.database import initialize_database
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


@app.on_event("startup")
def startup() -> None:
    settings.validate_production_security()
    initialize_database()


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "environment": settings.environment}


app.include_router(public_router, prefix="/api/public", tags=["public"])
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(admin_router, prefix="/api/admin", tags=["admin"])
