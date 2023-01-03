# raccoon-websocket-service

Async websocket service with Redis storage integration
and on-demand stream subscription, using `ccxt.pro` websocket methods.

## Setup

Install Docker and Docker Compose

[https://docs.docker.com/get-docker/](https://docs.docker.com/get-docker/)

Local development requires a `.env.development` env file. See the included `.env.development.sample` for reference.

**Start websocket service**

```
docker compose up
```

**Access Redis CLI in container**

```
docker compose exec redis redis-cli
```

The following examples were based on the `.env.development.sample` configuration and using development API key for Binance testnet.

## Public Stream Subscriptions

### Ticker Stream

```
127.0.0.1:6379> set binance-sandbox-ticker-subs '["BTCUSDT"]'
OK

127.0.0.1:6379> hget binance-sandbox-ticker BTCUSDT
"{\"symbol\": \"BTC/USDT\", \"timestamp\": 1670029046526, \"datetime\": \"2022-12-03T00:57:26.526Z\", \"high\": 17573.86, \"low\": 16426.15, \"bid\": 17044.46, \"bidVolume\": 0.114581, \"ask\": 17044.63, \"askVolume\": 0.171315, \"vwap\": 16966.21250138, \"open\": 17006.16, \"close\": 17044.46, \"last\": 17044.46, \"previousClose\": 17006.16, \"change\": 38.3, \"percentage\": 0.225, \"average\": null, \"baseVolume\": 7550.114946, \"quoteVolume\": 128096854.58368158, \"info\": {\"e\": \"24hrTicker\", \"E\": 1670029046526, \"s\": \"BTCUSDT\", \"p\": \"38.30000000\", \"P\": \"0.225\", \"w\": \"16966.21250138\", \"x\": \"17006.16000000\", \"c\": \"17044.46000000\", \"Q\": \"0.00100000\", \"b\": \"17044.46000000\", \"B\": \"0.11458100\", \"a\": \"17044.63000000\", \"A\": \"0.17131500\", \"o\": \"17006.16000000\", \"h\": \"17573.86000000\", \"l\": \"16426.15000000\", \"v\": \"7550.11494600\", \"q\": \"128096854.58368158\", \"O\": 1669942646526, \"C\": 1670029046526, \"F\": 4829287, \"L\": 5006014, \"n\": 176728}}"
```

### Kline Stream

```
127.0.0.1:6379> set binance-sandbox-kline-subs '["BTCUSDT-5m"]'
OK

127.0.0.1:6379> ts.get binance-sandbox-kline-BTCUSDT-5m-open
1) (integer) 1671844500000
2) 16805.68

127.0.0.1:6379> ts.get binance-sandbox-kline-BTCUSDT-5m-high
1) (integer) 1671844500000
2) 16807.12

127.0.0.1:6379> ts.get binance-sandbox-kline-BTCUSDT-5m-low
1) (integer) 1671844500000
2) 16801.47

127.0.0.1:6379> ts.get binance-sandbox-kline-BTCUSDT-5m-close
1) (integer) 1671844500000
2) 16801.66

127.0.0.1:6379> ts.get binance-sandbox-kline-BTCUSDT-5m-volume
1) (integer) 1671844500000
2) 22.270596
```

## Private Stream Subscriptions

Private API data is stored with keys that include a unique identifier, which is derived from the API key.
Making data collected to be unique for the API key, while public API data is not specific for the API key.

### Generate Data

Example script for generating order data on Binance testnet

Get a development API key for testing:

[https://testnet.binance.vision/](https://testnet.binance.vision/)

```
#!/usr/bin/python3

import ccxt

binance = ccxt.binance({ "apiKey": "<api_key>", "secret": "<secret>" })
binance.set_sandbox_mode(True)

binance.create_order("BTCUSDT", "limit", "buy", 0.1, 17000)
binance.create_order("ETHUSDT", "limit", "buy", 0.1, 1300)
```

### Balance Stream

```
127.0.0.1:6379> keys *
1) "binance-sandbox-4db7ef-balance"

127.0.0.1:6379> hkeys binance-sandbox-4db7ef-balance
1) "total"
2) "datetime"
3) "free"
4) "used"
5) "info"
6) "BTC"
7) "timestamp"
8) "USDT"
9) "ETH"

127.0.0.1:6379> hget binance-sandbox-4db7ef-balance free
"{\"BTC\": 1.2, \"USDT\": 6515.87905232, \"ETH\": 100.1}"

127.0.0.1:6379> hget binance-sandbox-4db7ef-balance total
"{\"BTC\": 1.2, \"USDT\": 6515.87905232, \"ETH\": 100.1}"

127.0.0.1:6379> hget binance-sandbox-4db7ef-balance USDT
"{\"free\": 6515.87905232, \"used\": 0.0, \"total\": 6515.87905232}"

127.0.0.1:6379> hget binance-sandbox-4db7ef-balance BTC
"{\"free\": 1.2, \"used\": 0.0, \"total\": 1.2}"

127.0.0.1:6379> hget binance-sandbox-4db7ef-balance ETH
"{\"free\": 100.1, \"used\": 0.0, \"total\": 100.1}"
```

### Order Stream

```
127.0.0.1:6379> keys *
1) "binance-sandbox-4db7ef-order-BTCUSDT"
2) "binance-sandbox-4db7ef-order-ETHUSDT"

127.0.0.1:6379> hkeys binance-sandbox-4db7ef-order-BTCUSDT
1) "5699638"

127.0.0.1:6379> hget binance-sandbox-4db7ef-order-BTCUSDT 5699638
"{\"info\": {\"e\": \"executionReport\", \"E\": 1671846028770, \"s\": \"BTCUSDT\", \"c\": \"x-R4BD3S82e95ad7340fca4354ed6bec\", \"S\": \"BUY\", \"o\": \"LIMIT\", \"f\": \"GTC\", \"q\": \"0.10000000\", \"p\": \"17000.00000000\", \"P\": \"0.00000000\", \"F\": \"0.00000000\", \"g\": -1, \"C\": \"\", \"x\": \"TRADE\", \"X\": \"FILLED\", \"r\": \"NONE\", \"i\": 5699638, \"l\": \"0.09934600\", \"z\": \"0.10000000\", \"L\": \"16806.21000000\", \"n\": \"0.00000000\", \"N\": \"BTC\", \"T\": 1671846028770, \"t\": 1144309, \"I\": 12541957, \"w\": false, \"m\": false, \"M\": true, \"O\": 1671846028770, \"Z\": \"1680.62098692\", \"Y\": \"1669.62973866\", \"Q\": \"0.00000000\", \"W\": 1671846028770, \"V\": \"NONE\"}, \"symbol\": \"BTC/USDT\", \"id\": \"5699638\", \"clientOrderId\": \"x-R4BD3S82e95ad7340fca4354ed6bec\", \"timestamp\": 1671846028770, \"datetime\": \"2022-12-24T01:40:28.770Z\", \"lastTradeTimestamp\": 1671846028770, \"type\": \"limit\", \"timeInForce\": \"GTC\", \"postOnly\": null, \"side\": \"buy\", \"price\": 17000.0, \"stopPrice\": 0.0, \"amount\": 0.1, \"cost\": 1680.62098692, \"average\": 16806.2098692, \"filled\": 0.1, \"remaining\": 0.0, \"status\": \"closed\", \"fee\": {\"cost\": 0.0, \"currency\": \"BTC\"}, \"trades\": [{\"info\": {\"e\": \"executionReport\", \"E\": 1671846028770, \"s\": \"BTCUSDT\", \"c\": \"x-R4BD3S82e95ad7340fca4354ed6bec\", \"S\": \"BUY\", \"o\": \"LIMIT\", \"f\": \"GTC\", \"q\": \"0.10000000\", \"p\": \"17000.00000000\", \"P\": \"0.00000000\", \"F\": \"0.00000000\", \"g\": -1, \"C\": \"\", \"x\": \"TRADE\", \"X\": \"PARTIALLY_FILLED\", \"r\": \"NONE\", \"i\": 5699638, \"l\": \"0.00065400\", \"z\": \"0.00065400\", \"L\": \"16806.19000000\", \"n\": \"0.00000000\", \"N\": \"BTC\", \"T\": 1671846028770, \"t\": 1144308, \"I\": 12541955, \"w\": false, \"m\": false, \"M\": true, \"O\": 1671846028770, \"Z\": \"10.99124826\", \"Y\": \"10.99124826\", \"Q\": \"0.00000000\", \"W\": 1671846028770, \"V\": \"NONE\"}, \"timestamp\": 1671846028770, \"datetime\": \"2022-12-24T01:40:28.770Z\", \"symbol\": \"BTC/USDT\", \"id\": \"1144308\", \"order\": \"5699638\", \"type\": \"limit\", \"takerOrMaker\": \"taker\", \"side\": \"buy\", \"price\": 16806.19, \"amount\": 0.000654, \"cost\": 10.99124826, \"fee\": {\"cost\": 0.0, \"currency\": \"BTC\"}}, {\"info\": {\"e\": \"executionReport\", \"E\": 1671846028770, \"s\": \"BTCUSDT\", \"c\": \"x-R4BD3S82e95ad7340fca4354ed6bec\", \"S\": \"BUY\", \"o\": \"LIMIT\", \"f\": \"GTC\", \"q\": \"0.10000000\", \"p\": \"17000.00000000\", \"P\": \"0.00000000\", \"F\": \"0.00000000\", \"g\": -1, \"C\": \"\", \"x\": \"TRADE\", \"X\": \"FILLED\", \"r\": \"NONE\", \"i\": 5699638, \"l\": \"0.09934600\", \"z\": \"0.10000000\", \"L\": \"16806.21000000\", \"n\": \"0.00000000\", \"N\": \"BTC\", \"T\": 1671846028770, \"t\": 1144309, \"I\": 12541957, \"w\": false, \"m\": false, \"M\": true, \"O\": 1671846028770, \"Z\": \"1680.62098692\", \"Y\": \"1669.62973866\", \"Q\": \"0.00000000\", \"W\": 1671846028770, \"V\": \"NONE\"}, \"timestamp\": 1671846028770, \"datetime\": \"2022-12-24T01:40:28.770Z\", \"symbol\": \"BTC/USDT\", \"id\": \"1144309\", \"order\": \"5699638\", \"type\": \"limit\", \"takerOrMaker\": \"taker\", \"side\": \"buy\", \"price\": 16806.21, \"amount\": 0.099346, \"cost\": 1669.62973866, \"fee\": {\"cost\": 0.0, \"currency\": \"BTC\"}}]}"
```
