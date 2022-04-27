# step03
# 5/15분봉 데이터로 RSI14 계산
import datetime
import time
import ccxt
import pandas as pd
import numpy as np

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

def calculate_rsi(df):
    df['변화량'] = df['close'] - df['close'].shift(1)
    df['상승폭'] = np.where(df['변화량']>=0, df['변화량'], 0)
    df['하락폭'] = np.where(df['변화량'] <0, df['변화량'].abs(), 0)

    # welles moving average
    df['AU'] = df['상승폭'].ewm(alpha=1/14, min_periods=14).mean()
    df['AD'] = df['하락폭'].ewm(alpha=1/14, min_periods=14).mean()
    df['RSI'] = df['AU'] / (df['AU'] + df['AD']) * 100

def update_data():
    # fetch ohlcv
    data = exchange.fetch_ohlcv(
        symbol=SYMBOL,
        timeframe=TIME_FRAME,
        since=None,
        limit=20
    )

    # convert to dataframe
    df = pd.DataFrame(data, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
    df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')
    df.set_index('datetime', inplace=True)
    return df

while True:
    now = datetime.datetime.now()
    df = update_data()
    calculate_rsi(df)
    rsi = df.iloc[-1]['RSI']
    print(now, rsi)
    time.sleep(1)





