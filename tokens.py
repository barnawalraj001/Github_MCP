# tokens.py

_tokens = {}

def save_token(user_id: str, access_token: str):
    _tokens[user_id] = access_token

def get_token(user_id: str):
    return _tokens.get(user_id)

def all_tokens():
    return _tokens
