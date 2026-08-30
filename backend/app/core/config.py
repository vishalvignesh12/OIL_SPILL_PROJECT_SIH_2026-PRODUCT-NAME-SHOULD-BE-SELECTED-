import os
from typing import List
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()

class Settings(BaseModel):
    PROJECT_NAME: str = Field(default_factory=lambda: os.getenv(
        "PROJECT_NAME", "Oil Spill Detection & AIS Attribution Platform API"
    ))
    APP_NAME: str = Field(default_factory=lambda: os.getenv(
        "APP_NAME", "Oil Spill Detection & AIS Attribution Platform API"
    ))
    VERSION: str = Field(default_factory=lambda: os.getenv(
        "VERSION", "1.0.0"
    ))
    API_V1_STR: str = Field(default_factory=lambda: os.getenv(
        "API_V1_STR", "/api/v1"
    ))
    
    DATABASE_URL: str = Field(default_factory=lambda: os.getenv(
        "DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/oil_spill"
    ))
    JWT_SECRET: str = Field(default_factory=lambda: os.getenv(
        "JWT_SECRET", "supersecretjwtkeyforoilspilldetectionplatform2026sih"
    ))
    JWT_ALGORITHM: str = Field(default_factory=lambda: os.getenv(
        "JWT_ALGORITHM", "HS256"
    ))
    JWT_EXPIRATION_MINUTES: int = Field(default_factory=lambda: int(os.getenv(
        "JWT_EXPIRATION_MINUTES", "1440"
    )))
    
    # Third-party integrations
    GFW_API_KEY: str = Field(default_factory=lambda: os.getenv(
        "GFW_API_KEY", "mock_gfw_api_key"
    ))
    CMEMS_USERNAME: str = Field(default_factory=lambda: os.getenv(
        "CMEMS_USERNAME", "mock_cmems_user"
    ))
    CMEMS_PASSWORD: str = Field(default_factory=lambda: os.getenv(
        "CMEMS_PASSWORD", "mock_cmems_pass"
    ))
    ERA5_API_KEY: str = Field(default_factory=lambda: os.getenv(
        "ERA5_API_KEY", "mock_era5_key"
    ))

    # ML Inference configuration
    ML_PROVIDER: str = Field(default_factory=lambda: os.getenv(
        "ML_PROVIDER", "fixture"
    ))
    ML_SERVICE_URL: str = Field(default_factory=lambda: os.getenv(
        "ML_SERVICE_URL", "http://localhost:8001/predict"
    ))
    ML_INFERENCE_TIMEOUT_SECONDS: int = Field(default_factory=lambda: int(os.getenv(
        "ML_INFERENCE_TIMEOUT_SECONDS", "30"
    )))
    ML_MODEL_NAME: str = Field(default_factory=lambda: os.getenv(
        "ML_MODEL_NAME", "oilspill-detector"
    ))
    ML_MODEL_VERSION: str = Field(default_factory=lambda: os.getenv(
        "ML_MODEL_VERSION", "v1"
    ))
    
    # CORS (PRD §34.6: explicit allowed origins, never "*" in production)
    CORS_ORIGINS: List[str] = Field(default_factory=lambda: [
        origin.strip() for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",") if origin.strip()
    ])

settings = Settings()
