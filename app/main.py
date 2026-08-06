from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routes.auth import router as auth_router
from app.routes.roles import router as roles_router
from app.routes.users import router as users_router


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
)


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