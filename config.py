import os
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

GITHUB_API_BASE_URL = "https://api.github.com"
MAX_LIMIT = 30

def safe_limit(limit: int) -> int:
    try:
        val = int(limit)
        return min(val, MAX_LIMIT)
    except Exception:
        return 10
