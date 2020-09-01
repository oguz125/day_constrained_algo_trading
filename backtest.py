#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug  1 22:05:06 2020

@author: apolat
"""

from api import getData
import datetime
import pandas as pd
import statsmodels.formula.api as sm

class BackTest:
    
     def __init__(self, ticker_list, seed_money, start_date = 1592294400, build_database = False):
         self.gd = getData()
         self.portfolio = {ticker: {'S':[0,0],'C':[0,0],'P':[0,0]} for ticker in ticker_list}
         self.balance = seed_money
         self.cost_basis = pd.DataFrame(columns=['Ticker', 'Type', 'Quantity', 'Cost', 'Time', 'Cash'])
         if build_database:
             self.build_database(start_date)
         self.data = pd.read_csv('data.csv').drop(columns=['Unnamed: 0'])
         self.data['datetime'] = self.data['datetime'].apply(lambda x: datetime.datetime.strptime( x,"%Y-%m-%d %H:%M:%S"))
         
         
     def change_portfolio(self, ticker, type_, quantity, time):
         cost = self.quote(ticker, time)
         self.portfolio[ticker][type_][1] = (self.portfolio[ticker][type_][0]*self.portfolio[ticker][type_][1] + quantity*cost)/(self.portfolio[ticker][type_][0] + quantity)
         self.portfolio[ticker][type_][0] += quantity
         self.balance -= quantity * cost
         self.cost_basis.append({'Ticker':ticker,'Type':type_,'Quantity':quantity, 'Cost':cost, 'Time':time, 'Cash': self.balance}, ignore_index=True)
         
     def quote(self, ticker, time):
         return float(self.data[self.data['ticker']==ticker][self.data[self.data['ticker']==ticker]['datetime']==time]['close'])

     def time_to_epoch(self, time):
         if type(time) is not int:
             return int(datetime.datetime.strptime(time,"%Y-%m-%d %H:%M:%S").timestamp())
         else:
             return time
         
     def build_database(self, start_date):
         startDate = self.time_to_epoch(start_date)
         data = []
         for ticker in self.portfolio.keys():
             temp = self.gd.getPrice(ticker, frequency=5, startDate=startDate)['candles']
             for i in temp:
                 i['ticker'] = ticker
             data.extend(temp)
             del temp
         data = pd.DataFrame(data = data, columns = ['ticker','open','high','low','close','volume','datetime'])
         data['datetime'] = data['datetime'].apply(lambda x: datetime.datetime.fromtimestamp(x/1000))
         data.to_csv('data.csv')
       
     def day_data(self):
         self.data['day']=self.data['datetime'].apply(lambda x: x.date())
         day_data = {}
         for ticker in self.data['ticker'].unique():
             day_data[ticker] = self.data[self.data['ticker']=='MSFT'].groupby(['day']).mean()
             day_data[ticker]['volume'] = self.data[self.data['ticker']=='MSFT'].groupby(['day']).sum()['volume']
         self.data = self.data.drop(columns=['day'])
         return day_data
       
     def open_position(self, ticker, type_, quantity, day, lag_period = 1):
         time = datetime.datetime(day.year,day.month,day.day,15,60-lag_period*5,0)
         self.change_portfolio(ticker, type_, quantity, time)
     
     def stop_loss(self, rate = .9, time):
         for ticker in self.portfolio:
             if self.quote(ticker,time) < rate * self.portfolio['ticker']['S'][1]:
                 self.close_position(ticker, 'S', time)
     
     def close_position(self, ticker, type_, time):
         quantity = -self.portfolio[ticker]['S'][0]
         self.change_portfolio(ticker, type_, quantity, time)
         
           
         
          
         
     def SMA_regression(self, back_window=30, train_size = 100, ma_windows = [5,15,30]):
         if max(ma_windows)>back_window:
             raise('ma_windows should not exceed back_window')
         reg = {}
         day_data = self.day_data()
         formula = 'day_change ~ close + volume'
         for i in ma_windows:
             formula += ' + ''open'+str(i)+'ma + '+'close'+str(i)+'ma + '+'volume'+str(i)+'ma'
         for key in day_data.keys():
             for i in ma_windows:
                 day_data[key]['open'+str(i)+'ma'] = day_data[key]['open'].rolling(i).mean()
                 day_data[key]['close'+str(i)+'ma'] = day_data[key]['close'].rolling(i).mean()
                 day_data[key]['volume'+str(i)+'ma'] = day_data[key]['volume'].rolling(i).mean()
             day_data[key]['day_change'] = day_data[key]['close'].diff().shift(-1)
             day_data[key]['day_change_std'] = day_data[key]['close'].diff().shift(-1).rolling(30).std()
             day_data[key] = day_data[key].dropna(how='any')
             reg[key] = sm.ols(formula = formula, data = day_data[key].iloc[:train_size]).fit()
             
            
         return reg
        

         

         
         
    
         