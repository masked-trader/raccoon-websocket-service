#!/usr/bin/env python

import asyncio
import logging

from constants import WEBSOCKET_LOG_LEVEL
from websocket.service import WebsocketService

logging.basicConfig(
    level=getattr(logging, WEBSOCKET_LOG_LEVEL),
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)

logger = logging.getLogger("websocket")


def main():
    manager = WebsocketService(logger=logger)

    asyncio.run(manager.start())


if __name__ == "__main__":
    main()
