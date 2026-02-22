import redis
from config import REDIS_URL

# Connect to Redis with string decoding enabled
redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

def save_token(user_id: str, access_token: str):
    """Save GitHub access token for a user in Redis."""
    redis_client.set(f"github_token:{user_id}", access_token)

def get_token(user_id: str) -> str:
    """Retrieve GitHub access token for a user from Redis."""
    token = redis_client.get(f"github_token:{user_id}")
    return token
