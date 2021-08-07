from csv import reader
import pandas as pd
#import numpy as np
import matplotlib.pyplot as plt
from binance.client import Client
#from binance.enums import *
import Keys
import os
import time
import datetime

targetCoin = "ETH"
targetCoinExchange = targetCoin+"USDT"
client = Client(Keys.apiKey, Keys.apiSecurityKey)
os.system('cls||clear')
info = client.get_account();
print("Logged In")
balances = info['balances']


#Seeing if price is correct
ETH = client.get_symbol_ticker(symbol="ETHUSDT")
print("Beginning program at " + (ETH["price"]))

def GetHistoricalPrices(targetCoinExchange):
    TargetPrices = client.get_historical_klines(targetCoinExchange, Client.KLINE_INTERVAL_1DAY, "1 Sep, 2017")
    return TargetPrices

def WritetoCSV(TargetPrices):
        with open('CurrencyPrices.csv', 'w') as d:
            for line in TargetPrices:
                d.write(f'{line[0]}, {line[1]}, {line[2]}, {line[3]}, {line[4]}\n')

TargetPrices = GetHistoricalPrices(targetCoinExchange)
WritetoCSV(TargetPrices)

#convert csv to dataframe
targetDf = pd.read_csv('CurrencyPrices.csv')
targetDf.columns = ['Date', 'Open', 'High', 'Low', 'Close']

#calculate short term EMA
shortEMA = targetDf.Close.ewm(span = 5, adjust=False).mean()

#Calculate long term EMA
longEMA = targetDf.Close.ewm(span = 35, adjust=False).mean()

#MACD
MACD = shortEMA - longEMA

#signal Line
signal = MACD.ewm(span=5, adjust=False).mean()
targetDf['MACD'] = MACD
targetDf['Signal'] = signal

#print(targetDf)

#making list copies of macd and signal
macdList = targetDf['MACD'].tolist()
signalList = targetDf['Signal'].tolist()

#BuySellSignal will return 1/0 depending on whether MACD suggest buy/sell
def BuySellSignal(recentMACDValue, recentSignalValue):
    posOnGraph = " "
    if (float(recentMACDValue)) >= 0 and float(recentSignalValue) >= 0:
        posOnGraph="bothPositive"
    elif (float(recentMACDValue)) >= 0 and float(recentSignalValue) <= 0:
        posOnGraph ="macdPositive,signalNegative"
    elif (float(recentMACDValue)) <= 0 and float(recentSignalValue) >= 0:
        posOnGraph="macdNegative,signalPositive"
    elif (float(recentMACDValue)) <= 0 and float(recentSignalValue) <= 0:
        posOnGraph="bothNegative"
    
    if posOnGraph == "bothPositive":
        if((recentMACDValue - recentSignalValue) > 0 ):
            return 1
        else: 
            return 0

    elif posOnGraph == "macdPositive,signalNegative":
        if((recentMACDValue) - (recentSignalValue) >= 3):
            return 1
        else:
            return 0

    elif posOnGraph == "macdNegative,signalPositive":
        return 0

    elif posOnGraph == "bothNegative":
        if(abs(recentSignalValue) - abs(recentMACDValue) > 0):
            return 1
        else:
            return 0

BuyOrSellList = []
def macdAndSignalCycler():
    for i in range(len(macdList)):
        macdValue = macdList[i]
        signalValue = signalList[i]
        result = BuySellSignal(macdValue, signalValue)
        BuyOrSellList.append(result)

macdAndSignalCycler()

#adding buyorsell list to dataframe
targetDf['BuyOrSell'] = BuyOrSellList
#print(targetDf)

#unix to calendar date converter
def UnixToCalendar(Unix):
    date = datetime.datetime.fromtimestamp(Unix)
    date = f"{date:%Y-%m-%d}"
    return date

Date = []
for i in range(len(targetDf['Date'])):
    value = (int(targetDf.Date[i]))/1000
    value = UnixToCalendar(value)
    Date.append(value)

targetDf['Date'] = Date

print(targetDf)
#making into csv
targetDf.to_csv('TargetInfo.csv')  


CriticalPoints = []
#now we need to cycle through the buy/sell signal column in the csv file and calculate percentage of profits
olderValue = 0 

for i in range(len(BuyOrSellList)):
    currentValue = BuyOrSellList[i]
    if olderValue != currentValue:
        price = targetDf.Close[i]
        CriticalPoints.append(price)
        olderValue = currentValue
    else:  
        continue

textfile = open("CriticalPoints.txt", "w")
for element in CriticalPoints:
    textfile.write(str(element) + "\n")
textfile.close()

currentEntry = 0.00
currentExit = 0.00
totalGain = 0.00
currentGain = 0.00

for i in range(0, len(CriticalPoints)):
    if i == 0:
        currentEntry = CriticalPoints[i]
        print("Bought at: " + str(currentEntry))
        continue
    if i == 1:
        currentExit = CriticalPoints[i]
        print("Sold at: "+ str(CriticalPoints[i]))
        currentGain = ((currentExit-currentEntry)/currentEntry)
        print("Gain/Loss: " + str(currentGain) + " or " + str(currentExit - currentEntry) + " USDT\n")
        totalGain = totalGain + currentGain
        continue
    if (i%2 == 0):
        currentEntry = CriticalPoints[i]
        print("bought at: "+ str(CriticalPoints[i]))
        continue
    if (i%2 == 1):
        currentExit = CriticalPoints[i]
        print("sold at: "+ str(CriticalPoints[i]))
        currentGain = ((currentExit-currentEntry)/currentEntry)
        totalGain = round(totalGain + currentGain, 3)
        print("Gain/Loss: " + str(currentGain) + " or " + str(currentExit - currentEntry) + " USDT")
        print("Total Gain/Loss: " + str(totalGain) + "\n")

        continue
    



