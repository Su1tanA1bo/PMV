from binance.client import Client
import Keys
import os
from datetime import datetime, timedelta
import pandas as pd



client = Client(Keys.apiKey, Keys.apiSecurityKey)
os.system('cls||clear')
info = client.get_account();
print("Logged In")
balances = info['balances']
ETH = client.get_symbol_ticker(symbol="ETHUSDT")
print("Beginning program at " + (ETH["price"]))

ETHprices = client.get_historical_klines("ETHUSDT", Client.KLINE_INTERVAL_3MINUTE, "2 hours 39 minutes ago UTC")
#print(ETHprices)
lastPriceIndex = len(ETHprices)-1
closingPrices = []
for i in range (len(ETHprices)):
    value = ETHprices[i]
    clprice = value[4]
    closingPrices.append(clprice)

pricesPDformat = pd.DataFrame.from_dict(closingPrices)  
#print(pricesPDformat)
exp1 = pricesPDformat.ewm(span=12, adjust=False).mean()
exp2 = pricesPDformat.ewm(span=26, adjust=False).mean()
macd = exp1 - exp2
exp3 = macd.ewm(span=9, adjust=False).mean()
print(macd)













    

    