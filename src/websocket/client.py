import functools

import ccxt.pro
import redis

from constants import (
    EXCHANGE_API_KEY,
    EXCHANGE_API_SECRET,
    EXCHANGE_NAME,
    EXCHANGE_SANDBOX,
    REDIS_DB,
    REDIS_HOST,
    REDIS_PORT,
)


@functools.cache
def get_websocket_client() -> ccxt.pro.Exchange:
    if EXCHANGE_NAME not in ccxt.pro.exchanges:
        raise ValueError(f"invalid exchange name {EXCHANGE_NAME}")

    websocket_cls = getattr(ccxt.pro, EXCHANGE_NAME)

    config = {}

    if EXCHANGE_API_KEY is not None:
        config.update({"apiKey": EXCHANGE_API_KEY})

    if EXCHANGE_API_SECRET is not None:
        config.update({"secret": EXCHANGE_API_SECRET})

    client: ccxt.pro.Exchange = websocket_cls(config)
    client.set_sandbox_mode(EXCHANGE_SANDBOX)

    return client


@functools.cache
def get_redis_client() -> redis.Redis:
    return redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
