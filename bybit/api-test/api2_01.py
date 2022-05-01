from pybit import HTTP
import pprint

with open("../bybit.key") as f:
    lines = f.readlines()
    api_key = lines[0].strip()
    api_secret = lines[1].strip()

session = HTTP(
    endpoint="https://api.bybit.com",
    api_key=api_key,
    api_secret=api_secret
)

resp = session.position_mode_switch(
    symbol="BTCUSDT",
    mode="MergedSingle"
)
pprint.pprint(resp)