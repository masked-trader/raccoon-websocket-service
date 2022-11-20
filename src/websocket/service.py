import asyncio
import logging

from websocket.client import get_websocket_client
from websocket.handler.private.balance import WebsocketBalanceHandler
from websocket.handler.private.order import WebsocketOrderHandler
from websocket.handler.public.kline import WebsocketKlineHandler
from websocket.handler.public.ticker import WebsocketTickerHandler


class WebsocketService:
    def __init__(self, logger=None):
        self.logger = logging.getLogger(__name__) if logger is None else logger

        self.balance_handler = WebsocketBalanceHandler(logger=logger)
        self.order_handler = WebsocketOrderHandler(logger=logger)
        self.kline_handler = WebsocketKlineHandler(logger=logger)
        self.ticker_handler = WebsocketTickerHandler(logger=logger)

    async def start(self):
        client = get_websocket_client()

        self.logger.info("starting websocket service")

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
            self.logger.info("websocket service manual shutdown")

        finally:
            await client.close()
            self.logger.info("connection closed")
