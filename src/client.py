import functools
import json

import ccxt.pro
import redis

from constants import REDIS_DB, REDIS_HOST, REDIS_PORT


@functools.cache
def get_websocket_client(
    exchange: str, config: str, sandbox: bool = False
) -> ccxt.pro.Exchange:
    websocket_cls = getattr(ccxt.pro, exchange)

    client: ccxt.pro.Exchange = websocket_cls(json.loads(config))
    client.set_sandbox_mode(sandbox)

    return client


@functools.cache
def get_redis_client() -> redis.Redis:
    return redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
