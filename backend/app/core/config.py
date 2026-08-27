import os
from typing import List
from pydantic import BaseModel, Field

class Settings(BaseModel):
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
    
    # CORS (PRD §34.6: explicit allowed origins, never "*" in production)
    CORS_ORIGINS: List[str] = Field(default_factory=lambda: [
        origin.strip() for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",") if origin.strip()
    ])

settings = Settings()
