import ccxt
import pprint

with open("../../bybit.key", encoding="utf-8") as f:
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

balance = exchange.fetch_balance()
#print(balance.keys())
pprint.pprint(balance['USDT'])
