# step04
# RSI14 < 30이하일 때 진입
import datetime
import time
import ccxt
import pandas as pd
import numpy as np


TIME_FRAME = '15m'
SYMBOL = "BTC/USDT"
GRID_NUM = 50               # 거미줄 50개
GRID_GAP = 300              # 300$
SLEEP_SECS = 2


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
#amount= balance['USDT']['total']['USDT'] / GRID_NUM
amount = 0.001       # minimum


def calculate_rsi(df):
    df['변화량'] = df['close'] - df['close'].shift(1)
    df['상승폭'] = np.where(df['변화량']>=0, df['변화량'], 0)
    df['하락폭'] = np.where(df['변화량'] <0, df['변화량'].abs(), 0)

    # welles moving average
    df['AU'] = df['상승폭'].ewm(alpha=1/14, min_periods=14).mean()
    df['AD'] = df['하락폭'].ewm(alpha=1/14, min_periods=14).mean()
    df['RSI'] = df['AU'] / (df['AU'] + df['AD']) * 100


def fetch_ohlcv():
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


start = False

while True:
    now = datetime.datetime.now()
    df = fetch_ohlcv()
    calculate_rsi(df)
    rsi = df.iloc[-1]['RSI']
    rsi2 = df.iloc[-2]['RSI']
    cur_price = df.iloc[-1]['close']
    print(str(now)[:19], cur_price, int(rsi), rsi2)

    if rsi < 30 and start is False:
        start = True

        # 시장가 매수로 초기 진입
        resp = exchange.create_market_buy_order(symbol=SYMBOL, amount=amount)
        price = resp['info']['avgPrice']

        # 위로 매도 예약
        sell_price = price + GRID_GAP
        exchange.create_limit_sell_order(symbol=SYMBOL, amount=amount, price=sell_price)

        # 아래로 매수 예약
        buy_price = price - GRID_GAP
        exchange.create_limit_buy_order(symbol=SYMBOL, amount=amount, price=buy_price)

        # update
        prev_buy_price = buy_price

        # 1초 쉬고 loop로 이동
        time.sleep(SLEEP_SECS)
        continue

    # 초기 진입을 한 경우
    if start is True:
        buy_remained = False
        cur_orders = exchange.fetch_open_orders(symbol="BTC/USDT")

        for order in cur_orders:
            price = float(order['info']['price'])
            side = order['info']['side']

            # 이전 매수예약이 오픈상태로 남이있다면
            if side == "BUY" and abs(prev_buy_price - price) < (GRID_GAP * 0.01):
                buy_remained = True

        # 예약매수가 체결된 경우
        if buy_remained is False:
            # 위로 매도 예약
            sell_price = prev_buy_price + GRID_GAP
            exchange.create_limit_sell_order(symbol=SYMBOL, amount=amount, price=sell_price)

            # 아래래로 매수 예약
            buy_price = prev_buy_price - GRID_GAP
            exchange.create_limit_buy_order(symbol=SYMBOL, amount=amount, price=buy_price)

            # update
            prev_buy_price = buy_price

    time.sleep(SLEEP_SECS)





