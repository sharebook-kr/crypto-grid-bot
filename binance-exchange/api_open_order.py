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

orders = exchange.fetch_open_orders(
    symbol="BTC/USDT"
)

print(len(orders))
for order in orders:
    print(order['info']['side'])
    print(order['info']['price'])
    #pprint.pprint(order)