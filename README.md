# raccoon-websocket-service

Async websocket service with Redis storage integration
and on-demand stream subscription, using `ccxt.pro` websocket methods.

## Usage

Install Docker and Docker Compose

[https://docs.docker.com/get-docker/](https://docs.docker.com/get-docker/)

**Start service**

```
docker compose up
```

**Configure exchange connection**

Generate API keys for testing

[https://testnet.binance.vision/](https://testnet.binance.vision/)

```
curl --location --request POST 'http://localhost/api/v1/config/connection/' \
--header 'Content-Type: application/json' \
--data-raw '{
    "id": "test-connection-id",
    "exchange": "binance",
    "apiKey": "YOUR_API_KEY",
    "secret": "YOUR_API_SECRET",
    "sandbox": true,
    "options": {}
}'
```

## Public Stream Subscriptions

### Ticker Stream

Subscribe to websocket ticker stream

```
curl --location --request POST 'http://localhost/api/v1/config/subscription/ticker/' \
--header 'X-Connection-Id: test-connection-id' \
--header 'Content-Type: application/json' \
--data-raw '{
    "symbol": "BTCUSDT"
}'
```

Verify data collection in Redis

```
docker compose exec redis redis-cli
```

```
127.0.0.1:6379> hget binance-sandbox-ticker BTCUSDT
"{\"symbol\": \"BTC/USDT\", \"timestamp\": 1670029046526, \"datetime\": \"2022-12-03T00:57:26.526Z\", \"high\": 17573.86, \"low\": 16426.15, \"bid\": 17044.46, \"bidVolume\": 0.114581, \"ask\": 17044.63, \"askVolume\": 0.171315, \"vwap\": 16966.21250138, \"open\": 17006.16, \"close\": 17044.46, \"last\": 17044.46, \"previousClose\": 17006.16, \"change\": 38.3, \"percentage\": 0.225, \"average\": null, \"baseVolume\": 7550.114946, \"quoteVolume\": 128096854.58368158, \"info\": {\"e\": \"24hrTicker\", \"E\": 1670029046526, \"s\": \"BTCUSDT\", \"p\": \"38.30000000\", \"P\": \"0.225\", \"w\": \"16966.21250138\", \"x\": \"17006.16000000\", \"c\": \"17044.46000000\", \"Q\": \"0.00100000\", \"b\": \"17044.46000000\", \"B\": \"0.11458100\", \"a\": \"17044.63000000\", \"A\": \"0.17131500\", \"o\": \"17006.16000000\", \"h\": \"17573.86000000\", \"l\": \"16426.15000000\", \"v\": \"7550.11494600\", \"q\": \"128096854.58368158\", \"O\": 1669942646526, \"C\": 1670029046526, \"F\": 4829287, \"L\": 5006014, \"n\": 176728}}"
```

### Kline Stream

Subscribe to websocket kline stream

```
curl --location --request POST 'http://localhost/api/v1/config/subscription/kline/' \
--header 'X-Connection-Id: test-connection-id' \
--header 'Content-Type: application/json' \
--data-raw '{
    "symbol": "BTCUSDT",
    "interval": "5m"
}'
```

Verify data collection in Redis

```
docker compose exec redis redis-cli
```

```
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

## Private Stream Subscriptions.

Private streams are automatically subscribed on submitting connection configuration

### Generate Data

Create an order to generate user account data

```
curl --location --request POST 'http://localhost/api/v1/exchange/order/' \
--header 'X-Connection-Id: test-connection-id' \
--header 'Content-Type: application/json' \
--data-raw '{
    "symbol": "BTCUSDT",
    "type": "limit",
    "side": "buy",
    "amount": 0.001,
    "price": 20000,
    "params": {}
}'
```

### Order Stream

Verify data collection in Redis

```
docker compose exec redis redis-cli
```

```
127.0.0.1:6379> hgetall binance-sandbox-test-connection-id-order-BTCUSDT
1) "7992341"
2) "{\"info\": {\"e\": \"executionReport\", \"E\": 1673906249569, \"s\": \"BTCUSDT\", \"c\": \"x-R4BD3S825b5e614625b68d98137cf3\", \"S\": \"BUY\", \"o\": \"LIMIT\", \"f\": \"GTC\", \"q\": \"0.00100000\", \"p\": \"20000.00000000\", \"P\": \"0.00000000\", \"F\": \"0.00000000\", \"g\": -1, \"C\": \"\", \"x\": \"NEW\", \"X\": \"NEW\", \"r\": \"NONE\", \"i\": 7992341, \"l\": \"0.00000000\", \"z\": \"0.00000000\", \"L\": \"0.00000000\", \"n\": \"0\", \"N\": null, \"T\": 1673906249569, \"t\": -1, \"I\": 17889024, \"w\": true, \"m\": false, \"M\": false, \"O\": 1673906249569, \"Z\": \"0.00000000\", \"Y\": \"0.00000000\", \"Q\": \"0.00000000\", \"W\": 1673906249569, \"V\": \"NONE\"}, \"symbol\": \"BTC/USDT\", \"id\": \"7992341\", \"clientOrderId\": \"x-R4BD3S825b5e614625b68d98137cf3\", \"timestamp\": 1673906249569, \"datetime\": \"2023-01-16T21:57:29.569Z\", \"lastTradeTimestamp\": null, \"type\": \"limit\", \"timeInForce\": \"GTC\", \"postOnly\": null, \"side\": \"buy\", \"price\": 20000.0, \"stopPrice\": 0.0, \"triggerPrice\": 0.0, \"amount\": 0.001, \"cost\": 0.0, \"average\": null, \"filled\": 0.0, \"remaining\": 0.001, \"status\": \"open\", \"fee\": null, \"trades\": null}"
```

Verify data collection in exchange service

```
curl --location --request GET 'http://localhost/api/v1/exchange/order/BTCUSDT/' \
--header 'X-Connection-Id: test-connection-id'
```

### Balance Stream

Verify data collection in Redis

```
docker compose exec redis redis-cli
```

```
127.0.0.1:6379> hgetall binance-sandbox-test-connection-id-balance
1) "BTC"
2) "{\"free\": 1.513, \"used\": 0.0, \"total\": 1.513}"
3) "USDT"
4) "{\"free\": 820.0, \"used\": 120.0, \"total\": 940.0}"
```

Verify data collection in exchange service

```
curl --location --request GET 'http://localhost/api/v1/exchange/market/ticker/BTCUSDT/' \
--header 'X-Connection-Id: test-connection-id'
```