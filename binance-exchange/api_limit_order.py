import ccxt
import pprint


with open("../binance.key", encoding="utf-8") as f:
    lines = f.readlines()
    api_key = lines[0].strip()
    secret  = lines[1].strip()


exchange = ccxt.binance(config={
    'apiKey': api_key,
    'secret': secret,
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future'
    }
})


# 잔고조회
balance = exchange.fetch_balance(params={"type": "future"})
usdt = balance['total']['USDT']
print(usdt)

exchange.create_limit_buy_order(
    symbol="BTC/USDT",
    amount=0.001,
    price=38917-300
)

exchange.create_limit_sell_order(
    symbol="BTC/USDT",
    amount=0.001,
    price=38917+300
)
