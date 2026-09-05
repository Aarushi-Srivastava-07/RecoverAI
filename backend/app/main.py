from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.api.recovery import router as recovery_router
from app.core.config import get_settings
from app.db.session import Base, engine
import app.db.models  # noqa: F401 - registers SQLAlchemy tables

settings = get_settings()
app = FastAPI(title=settings.app_name, version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=[],
)
app.include_router(health_router, prefix="/api")
app.include_router(recovery_router, prefix="/api")


@app.on_event("startup")
def initialise_database() -> None:
    Base.metadata.create_all(bind=engine)
