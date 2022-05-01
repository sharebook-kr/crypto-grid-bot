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

symbol = "BTC/USDT"
params = {'positionSide': 'LONG'}

#resp = exchange.create_limit_buy_order(
#    symbol=symbol,
#    amount=0.001,
#    price=38000,
#    params=params
#)
#pprint.pprint(resp)

resp = exchange.create_limit_sell_order(
    symbol=symbol,
    amount=0.001,
    price=39000,
    params=params
)
pprint.pprint(resp)