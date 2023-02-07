import asyncio
import json
import time
import typing

from client import get_ccxt_pro_client
from settings import settings
from websocket.handler.base import WebsocketHandler


class WebsocketTickerHandler(WebsocketHandler):

    handler_type = "ticker"
    subscription_key = "ticker-subs"

    def process_msg_ticker(self, symbol: str, msg: dict):
        db_key = self.get_db_key(self.handler_type)
        self.redis.hset(db_key, symbol, json.dumps(msg))

    async def manage_streams(self):
        subscription_key = self.get_db_key(self.subscription_key)

        while True:
            self.manage_subscriptions(subscription_key)
            subscription = self.get_subscriptions()

            for sub_key, running in subscription.items():
                if not running:
                    self.update_subscription(sub_key=sub_key, status=True)
                    self.dispatch_task(lambda: self.handle_ticker_stream(sub_key))

            await asyncio.sleep(3)

    async def handle_ticker_stream(
        self, sub_key: str, params: typing.Optional[dict] = None
    ):
        reset_timestamp = time.time() + settings.service_stream_lifetime_seconds

        client = get_ccxt_pro_client(self.connection_id)

        if params is None:
            params = {}

        self.logger.info("starting %s %s stream", self.handler_type, sub_key)

        while sub_key in self.subscriptions and reset_timestamp > time.time():
            msg = await client.watch_ticker(sub_key, params)
            self.process_msg_ticker(sub_key, msg)

        if reset_timestamp <= time.time():
            self.logger.info("expired %s %s stream", self.handler_type, sub_key)

        self.logger.info("closing %s %s stream", self.handler_type, sub_key)
