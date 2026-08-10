from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routes.auth import router as auth_router
from app.routes.roles import router as roles_router
from app.routes.users import router as users_router
from app.routes.sales import router as sales_router
from app.routes.presale import router as presale_router
from app.routes.resource_manager import router as resource_manager_router
from app.routes.account_director import router as account_director_router
from app.routes.executive import router as executive_router
from app.routes.alliance import router as alliance_router
from app.routes.rfp import router as rfp_router
from app.routes.blended_rate import router as blended_rate_router
from app.routes.resource_match import router as resource_match_router
from app.core.database import (
    Base,
    engine,
    normalize_currency_to_usd,
)


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
)

@app.on_event("startup")
def create_tables() -> None:
    Base.metadata.create_all(bind=engine)
    normalize_currency_to_usd()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router)
app.include_router(roles_router)
app.include_router(users_router)
app.include_router(sales_router)
app.include_router(presale_router)
app.include_router(resource_manager_router)
app.include_router(account_director_router)
app.include_router(executive_router)
app.include_router(alliance_router)
app.include_router(rfp_router)
app.include_router(blended_rate_router)
app.include_router(resource_match_router)


@app.get("/")
def root():
    return {
        "message": "CRM for IT Services API is running",
        "status": "success",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
    }
