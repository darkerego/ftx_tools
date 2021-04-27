#!/usr/bin/env python3.8
import requests

from engine.api_ccxt import ApiFunctions as api
api = api()
from utils.color import NewColorPrint
cp = NewColorPrint()
import argparse
import numpy as np
from statsmodels.stats.weightstats import DescrStatsW

def weighted_std(values, weights):
    # For simplicity, assume len(values) == len(weights)
    # assume all weights > 0
    sum_of_weights = np.sum(weights)
    weighted_average = np.sum(values * weights) / sum_of_weights
    n = len(weights)
    numerator = np.sum(n * weights * (values - weighted_average) ** 2.0)
    denominator = (n - 1) * sum_of_weights
    weighted_std = np.sqrt(numerator / denominator)
    return weighted_std


def calcweightedavg(data, weights):
    import pandas as pd
    import numpy as np
    # X is the dataset, as a Pandas' DataFrame
    mean = np.ma.average(data, axis=0, weights=weights) # Computing the weighted sample mean (fast, efficient and precise)

    # Convert to a Pandas' Series (it's just aesthetic and more
    # ergonomic; no difference in computed values)
    mean = pd.Series(mean, index=list(data.keys()))
    xm = data-mean # xm = X diff to mean
    xm = xm.fillna(0) # fill NaN with 0 (because anyway a variance of 0 is just void, but at least it keeps the other covariance's values computed correctly))
    sigma2 = 1./(weights.sum()-1) * xm.mul(weights, axis=0).T.dot(xm) # Compute the unbiased weighted sample covariance

# Add your function below!
def average(numbers):
    total = sum(numbers)
    total = float(total)
    total /= len(numbers)
    return total

def variance( data, ddof=0):
    n = len(data)
    mean = sum(data) / n
    return sum((x - mean) ** 2 for x in data) / (n - ddof)

def stdev(data):
    import math
    var = variance(data)
    std_dev = math.sqrt(var)
    return std_dev

def get_ohlcv(symbol):
    """
    Periods in number of seconds:
    15s, 1m,  5m,  15m,  1h,   4h,   1d
    15, 60, 300, 900, 3600, 14400, 86400
    0.01736111111111111 %, 0.06944444444444445 %  0.3472222222222222 % 1.0416666666666665% 4.166666666666666% 16.666666666666664 % 77%


    """
    candle_dict = []
    std_dict = []
    std_periods = []
    period_list = [15, 60, 300, 900, 3600, 14400, 86400]

    # candles = api.ftx_api.fetchOHLCV(symbol=symbol, timeframe=period)
    for p in period_list:
        close_array = []
        _candles = requests.get(f'https://ftx.com/api/markets/{symbol}/candles?resolution={p}')
        if _candles.status_code != 200:
            cp.red(f'HTTP Status Code: {_candles.status_code}')
        if args.verbosity >= 2:
            if _candles.json()['success']:
                print('Success...')
        for c in _candles.json()['result']:
            close_array.append(c['close'])
        candle_dict.append((p, _candles.json()))
        # close_array = [float(entry[5]) for entry in _candles.json()['result']]
        close_array = np.asarray(close_array)
        std_dev = stdev(close_array)
        std_dict.append(std_dev)
        std_periods.append((std_dev, p))
        if args.verbosity >= 1:
            print(f'Aggravating data for period: {p}')
        for _ in _candles:
            timestamp = _[0]
            high = _[1]
            low = _[2]
            try:
                close = _[3]
            except IndexError:
                close = 0
            volume = _[4]
            candle_dict.append(f'{{"peroid":{p} "timestamp": {timestamp},"high": {high}, "low":{low}, "close":{close},'
                               f' "volume":{volume}}}')
    if args.verbosity > 3:
        for i in candle_dict:
             cp.random_color(i)
    std_dict = np.asarray(std_dict)
    cp.blue(f'Stdev by periods (timeframes in # of seconds): {std_periods}')
    weights = [0.017361111111111112, 0.06944444444444445, 0.3472222222222222, 1.0416666666666665, 4.166666666666666, 16.666666666666664, 77]
    weighted_stats = DescrStatsW(std_dict, weights=np.asarray(weights), ddof=0)
    cp.purple(f'Weighted Statistical Standard Deviation: {weighted_stats.std}')
    cp.yellow(f'Weighted Statistical Variance: {weighted_stats.var}')
    cp.red(f'Weighted Statistical Standard Error: {weighted_stats.std_mean}')
    cp.green(f'Weighted Statistical Mean: {weighted_stats.mean}')





def main():
    global args
    args = argparse.ArgumentParser()
    args.add_argument('-s', '--symbol', dest='symbol', type=str, help='Market to fetch. Ex: BTC-PERP')
    args.add_argument('-p', '--period', dest='period', type=str, help='Time period to fetch. Ex: 1m, 5m,'
                                                            ' 15m, 30m, 1h, 2h, 4h, 1d')
    args.add_argument('-v', '--verbose', dest='verbosity', action='count', default=0, help='Verbosity (-vvv)')

    args = args.parse_args()
    print(args.verbosity)
    get_ohlcv(args.symbol)


if __name__ == '__main__':
    main()
