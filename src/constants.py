import os

REDIS_HOST = os.getenv("RACCOON_REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("RACCOON_REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("RACCOON_REDIS_DB", 0))

EXCHANGE_NAME = os.getenv("RACCOON_WEBSOCKET_EXCHANGE", "binance")
EXCHANGE_API_KEY = os.getenv("RACCOON_WEBSOCKET_EXCHANGE_API_KEY", "placeholder")
EXCHANGE_API_SECRET = os.getenv("RACCOON_WEBSOCKET_EXCHANGE_API_SECRET", "placeholder")
EXCHANGE_SANDBOX = bool(os.getenv("RACCOON_WEBSOCKET_EXCHANGE_SANDBOX", False))

WEBSOCKET_LOG_LEVEL = os.getenv("RACCOON_WEBSOCKET_LOG_LEVEL", "INFO")
WEBSOCKET_STREAM_LIFETIME_SECONDS = int(
    os.getenv("RACCOON_WEBSOCKET_STREAM_LIFETIME_SECONDS", 86800)
)
WEBSOCKET_KLINE_DUPLICATE_POLICY = os.getenv(
    "RACCOON_WEBSOCKET_KLINE_DUPLICATE_POLICY", "last"
)
WEBSOCKET_KLINE_RETENTION_SECONDS = os.getenv(
    "RACCOON_WEBSOCKET_KLINE_RETENTION_SECONDS", 14400000
)


def get_connection_name():
    return "-".join([EXCHANGE_NAME, "sandbox"]) if EXCHANGE_SANDBOX else EXCHANGE_NAME


def get_connection_unique_name():
    connection_name = (
        "-".join([EXCHANGE_NAME, "sandbox"]) if EXCHANGE_SANDBOX else EXCHANGE_NAME
    )

    return "-".join([connection_name, EXCHANGE_API_KEY[:6]])
