from fastapi import FastAPI, Request, status, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import check_db_health
from app.core.logging import setup_logging
from app.api.v1.router import api_router

# Initialize structured logging
setup_logging()

app = FastAPI(
    title="Oil Spill Detection & AIS Attribution Platform API",
    description="Spatio-temporal oil spill forensics API connecting satellite imagery, particle drift modeling, and AIS vessel tracks.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration per PRD §34.6
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from starlette.exceptions import HTTPException as StarletteHTTPException

# Exception handlers for standard error envelope per PRD §36
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Override default HTTP exceptions to use standard JSON error envelope per PRD §36."""
    code_map = {
        status.HTTP_401_UNAUTHORIZED: "UNAUTHORIZED",
        status.HTTP_403_FORBIDDEN: "FORBIDDEN",
        status.HTTP_404_NOT_FOUND: "NOT_FOUND",
        status.HTTP_409_CONFLICT: "CONFLICT",
        status.HTTP_422_UNPROCESSABLE_ENTITY: "VALIDATION_ERROR",
        status.HTTP_500_INTERNAL_SERVER_ERROR: "INTERNAL_ERROR",
    }
    code = code_map.get(exc.status_code, "HTTP_ERROR")
    message = str(exc.detail) if exc.detail else "An error occurred"
    if exc.status_code == status.HTTP_401_UNAUTHORIZED and message == "Not authenticated":
        message = "Could not validate credentials"
        code = "UNAUTHORIZED"

    return JSONResponse(
        status_code=exc.status_code,
        headers=exc.headers,
        content={
            "error": {
                "code": code,
                "message": message
            }
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Override default validation errors to use the standard JSON envelope."""
    errors = exc.errors()
    message = "; ".join([f"{'.'.join(str(p) for p in err['loc'])}: {err['msg']}" for err in errors])
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": message
            }
        }
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Override unhandled exceptions to use the standard JSON envelope."""
    # Log the stacktrace internally
    import traceback
    traceback.print_exc()
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred on the server."
            }
        }
    )

# Include sub-routers
app.include_router(api_router, prefix="/api/v1")

# Health check endpoints per PRD §40
@app.get("/health", tags=["Health Monitoring"])
async def liveness_check():
    """Simple check to verify the API server is alive."""
    return {"status": "ok"}

@app.get("/health/ready", tags=["Health Monitoring"])
async def readiness_check():
    """Database connectivity check."""
    db_healthy = await check_db_health()
    if db_healthy:
        return {
            "status": "ready",
            "database": "connected"
        }
    else:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unavailable",
                "database": "disconnected"
            }
        )
