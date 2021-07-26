
import pandas as pd
#import numpy as np
import matplotlib.pyplot as plt
from binance.client import Client
#from binance.enums import *
import Keys
import os
import time
from datetime import date, datetime, timedelta

targetCoin = "ETH"
targetCoinExchange = targetCoin+"USDT"
client = Client(Keys.apiKey, Keys.apiSecurityKey)
os.system('cls||clear')
info = client.get_account();
print("Logged In")
balances = info['balances']
targetCoinExchange = "ETHUSDT"

def GetHistoricalPrices(targetCoinExchange):
    TargetPrices = client.get_historical_klines(targetCoinExchange, Client.KLINE_INTERVAL_1DAY, "1 Sep, 2017")
    return TargetPrices

def WritetoCSV(TargetPrices):
        with open('CurrencyPrices2.csv', 'w') as d:
            for line in TargetPrices:
                d.write(f'{line[0]}, {line[1]}, {line[2]}, {line[3]}, {line[4]}\n')

TargetPrices = GetHistoricalPrices(targetCoinExchange)
WritetoCSV(TargetPrices)

#convert csv to dataframe
targetDf = pd.read_csv('CurrencyPrices.csv')
targetDf.columns = ['Date', 'Open', 'High', 'Low', 'Close']

#calculate short term EMA
shortEMA = targetDf.Close.ewm(span = 12, adjust=False).mean()

#Calculate long term EMA
longEMA = targetDf.Close.ewm(span = 26, adjust=False).mean()

#MACD
MACD = shortEMA - longEMA

#signal Line
signal = MACD.ewm(span=5, adjust=False).mean()
targetDf['MACD'] = MACD
targetDf['Signal'] = signal

#for(x )

