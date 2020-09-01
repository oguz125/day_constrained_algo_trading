#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May  1 11:51:40 2020

@author: apolat
"""

import requests
import time
import csv
import pandas as pd
import datetime

'''
The key.txt file contains the consumer key, account id and refresh_token linebreak separated.
'''

class getData:
     def __init__(self):
         keys=[]
         with open('/Users/apolat/bin/key.txt') as csv_file:
             csv_reader = csv.reader(csv_file, delimiter=',')
             for row in csv_reader:
                 keys.append(row[1])
         self.consumer_key=keys[0]
         self.api_url='https://api.tdameritrade.com/v1/'
         self.mkt='marketdata/'
         self.account_id=keys[1]
         self.authorization=None
         self.last_refresh_time=None
         self.refresh_token=keys[2]
     
     def refresh(self):
         payload={'grant_type':'refresh_token',
                  'refresh_token':self.refresh_token,
                  'client_id':self.consumer_key
             }
         url=self.api_url+'oauth2/token'
         
         self.authorization=requests.post(url,data=payload).json()['access_token']
         self.last_refresh_time=time.time()
         
     def getPrice(self,ticker,periodType='day',period=None,frequencyType='minute',frequency=1,endDate=None,startDate=None,needExtendedHoursData=True, df=False):
         """

         Parameters
         ----------
         ticker : str
         periodType : str, optional
             The type of period to show. Valid values are day, month, year, or ytd (year to date). The default is 'day'.
         period : int, optional
             The number of periods to show.

            Example: For a 2 day / 1 min chart, the values would be:
            
            period: 2
            periodType: day
            frequency: 1
            frequencyType: min
            
            Valid periods by periodType (defaults marked with an asterisk):
            
            day: 1, 2, 3, 4, 5, 10*
            month: 1*, 2, 3, 6
            year: 1*, 2, 3, 5, 10, 15, 20
            ytd: 1* 
         frequencyType : str, optional
             The type of frequency with which a new candle is formed.
            Valid frequencyTypes by periodType (defaults marked with an asterisk):
            
            day: minute*
            month: daily, weekly*
            year: daily, weekly, monthly*
            ytd: daily, weekly*
         frequency : int, optional
             The number of the frequencyType to be included in each candle.

            Valid frequencies by frequencyType (defaults marked with an asterisk):
            
            minute: 1*, 5, 10, 15, 30
            daily: 1*
            weekly: 1*
            monthly: 1*
         endDate : str, optional
             End date as milliseconds since epoch. If startDate and endDate are provided, period should not be provided. Default is previous trading day.
         startDate : TYPE, optional
             Start date as milliseconds since epoch. If startDate and endDate are provided, period should not be provided.
         needExtendedHoursData : str, optional
             true to return extended hours data, false for regular market hours only. Default is true

         Returns
         -------
         dict

         help: https://developer.tdameritrade.com/price-history/apis/get/marketdata/%7Bsymbol%7D/pricehistory#
         """
         if self.authorization is None or time.time()-self.last_refresh_time>1800:
             self.refresh()
         payload={'apikey':self.consumer_key,
                  'periodType':periodType,
                  'period':period,
                  'frequencyType':frequencyType,
                  'frequency':frequency,
                  'endDate':endDate,
                  'startDate':startDate,
                  'needExtendedHoursData':needExtendedHoursData}
         
         headers={'Authorization':'Bearer '+self.authorization}
         
         url=self.api_url+self.mkt+'{}/pricehistory'.format(ticker)
         ret = requests.get(url,params=payload, headers=headers).json()
         
         if df:
             ret = pd.DataFrame(ret['candles'])
             ret['date'] = ret['datetime'].apply(lambda x: datetime.datetime.fromtimestamp(x/1000).strftime('%Y-%m-%d %H-%M'))
             ret = ret.drop(columns=['datetime'])
             

         return ret
             
             
     
     def getQuote(self,ticker):
         """
         help: https://developer.tdameritrade.com/quotes/apis/get/marketdata/%7Bsymbol%7D/quotes
         """
         if self.authorization is None or time.time()-self.last_refresh_time>1800:
             self.refresh()
         payload={'apikey':self.consumer_key}
         
         url=self.api_url+self.mkt+'{}/quotes'.format(ticker)
         

         return requests.get(url,params=payload).json()
     
     def getQuotes(self,ticker_list):
         """
         help: https://developer.tdameritrade.com/quotes/apis/get/marketdata/%7Bsymbol%7D/quotes
         """
         if self.authorization is None or time.time()-self.last_refresh_time>1800:
             self.refresh()
         tickers=''
         for ticker in ticker_list:
             tickers+=ticker+','
         tickers=tickers[:-1]     
        
             
         payload={'apikey':self.consumer_key,
                  'symbol':tickers}
         
         url=self.api_url+self.mkt+'/quotes'
         

         return requests.get(url,params=payload).json()
     
     def getPositions(self,fields=None):
         if self.authorization is None or time.time()-self.last_refresh_time>1800:
             self.refresh()
         url=self.api_url+'accounts/'+self.account_id
         payload={}
         if fields is not None:
             payload={'fields':fields}
         headers={'Authorization':'Bearer '+self.authorization}
         
         return requests.get(url,params=payload,headers=headers).json()
     
     def searchInstruments(self,symbol,projection):
         """
         Parameters
         ----------
         symbol : String
             Value to pass to the search.
         projection : TYPE
             The type of request:
                 symbol-search: Retrieve instrument data of a specific symbol or cusip
                 symbol-regex: Retrieve instrument data for all symbols matching regex. Example: symbol=XYZ.* will return all symbols beginning with XYZ
                 desc-search: Retrieve instrument data for instruments whose description contains the word supplied. Example: symbol=FakeCompany will return all instruments with FakeCompany in the description.
                 desc-regex: Search description with full regex support. Example: symbol=XYZ.[A-C] returns all instruments whose descriptions contain a word beginning with XYZ followed by a character A through C.
                 fundamental: Returns fundamental data for a single instrument specified by exact symbol.'
         Returns
         -------
         TYPE dict
             see https://developer.tdameritrade.com/instruments/apis/get/instruments

         """
         if self.authorization is None or time.time()-self.last_refresh_time>1800:
             self.refresh()
         
         url=self.api_url+'instruments/'
         payload={'apikey':self.consumer_key,
                  'symbol':symbol,
                  'projection':projection}
         headers={'Authorization':'Bearer '+self.authorization}
         
         return requests.get(url,params=payload,headers=headers).json()
     
     def getInstruments(self,cusip):
         if self.authorization is None or time.time()-self.last_refresh_time>1800:
             self.refresh()
         
         url=self.api_url+'instruments/'+cusip
         payload={'apikey':self.consumer_key}
         headers={'Authorization':'Bearer '+self.authorization}
         
         return requests.get(url,params=payload,headers=headers).json()
     
     def OptionChain(self, symbol, contractType='ALL', strikeCount=5, includeQuotes='TRUE', strategy='SINGLE', interval=None, strike=None, range_='ALL', fromDate=None, toDate=None, volatility=None, underlyingPrice=None, interestRate=None, daysToExpiration=None, expMonth='ALL', optionType='ALL'):
         """

         Parameters
         ----------
         symbol : str
             Enter one symbol.
         contractType : str, optional
             Type of contracts to return in the chain. Can be CALL, PUT, or ALL. The default is 'ALL'.
         strikeCount : int, optional
             The number of strikes to return above and below the at-the-money price.. The default is 5.
         includeQuotes : bool str, optional
             Include quotes for options in the option chain. Can be TRUE or FALSE. The default is 'TRUE'.
         strategy : str, optional
             Passing a value returns a Strategy Chain. Possible values are SINGLE, ANALYTICAL (allows use of the volatility, underlyingPrice, interestRate, and daysToExpiration params to calculate theoretical values), COVERED, VERTICAL, CALENDAR, STRANGLE, STRADDLE, BUTTERFLY, CONDOR, DIAGONAL, COLLAR, or ROLL. . The default is 'SINGLE'.
         interval : str, optional
             Strike interval for spread strategy chains (see strategy param). The default is None.
         strike : int, optional
             Provide a strike price to return options only at that strike price. The default is None.
         range_ : TYPE, optional
             Returns options for the given range. Possible values are:
             'ITM': In-the-money
             'NTM'': Near-the-money
             'OTM': Out-of-the-money
             'SAK': Strikes Above Market
             'SBK': Strikes Below Market
             'SNK': Strikes Near Market
             'ALL': All Strikes. 
             The default is 'ALL'.
         fromDate : TYPE, optional
             Only return expirations after this date. For strategies, expiration refers to the nearest term expiration in the strategy. Valid ISO-8601 formats are: yyyy-MM-dd and yyyy-MM-dd'T'HH:mm:ss. The default is None.
         toDate : TYPE, optional
             Only return expirations before this date. For strategies, expiration refers to the nearest term expiration in the strategy. Valid ISO-8601 formats are: yyyy-MM-dd and yyyy-MM-dd'T'HH:mm:ss. The default is None.
         volatility : TYPE, optional
             Volatility to use in calculations. Applies only to ANALYTICAL strategy chains (see strategy param). The default is None.
         underlyingPrice : TYPE, optional
             Underlying price to use in calculations. Applies only to ANALYTICAL strategy chains (see strategy param). The default is None.
         interestRate : TYPE, optional
             Interest rate to use in calculations. Applies only to ANALYTICAL strategy chains (see strategy param). The default is None.
         daysToExpiration : TYPE, optional
             Days to expiration to use in calculations. Applies only to ANALYTICAL strategy chains (see strategy param). The default is None.
         expMonth : TYPE, optional
             'Return only options expiring in the specified month. Month is given in the three character format. The default is 'ALL'.
         optionType : TYPE, optional
             'Type of contracts to return. Possible values are:

             S: Standard contracts
             NS: Non-standard contracts
             ALL: All contracts
             The default is 'ALL'.

         Returns
         -------
         a dict
         see https://developer.tdameritrade.com/option-chains/apis/get/marketdata/chains

         """
         if self.authorization is None or time.time()-self.last_refresh_time>1800:
             self.refresh()
         url=self.api_url+'marketdata/chains'
         payload = {'apikey':self.consumer_key,
                    'symbol':symbol,
                    'contractType':contractType,
                    'strikeCount':strikeCount,
                    'includeQuotes':includeQuotes,
                    'strategy':strategy,
                    'interval':interval,
                    'strike':strike,
                    'range':range_,
                    'fromDate':fromDate,
                    'toDate':toDate,
                    'volatility':volatility,
                    'underlyingPrice':underlyingPrice,
                    'interestRate':interestRate,
                    'daysToExpiration':daysToExpiration,
                    'expMonth':expMonth,
                    'optionType':expMonth}
         headers={'Authorization':'Bearer '+self.authorization}
         
         return requests.get(url,params=payload,headers=headers).json()

             
             
