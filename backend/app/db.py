import os
from functools import lru_cache

from supabase import Client, create_client


@lru_cache
def get_db() -> Client:
    """Supabase client using the secret key. Only the backend holds this key."""
    return create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SECRET_KEY"])
