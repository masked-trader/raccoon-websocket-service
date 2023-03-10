import asyncio
import logging

from api import internal_retrieve_connection_config
from client import get_ccxt_pro_client
from websocket.handler.private.balance import WebsocketBalanceHandler
from websocket.handler.private.order import WebsocketOrderHandler
from websocket.handler.public.kline import WebsocketKlineHandler
from websocket.handler.public.ticker import WebsocketTickerHandler


class WebsocketService:
    def __init__(self, connection_id: str):
        self.logger = logging.getLogger(f"websocket.service {connection_id}")

        self.connection_id = connection_id

        self.kline_handler = WebsocketKlineHandler(connection_id)
        self.order_handler = WebsocketOrderHandler(connection_id)
        self.ticker_handler = WebsocketTickerHandler(connection_id)
        self.balance_handler = WebsocketBalanceHandler(connection_id)

    async def start(self):
        client = get_ccxt_pro_client(self.connection_id)

        self.logger.info("starting service")

        try:
            await asyncio.gather(
                self.balance_handler.manage_streams(),
                self.kline_handler.manage_streams(),
                self.ticker_handler.manage_streams(),
                self.order_handler.manage_streams(),
            )

        except Exception as e:
            self.logger.exception(e)

        except KeyboardInterrupt:
            self.logger.info("service manual shutdown")

        finally:
            await client.close()

            get_ccxt_pro_client.cache_clear()
            internal_retrieve_connection_config.cache_clear()

            self.logger.info("connection closed")

    async def stop(self):
        self.logger.info("stopping service")

        client = get_ccxt_pro_client(self.connection_id)

        await client.close()
