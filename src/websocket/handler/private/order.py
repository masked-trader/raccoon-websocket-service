import asyncio
import json
import time
import typing

from client import get_ccxt_pro_client
from internal import internal_update_order_data
from settings import settings
from websocket.handler.base import WebsocketHandler


class WebsocketOrderHandler(WebsocketHandler):

    handler_type = "order"

    def process_msg_order(self, msg: list):
        for data in msg:
            symbol = data["symbol"].replace("/", "")

            db_key = self.get_db_key_private(self.handler_type, symbol)
            self.redis.hset(db_key, data["id"], json.dumps(data))

            order_data = {
                **data,
                "symbol": symbol,
                "orderId": data["id"],
                "connection": self.connection_id,
            }

            del order_data["id"]

            self.dispatch_task(
                lambda: internal_update_order_data(self.connection_id, order_data)
            )

    async def manage_streams(self):
        self.add_subscription(self.handler_type)

        while True:
            if not self.get_subscription(self.handler_type):
                self.update_subscription(self.handler_type, status=True)
                self.dispatch_task(lambda: self.handle_order_stream())

            await asyncio.sleep(3)

    async def handle_order_stream(
        self,
        symbol: typing.Optional[str] = None,
        since: typing.Optional[str] = None,
        limit: typing.Optional[int] = None,
        params: typing.Optional[dict] = None,
    ):
        reset_timestamp = time.time() + settings.service_stream_lifetime_seconds

        client = get_ccxt_pro_client(self.connection_id)

        if since is not None:
            since = client.iso8601(since)

        if params is None:
            params = {}

        self.logger.info("starting %s stream", self.handler_type)

        while reset_timestamp > time.time():
            msg = await client.watch_orders(
                symbol=symbol, since=since, limit=limit, params=params
            )

            self.process_msg_order(msg)

        if reset_timestamp <= time.time():
            self.logger.info("expired %s stream", self.handler_type)

        self.logger.info("closing %s stream", self.handler_type)
