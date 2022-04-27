# step02
# 5/15분봉 데이터를 얻기
import datetime
import time
import ccxt
import pandas as pd

TIME_FRAME = '15m'
SYMBOL = "BTC/USDT"

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


def update_data():
    data = exchange.fetch_ohlcv(
        symbol=SYMBOL,
        timeframe=TIME_FRAME,
        since=None,
        limit=20
    )

    # dataframe
    df = pd.DataFrame(data, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
    df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')
    df.set_index('datetime', inplace=True)
    return df

while True:
    now = datetime.datetime.now()
    print(now)
    df = update_data()
    print(df)
    time.sleep(1)


