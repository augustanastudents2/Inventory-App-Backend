"""
 * Application Configuration Settings
 *
 * This file contains the application configuration class that loads
 * environment variables and provides default settings for the API.
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """
    Application settings class - Loads configuration from environment variables
    """
    
    # Supabase Configuration
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_SERVICE_KEY: str
    
    # Database Tables
    PRODUCTS_TABLE: str = "products"
    CATEGORIES_TABLE: str = "categories"
    TAGS_TABLE: str = "tags"
    STORAGE_LOCATIONS_TABLE: str = "storage_locations"
    VENDORS_TABLE: str = "vendors"
    USERS_TABLE: str = "users"
    STOCK_HISTORY_TABLE: str = "stock_history"
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173,http://127.0.0.1:5173,https://inventory-app-frontend-lilac.vercel.app"
    
    def get_cors_origins(self) -> List[str]:
        if isinstance(self.CORS_ORIGINS, str):
            return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
        return self.CORS_ORIGINS if isinstance(self.CORS_ORIGINS, list) else []
    
    # JWT Settings
    JWT_SECRET: str = ""
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION: int = 3600  # 1 hour
    
    # Application
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
