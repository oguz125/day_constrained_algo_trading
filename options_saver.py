#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 30 01:48:15 2020

@author: apolat
"""

from api import getData 
import pandas as pd
from datetime import datetime



gd = getData()

ticker = 'AAPL'

def option_chain_summary(ticker, strikeCount = 5):
    option_data = gd.OptionChain(ticker, strikeCount = strikeCount)
    df = []
    if option_data['callExpDateMap'].keys() == option_data['putExpDateMap'].keys():
        for key in option_data['callExpDateMap']:
            for strike in option_data['callExpDateMap'][key]:
                l=[]
                l.append(key)
                l.append(option_data['callExpDateMap'][key][strike][0]['last'])
                l.append(option_data['callExpDateMap'][key][strike][0]['totalVolume'])
                l.append(float(strike))
                l.append(option_data['putExpDateMap'][key][strike][0]['last'])
                l.append(option_data['putExpDateMap'][key][strike][0]['totalVolume'])
                df.append(l)

    return pd.DataFrame(data=df, columns=['Expiration','Call_Price','Call_Volume','Strike','Put_Price','Put_Volume'])
                
option_chain = option_chain_summary(ticker)

spy = list(pd.read_csv('spy.csv')['sym'])   



def list_option_chain_summary(ticker_list, strikeCount = 5):
    df = []
    for ticker in ticker_list:
        day_quote = gd.getQuote(ticker)[ticker]
        day_change = 100*(day_quote['closePrice']/day_quote['openPrice']-1)
        option_data = gd.OptionChain(ticker, strikeCount = strikeCount)
        for key in option_data['callExpDateMap']:
            if option_data['callExpDateMap'][key].keys() == option_data['putExpDateMap'][key].keys():
                for strike in option_data['callExpDateMap'][key]:
                    l=[]
                    l.append(ticker)
                    l.append(day_change)
                    l.append(key)
                    l.append(option_data['callExpDateMap'][key][strike][0]['last'])
                    l.append(option_data['callExpDateMap'][key][strike][0]['totalVolume'])
                    l.append(float(strike))
                    l.append(option_data['putExpDateMap'][key][strike][0]['last'])
                    l.append(option_data['putExpDateMap'][key][strike][0]['totalVolume'])
                    df.append(l)
    return pd.DataFrame(data=df, columns=['Ticker','Day_Change','Expiration','Call_Price','Call_Volume','Strike','Put_Price','Put_Volume'])


if __name__ == '__main__':
    additional_tickers = ['TSLA','MRNA', 'ZM', 'SPY']     
    option_chains = list_option_chain_summary(spy[:30]+additional_tickers)
    file_name = 'option_chains/'+datetime.today().strftime('%m-%d')+'.csv'                  
    option_chains.to_csv(file_name)   

