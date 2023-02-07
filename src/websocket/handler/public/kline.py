import asyncio
import time
import typing

from client import get_ccxt_pro_client
from settings import settings
from websocket.handler.base import WebsocketHandler

TIME_SERIES_OPEN = "open"
TIME_SERIES_HIGH = "high"
TIME_SERIES_LOW = "low"
TIME_SERIES_CLOSE = "close"
TIME_SERIES_VOLUME = "volume"


class WebsocketKlineHandler(WebsocketHandler):

    handler_type = "kline"
    subscription_key = "kline-subs"

    def get_kline_time_series_key(self, symbol, interval, *args):
        return self.get_db_key(self.handler_type, symbol, interval, *args)

    def process_msg_kline(self, symbol: str, interval: str, msg: list):
        for ohlcv in msg:
            self.write_kline_time_series_data(symbol, interval, ohlcv)

    async def manage_streams(self):
        subscription_key = self.get_db_key(self.subscription_key)

        while True:
            self.manage_subscriptions(subscription_key)
            subscription = self.get_subscriptions()

            for sub_key, running in subscription.items():
                if not running:
                    self.update_subscription(sub_key=sub_key, status=True)
                    self.dispatch_task(
                        lambda: self.handle_kline_stream(sub_key=sub_key)
                    )

            await asyncio.sleep(3)

    async def handle_kline_stream(
        self,
        sub_key: str,
        since: typing.Optional[str] = None,
        limit: typing.Optional[int] = None,
        params: typing.Optional[dict] = None,
    ):
        symbol, interval = sub_key.split("-")
        reset_timestamp = time.time() + settings.service_stream_lifetime_seconds

        client = get_ccxt_pro_client(self.connection_id)

        if params is None:
            params = {}

        self.logger.info("starting %s %s stream", self.handler_type, symbol)

        if since is not None:
            since = client.iso8601(since)

        self.setup_kline_time_series(symbol, interval)

        while sub_key in self.subscriptions and reset_timestamp > time.time():
            msg = await client.watch_ohlcv(
                symbol=symbol,
                timeframe=interval,
                limit=limit,
                since=since,
                params=params,
            )

            self.process_msg_kline(symbol, interval, msg)

        if reset_timestamp <= time.time():
            self.logger.info("expired %s %s stream", self.handler_type, symbol)

        self.logger.info("closing %s %s stream", self.handler_type, symbol)

    def clean_kline_ts(self, symbol, interval):
        scan_query = self.get_kline_time_series_key(symbol, interval) + "*"

        for ts_key in self.redis.scan_iter(scan_query):
            self.redis.delete(ts_key)

    def setup_kline_time_series(self, market, interval):
        self.logger.debug(
            "setup %s time series keys - %s %s", self.handler_type, market, interval
        )

        labels = {
            "market": market,
            "interval": interval,
        }

        ts = self.redis.ts()

        ts.create(
            self.get_kline_time_series_key(market, interval, TIME_SERIES_OPEN),
            duplicate_policy=settings.redis_time_series_duplicate_policy,
            retention_msecs=settings.redis_time_series_retention_seconds,
            labels=labels,
        )
        ts.create(
            self.get_kline_time_series_key(market, interval, TIME_SERIES_HIGH),
            duplicate_policy=settings.redis_time_series_duplicate_policy,
            retention_msecs=settings.redis_time_series_retention_seconds,
            labels=labels,
        )
        ts.create(
            self.get_kline_time_series_key(market, interval, TIME_SERIES_LOW),
            duplicate_policy=settings.redis_time_series_duplicate_policy,
            retention_msecs=settings.redis_time_series_retention_seconds,
            labels=labels,
        )
        ts.create(
            self.get_kline_time_series_key(market, interval, TIME_SERIES_CLOSE),
            duplicate_policy=settings.redis_time_series_duplicate_policy,
            retention_msecs=settings.redis_time_series_retention_seconds,
            labels=labels,
        )
        ts.create(
            self.get_kline_time_series_key(market, interval, TIME_SERIES_VOLUME),
            duplicate_policy=settings.redis_time_series_duplicate_policy,
            retention_msecs=settings.redis_time_series_retention_seconds,
            labels=labels,
        )

    def write_kline_time_series_data(self, symbol, interval, ohlcv):
        ts, open, high, low, close, volume = ohlcv

        time_series_data = (
            (
                self.get_kline_time_series_key(symbol, interval, TIME_SERIES_OPEN),
                ts,
                open,
            ),
            (
                self.get_kline_time_series_key(symbol, interval, TIME_SERIES_HIGH),
                ts,
                high,
            ),
            (
                self.get_kline_time_series_key(symbol, interval, TIME_SERIES_LOW),
                ts,
                low,
            ),
            (
                self.get_kline_time_series_key(symbol, interval, TIME_SERIES_CLOSE),
                ts,
                close,
            ),
            (
                self.get_kline_time_series_key(symbol, interval, TIME_SERIES_VOLUME),
                ts,
                volume,
            ),
        )

        timeseries = self.redis.ts()
        timeseries.madd(time_series_data)
