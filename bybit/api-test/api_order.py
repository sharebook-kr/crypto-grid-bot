import ccxt
import pprint


with open("../bybit.key", encoding="utf-8") as f:
    lines = f.readlines()
    api_key = lines[0].strip()
    secret  = lines[1].strip()


exchange = ccxt.bybit(config={
    'apiKey': api_key,
    'secret': secret,
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future'
    }
})


resp = exchange.create_limit_sell_order(
    symbol="BTC/USDT",
    amount=0.001,
    price=40000
)
pprint.pprint(resp)
