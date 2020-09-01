# A Day Trading Constrained Low Frequency Trading Algorithm

Day Trading constraints prevents retail investors from opening and closing positions within the same day. As a result, retail investors have to carry their positions overnight. This shouldn't, however, discourage the retail investors to exploit statistical models. Here, I utilize a couple of statistical models and measure their performances under the day trading constraints.

The algorithm uses the price and volume data to predict next day return. Given the prediction, it opens positions at market close. The positions are closed next day if they hit a stop loss or target level intraday. If a position survives until the market close, it either is rolled over to next day or closed in favor of another asset based on the updated predictions.

## api.py
Implements TD Ameritrade API.

## options_saver.py
As the TD Ameritrade API, along with most other inexpensive data resources, does not provide historical option price data, this tool saves the current day option prices which can be used to create a database of historical option prices.

## backtest.py
Implements a backtesting environment for the algorithm and an implementation of the algorithm. 

## Sample Files
05-31.csv is a sample output for options_saver.py which documents the option chains of selected tickers on 31 May 2020. data.csv contains the pricing and volume data in 5 minutes frequency for selected tickers that is used in the backtesting.



