
import pandas as pd
#import numpy as np
import matplotlib.pyplot as plt
from binance.client import Client
from binance.enums import *
import Keys
import os
import time
from datetime import date, datetime, timedelta

client = Client(Keys.apiKey, Keys.apiSecurityKey)#
"""
USDTbalance  = client.get_asset_balance(asset='USDT')
#USDTbalance = int(USDTbalance)
USDTbalance = USDTbalance['free']
USDTbalance = float(USDTbalance)

print(type(USDTbalance))

Eth = client.get_symbol_ticker(symbol="BTCUSDT")
print(Eth['price'])
"""

order = client.create_order(
    symbol='BNBUSDT',
    side=SIDE_BUY,
    type=ORDER_TYPE_LIMIT,
    timeInForce=TIME_IN_FORCE_GTC,
    quantity=0.01,
    price='200'
)