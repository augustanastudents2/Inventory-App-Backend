"""
 * ASA Inventory App - FastAPI Backend
 * Main application entry point
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Dict, Any

from app.routers import products, settings_router, auth, users
from app.core.config import settings

app = FastAPI(
    title="ASA Inventory App API",
    description="Backend API for the ASA Inventory Management System",
    version="1.0.0"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(products.router, prefix="/api/products", tags=["Products"])
app.include_router(settings_router.router, prefix="/api/settings", tags=["Settings"])


@app.get("/")
async def root() -> Dict[str, str]:
    return {
        "message": "ASA Inventory App API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/api/health")
async def health_check() -> Dict[str, str]:
    return {"status": "healthy"}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "message": str(exc)}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
