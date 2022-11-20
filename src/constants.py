import functools
import hashlib
import os

EXCHANGE_NAME = os.getenv("RACCOON_EXCHANGE_NAME", "binance")
EXCHANGE_API_KEY = os.getenv("RACCOON_EXCHANGE_API_KEY", "placeholder")
EXCHANGE_API_SECRET = os.getenv("RACCOON_EXCHANGE_API_SECRET", "placeholder")
EXCHANGE_TESTNET = bool(os.getenv("RACCOON_EXCHANGE_TESTNET", False))

REDIS_HOST = os.getenv("RACCOON_REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("RACCOON_REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("RACCOON_REDIS_DB", 0))

WEBSOCKET_LOG_LEVEL = os.getenv("RACCOON_WEBSOCKET_LOG_LEVEL", "INFO")
WEBSOCKET_STREAM_LIFETIME_SECONDS = int(
    os.getenv("RACCOON_WEBSOCKET_STREAM_LIFETIME_SECONDS", 86800)
)


@functools.cache
def get_redis_key_prefix():
    if EXCHANGE_TESTNET:
        return "-".join([EXCHANGE_NAME, "sandbox"])

    return EXCHANGE_NAME


@functools.cache
def get_redis_private_key_prefix():
    hashed_key = hashlib.md5(EXCHANGE_API_KEY.encode()).hexdigest()

    if EXCHANGE_TESTNET:
        return "-".join([EXCHANGE_NAME, "sandbox", hashed_key[:6]])

    return "-".join([EXCHANGE_NAME, hashed_key[:6]])
