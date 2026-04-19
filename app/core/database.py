"""
 * Supabase Database Client Setup
"""

from supabase import create_client, Client
from app.core.config import settings


class SupabaseClient:
    _instance: Client = None
    
    @classmethod
    def get_client(cls) -> Client:
        if cls._instance is None:
            cls._instance = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_KEY
            )
        return cls._instance
    
    @classmethod
    def get_service_client(cls) -> Client:
        return create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_KEY
        )


def get_db() -> Client:
    return SupabaseClient.get_client()


def get_service_db() -> Client:
    return SupabaseClient.get_service_client()
