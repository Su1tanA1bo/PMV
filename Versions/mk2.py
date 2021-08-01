
#%%
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
ETH = client.get_symbol_ticker(symbol="ETHUSDT")
print("Beginning program at " + (ETH["price"]))

#def buyTargetTicker():


#theAdministrator decides whether we buy or sell. 1 = buy, -1 = sell. the difference between this and int(flag) is the administrator knows whether we're currently holding or buying or bearish
#as its not in the while loop
theAdministrator = -1
#programlooper is created to allow an infinite loop
programlooper = 5

def GetHistoricalPrices(targetCoinExchange):
    TargetPrices = client.get_historical_klines(targetCoinExchange, Client.KLINE_INTERVAL_1DAY, "1 Sep, 2017")
    return TargetPrices

while(programlooper == 5):
    try:
        client = Client(Keys.apiKey, Keys.apiSecurityKey)
        #get ETH prices every 3 minutes from 3 hrs ago

        TargetPrices = GetHistoricalPrices(targetCoinExchange)
    except:
        now = datetime.now()
        currentTime = now.strftime("%H:%M:%S")
        print('Something went wrong @: '+str(currentTime))
        time.sleep(3600)
        client = Client(Keys.apiKey, Keys.apiSecurityKey)
        TargetPrices = GetHistoricalPrices(targetCoinExchange)
        continue
    #write prices into csv file
    def WritetoCSV():
        with open('CurrencyPrices.csv', 'w') as d:
            for line in TargetPrices:
                d.write(f'{line[0]}, {line[1]}, {line[2]}, {line[3]}, {line[4]}\n')

    WritetoCSV()

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
    print(targetDf)

    #defining function
    def logSignalChange():
     f=open("log.txt", "a+")
     f.write("\n")
     today= str(date.today())
     f.write(today + ", ")
     now = datetime.now() + timedelta(hours = 1)
     current_time = now.strftime("%H:%M:%S")
     f.write("time: "+str(current_time)+", ")
     f.write("Close; "+ str(targetDf.Close[len(targetDf.Close)-1])+", ")
     if(theAdministrator == 1):
        f.write("buy/hold, ")
     elif(theAdministrator == -1):
        f.write("sell, ")
     f.write("MACD: "+str(targetDf.MACD[len(targetDf.MACD)-1])+", ")
     f.write("Signal: "+str(targetDf.Signal[len(targetDf.Signal)-1])+", ")
     f.write(posOnGraph)

    recentMACDValue = targetDf.MACD[len(MACD)-1]
    print("Macd:",recentMACDValue)
    recentSignalValue = targetDf.Signal[len(signal)-1]
    print("Signal",recentSignalValue)

    #finding USDT current balance
    USDTbalance = client.get_asset_balance(asset='USDT')
    print("Your current Tether(USDT) balance : "+str((USDTbalance['free'])) )
    #conditions of buying/selling
    posOnGraph = ""

    if (float(recentMACDValue)) >= 0 and float(recentSignalValue) >= 0:
        posOnGraph ="bothPositive"
    elif (float(recentMACDValue)) >= 0 and float(recentSignalValue) <= 0:
        posOnGraph ="macdPositive,signalNegative"
    elif (float(recentMACDValue)) <= 0 and float(recentSignalValue) >= 0:
        posOnGraph="macdNegative,signalPositive"
    elif (float(recentMACDValue)) <= 0 and float(recentSignalValue) <= 0:
        posOnGraph="bothNegative"

    print(posOnGraph)

    AdminPreviousDecision = theAdministrator

    def buyOrder():
        # target price in float
        targetPrice = client.get_symbol_ticker(symbol=targetCoinExchange)
        targetPrice = float(targetPrice['price'])
        # USDT balance in float
        USDTfloat= USDTbalance['free']
        USDTfloat = float(USDTfloat)
        #seeing target quantity capable for purchase
        capableToBuy = targetPrice/USDTfloat
        quantityToBePurchased = float(1/capableToBuy)
        quantityToBePurchased = round(quantityToBePurchased - ((quantityToBePurchased/100)*0.5), 5)
        order = client.order_market_buy(
            symbol=targetCoinExchange,
            quantity=quantityToBePurchased)
        order()
        print("Purchase Made: "+quantityToBePurchased+ targetCoin)

    def sellOrder():
        #getting balance of coin
        targetCoinBalance = round(float(client.get_asset_balance(asset=targetCoin)), 5)
        order = client.order_market_sell(
            symbol=targetCoinExchange,
            quantity=targetCoinBalance)
        order()
        print(targetCoinBalance+" "+targetCoin+" sold! ")


    if posOnGraph == "bothPositive":
        if((recentMACDValue - recentSignalValue) >= 3):
            print("buy/hold")
            if(theAdministrator == -1):
                theAdministrator = 1
                #buyOrder()
        else:
            if(theAdministrator == 1):
                theAdministrator = -1
                #sellOrder()
                print("sell")
            if(theAdministrator == -1):
                print("Bearish - Not Engaging")

    elif posOnGraph == "macdPositive,signalNegative":
        if((recentMACDValue) - (recentSignalValue) >= 3):
            print("buy/hold")
            if(theAdministrator == -1):
                theAdministrator = 1
                #buyOrder()
        else:
            if(theAdministrator == 1):
                theAdministrator = -1
                #sellOrder()
                print("sell")
            if(theAdministrator == -1):
                print("Bearish - Not Engaging")

    elif posOnGraph == "macdNegative,signalPositive":
        print("sell")
        if(theAdministrator == 1):
            theAdministrator = -1
            print("sell")
            #sellOrder()
        elif(theAdministrator == -1):
                print("Bearish - Not Engaging")

    elif posOnGraph == "bothNegative":
        if(abs(recentSignalValue) - abs(recentMACDValue) >= 3):
            print("buy/hold")
            if(theAdministrator == -1):
                theAdministrator = 1
                #buyOrder()
        else:
            if(theAdministrator == 1):
                theAdministrator = -1
                #sellOrder()
                print("sell")
            elif(theAdministrator == -1):
                print("Bearish - Not Engaging")


    print("Administrator: ",+theAdministrator)

    #plot both closing price graph and MACD graph
    plt.subplot(2,1,1)
    plt.plot(targetDf.index*3, MACD, label = 'MACD', color = 'blue')
    plt.plot(targetDf.index*3, signal, label = 'Signal', color = 'red')
    plt.ylabel("MACD")
    plt.legend(loc='lower left')
    plt.grid()

    plt.subplot(2,1,2)
    plt.plot(targetDf.index*3, targetDf['Close'], label = 'Close', color = 'black')
    plt.ylabel("Price")
    plt.legend(loc='lower left')
    plt.grid()
    plt.show() #comment out if you dont want graph pop up
    plt.savefig("currentGraph.pdf")


    #if changed
    if(theAdministrator != AdminPreviousDecision):
        logSignalChange()
        print("action logged")

    #buy_order = client.create_test_order(symbol=targetCoinExchange, side='BUY', type='MARKET', quantity=100)
    #print(buy_order)
    now = datetime.now() + timedelta(hours = 1)
    currentTime = now.strftime("%H:%M:%S")
    print(currentTime)
    #time.sleep(86400)

    os.remove("CurrencyPrices.csv")
    plt.cla()
    plt.clf()




    # %%




