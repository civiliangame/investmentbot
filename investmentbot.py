from alpha_vantage.timeseries import TimeSeries
import numpy as np
import pandas as pd
import time



token = "5J55R0F90P2AUYS1"
#Trader class
class Trader():
    def __init__(self, token, stocks, balance):
        self.ts = TimeSeries(key=token, output_format='pandas')
        self.stocks_dict = {}
        self.stocks = stocks

        #Fields:
        # last_price: int, represents the last price that the last transaction was performed at
        # quantity: int, quantity of stocks owned
        # last_action: string, buy or sell
        # last_mins: holds the most recent prices
        for element in stocks:
            self.stocks_dict[element] = {"last_price": 0, "quantity": 0, "last_action": "sell", "last_mins": [], "balance": balance}
        print(self.stocks_dict)
    # gets the time series for the given stock symbol. Gets 100 max. Interval is every minute.
    def get_timeseries(self, symbol):
        print(symbol)
        result, _ = self.ts.get_intraday(symbol=symbol,interval='1min', outputsize='compact')
        # print(_)
        return result

    # updates the most recent time series based on last_x, a variable that represents how many minutes we want to take
    # into consideration while doing our analysis
    def update(self, symbol, last_x):
        result = self.get_timeseries(symbol)
        self.stocks_dict[symbol]["last_mins"] = result["4. close"][:last_x]

    # looks at the time series and decides if we want to buy or sell
    def analysis(self, symbol):
        last_mins = pd.DataFrame(self.stocks_dict[symbol]["last_mins"]).to_numpy()

        #make the x intercept
        x = np.array([len(last_mins) - i for i in range(len(last_mins))])

        #slope of the previous time series
        poly = np.polyfit(x, last_mins, deg=1)[0]
        print("for stock %s, the slope for the past few minutes has been %s" %(symbol, poly))

        #If the last action was "buy" (meaning we are now looking to sell)
        #and the slope is negative, meaning that the stock price is falling
        if self.stocks_dict[symbol]["last_action"] == "buy" and poly < 0:

            #Also, if we bought at a lower price than the most recent price
            if self.stocks_dict[symbol]["last_price"] < last_mins[0]:
                print("selling")

                #Sell
                self.sell(symbol)

        #If the last action was selling, meaning we are looking to buy, and the stock price is increasing
        if self.stocks_dict[symbol]["last_action"] == "sell" and poly > 0:

            #buy the stock
            self.buy(symbol)



    def buy(self, symbol):

        #TODO: Edge case: what if price changes so that we cannot afford it with balance?

        #Update field to reflect this action
        self.stocks_dict[symbol]["last_action"] = "buy"

        #Calculate how many stocks we can afford
        quantity_to_buy = int(self.stocks_dict[symbol]["balance"]/self.stocks_dict[symbol]["last_mins"][0])
        # print("Quant:")
        # print(quantity_to_buy)
        #TODO: put in order to buy
        #Update balance: subtract the stock price * quantity from balance
        #TODO: Use actual stock price that the order was fulfilled at
        self.stocks_dict[symbol]["balance"] = self.stocks_dict[symbol]["balance"] - self.stocks_dict[symbol]["last_mins"][0]*quantity_to_buy #updated price


        print("Buying %s shares of stock %s at price %s." % (
        quantity_to_buy, symbol, self.stocks_dict[symbol]["last_mins"][0]))
        print("Balance of account is %s and the total value of account is %s" % (self.stocks_dict[symbol]["balance"],
                                                                                 self.stocks_dict[symbol]["balance"] +
                                                                                 self.stocks_dict[symbol]["last_mins"][
                                                                                     0] * quantity_to_buy))

        #Update last_price field to accurately reflect the price that we bought at
        #TODO: Use actual stock price that the order was fulfilled at
        self.stocks_dict[symbol]["last_price"] = self.stocks_dict[symbol]["last_mins"][0]

        #Update quantity
        self.stocks_dict[symbol]["quantity"] = quantity_to_buy



    # Sell the stock
    def sell(self, symbol):
        self.stocks_dict[symbol]["last_action"] = "sell"
        #TODO: actually sell all stocks

        #Update balance. Balance = balance + quantity*last price
        #TODO: Use actual stock price that the order was fulfilled at
        self.stocks_dict[symbol]["balance"] =self.stocks_dict[symbol]["balance"] +self.stocks_dict[symbol]["quantity"]*self.stocks_dict[symbol]["last_mins"][0]

        print("Selling %s shares of stock %s at price %s." % (
        self.stocks_dict[symbol]["quantity"], symbol, self.stocks_dict[symbol]["last_mins"][0]))


        self.stocks_dict[symbol]["quantity"] = 0


        print("Balance of account is %s" % (self.stocks_dict[symbol]["balance"]))

        #TODO: Use actual stock price that the order was fulfilled at
        self.stocks_dict[symbol]["last_price"] = self.stocks_dict[symbol]["last_mins"][0]
        #print((result["4. close"][0]))
        # (result["4. close"][:last_x])

#date = 0
#close = 4

stocks = ["AAPL", "FB", "TSLA", "NVDA", "MMM"]
t = Trader(token, stocks, 1000.0)
while 1==1:
    for stock in stocks:
        t.update(stock, 20)
        t.analysis(stock)
    time.sleep(10*60)

#
# pprint(o.stocks_dict)
# pprint(o.update("TSLA", 50))
# print("analysis")
#
# pprint(o.analysis("TSLA"))
#pprint(o.get_timeseries("TSLA"))





