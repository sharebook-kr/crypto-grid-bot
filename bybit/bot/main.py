import ccxt
import datetime
import time
import numpy as np
import pandas as pd

SYMBOL = "BTC/USDT"
UNIT_AMOUNT = 0.01
GRID = 300                          # 300 달러
RSI_MIN = 35
ELAPSED_TIME_LIMIT = 3600 * 10      # 10 hours

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

def calculate_rsi(df):
    df['변화량'] = df['close'] - df['close'].shift(1)
    df['상승폭'] = np.where(df['변화량']>=0, df['변화량'], 0)
    df['하락폭'] = np.where(df['변화량'] <0, df['변화량'].abs(), 0)

    # welles moving average
    df['AU'] = df['상승폭'].ewm(alpha=1/14, min_periods=14).mean()
    df['AD'] = df['하락폭'].ewm(alpha=1/14, min_periods=14).mean()
    df['RSI'] = df['AU'] / (df['AU'] + df['AD']) * 100
    return df

def fetch_ohlcv():
    # fetch ohlcv
    data = exchange.fetch_ohlcv(
        symbol=SYMBOL,
        timeframe='15m',
        since=None,
        limit=20
    )

    # convert to dataframe
    df = pd.DataFrame(data, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
    df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')
    df.set_index('datetime', inplace=True)
    return df

def close_all_positions(exchange):
    resp = exchange.private_linear_get_position_list({'symbol':SYMBOL})
    positions = resp['result']
    for position in positions:
        if position['entry_price'] == '0':
            continue

        exchange.create_market_order(
            symbol=SYMBOL,
            side="sell",
            amount=0.001,
            params = {'reduce_only': True}
        )

def cleanup(exchange):
    global is_running

    is_running = False

    # cancel all orders
    exchange.cancel_all_orders(symbol=SYMBOL)

    # close all positions
    close_all_positions(exchange)


def is_target_grid_excuted(exchange, target_price, open_orders):
    target_grid_exist = False
    for order in open_orders:
        price = float(order['info']['price'])
        side = order['info']['side']

        if side == "Buy" and price == target_price:
            target_grid_exist = True

    if target_grid_exist:
        return False
    else:
        return True

is_running = False
run_start_time = 0
elapsed_time = 0
target_grid_price = 0
balance = exchange.fetch_balance()
prev_usdt = balance['USDT']['total']


while True:
    df = fetch_ohlcv()
    df_rsi = calculate_rsi(df)
    close = float(df.iloc[-1].loc['close'])
    rsi = df_rsi.iloc[-1].loc['RSI']

    balance = exchange.fetch_balance()
    curr_usdt = balance['USDT']['total']

    now = datetime.datetime.now()
    fmt_time = str(now)[:19]
    fmt = f"{fmt_time} | {close} | {rsi: .2f}"
    print(fmt)

    # 현재 거미줄 매매가 돌고 있을 때
    if is_running:
        delta = now - run_start_time
        elapsed_time = delta.seconds            # 경과시간(초)

        # 일정 시간이 지나면 정리하는 기능
        if elapsed_time >= ELAPSED_TIME_LIMIT:
            cleanup(exchange)
            continue

        # 전체 잔고 기준 익절
        rate_of_return = (curr_usdt - prev_usdt) / prev_usdt * 100
        if rate_of_return >= 4:
            cleanup(exchange)
            continue

        # open long 체결이 체결된 경우
        open_orders = exchange.fetch_open_orders(symbol=SYMBOL)

        # 거미줄 체결 감시
        if is_target_grid_excuted(exchange, target_grid_price, open_orders):
            # 아래로 매수 거미줄
            exchange.create_limit_order(
                symbol=SYMBOL,
                side="buy",
                amount=0.001,
                price=target_grid_price-GRID
            )

            # 위로 매도 거미줄
            exchange.create_limit_order(
                symbol=SYMBOL,
                side="sell",
                amount=0.001,
                price=target_grid_price+GRID,
                params = {'reduce_only': True}
            )

            # 체결 감시 거미줄 가격 업데이트
            target_grid_price = target_grid_price-GRID


    # 거미줄 시작
    if is_running is False and rsi < RSI_MIN:
        run_start_time = datetime.datetime.now()
        target_grid_price = close

        # open long (market)
        exchange.create_market_order(
            symbol=SYMBOL,
            side = "buy",
            amount=UNIT_AMOUNT
        )

        # 현재 거미줄 하나 아래로 open long (limit)
        exchange.create_limit_order(
            symbol=SYMBOL,
            side="buy",
            amount=0.001,
            price=target_grid_price-GRID
        )

        # 현재 거미줄 하나 위로 close long (limit)
        exchange.create_limit_order(
            symbol=SYMBOL,
            side="sell",
            amount=0.001,
            price=target_grid_price+GRID,
            params = {'reduce_only': True}
        )

    time.sleep(2)