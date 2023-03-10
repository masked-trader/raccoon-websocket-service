import asyncio
import json
import time
import typing

from api import internal_update_balance_data
from client import get_ccxt_pro_client
from settings import settings
from websocket.handler.base import WebsocketHandler

MESSAGE_KEY_FREE = "free"
MESSAGE_KEY_USED = "used"
MESSAGE_KEY_TOTAL = "total"


class WebsocketBalanceHandler(WebsocketHandler):

    handler_type = "balance"

    def process_msg_balance(self, msg: dict):
        db_key = self.get_db_key_private(self.handler_type)

        for asset in msg[MESSAGE_KEY_TOTAL].keys():
            balance_data = {
                "free": msg[MESSAGE_KEY_FREE][asset],
                "used": msg[MESSAGE_KEY_USED][asset],
                "total": msg[MESSAGE_KEY_TOTAL][asset],
            }

            self.redis.hset(db_key, asset, json.dumps(balance_data))

            self.dispatch_task(
                lambda: internal_update_balance_data(
                    self.connection_id,
                    {
                        **balance_data,
                        "asset": asset,
                        "connection": self.connection_id,
                    },
                )
            )

    async def manage_streams(self):
        self.add_subscription(self.handler_type)

        while True:
            if not self.get_subscription(self.handler_type):
                self.update_subscription(self.handler_type, status=True)
                self.dispatch_task(lambda: self.handle_balance_stream())

            await asyncio.sleep(3)

    async def handle_balance_stream(self, params: typing.Optional[dict] = None):
        reset_timestamp = time.time() + settings.service_stream_lifetime_seconds

        client = get_ccxt_pro_client(self.connection_id)

        if params is None:
            params = {}

        self.logger.info("starting %s stream", self.handler_type)

        while reset_timestamp > time.time():
            msg = await client.watch_balance(params)
            self.process_msg_balance(msg)

        if reset_timestamp <= time.time():
            self.logger.info("expired %s stream", self.handler_type)

        self.logger.info("closing %s stream", self.handler_type)
