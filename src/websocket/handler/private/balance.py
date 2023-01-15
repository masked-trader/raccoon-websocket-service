import asyncio
import json
import time
import typing

from constants import SERVICE_STREAM_LIFETIME_SECONDS
from util import get_exchange_websocket_client
from websocket.handler.base import WebsocketHandler


class WebsocketBalanceHandler(WebsocketHandler):

    handler_type = "balance"

    def process_msg_balance(self, msg: dict):
        db_key = self.get_db_key_private(self.handler_type)

        for key, value in msg.items():
            self.redis.hset(db_key, key, json.dumps(value))

    async def manage_streams(self):
        self.add_subscription(self.handler_type)

        while True:
            if not self.get_subscription(self.handler_type):
                self.update_subscription(self.handler_type, status=True)

                loop = asyncio.get_running_loop()
                loop.create_task(self.handle_balance_stream())

            await asyncio.sleep(3)

    async def handle_balance_stream(self, params: typing.Optional[dict] = None):
        reset_timestamp = time.time() + SERVICE_STREAM_LIFETIME_SECONDS

        client = get_exchange_websocket_client(self.connection_id)

        if params is None:
            params = {}

        self.logger.info("starting %s stream", self.handler_type)

        while reset_timestamp > time.time():
            msg = await client.watch_balance(params)
            self.process_msg_balance(msg)

        if reset_timestamp <= time.time():
            self.logger.info("expired %s stream", self.handler_type)

        self.logger.info("closing %s stream", self.handler_type)
