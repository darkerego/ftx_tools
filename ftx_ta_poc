#!/usr/bin/env python3.8
import datetime
import random
import sys

import requests
from colored import fg, attr, bg
import numpy as np
import talib
from utils import sql_lib
from utils.colorprinter import ColorPrint





class CurrentSig:
    current_analysis = {
        'signal': {'signal': 'NEUTRAL', 'status': None, 'instrument': None, 'open_time': 0.0, 'Entry': 0.0, 'Exit': 0.0,
                   'closed_at': 0.0}}
    sql = sql_lib.SQLLiteConnection()

    def __get__(self):
        return self.current_analysis

    def __update__(self, data):
        self.current_analysis = data

    def __record__(self, datadict):
        self.sql.append(value=datadict, table='signals')


class Strategy:
    """
    Simple Framework For Analyzing FTX Candle Data
    """

    def __init__(self, market, periods=None, min_score=10, quiet=False):
        if periods is None:
            periods = [15, 60, 300, 900, 3600, 14400, 86400]
        self.market = market
        self.periods = periods
        self.min_score = min_score
        self.indicators = ['sar', 'macd', 'ema_cross']
        self.quiet = quiet
        self.cp = ColorPrint(quiet=self.quiet)
        self.sig = CurrentSig()


    def _print(self, data):
        if self.quiet:
            pass
        else:
            print(data)

    def spot_ticker(self, market):
        ret = requests.get(f'https://ftx.com/api/markets/{market}').json()
        return ret['result']['price']

    def future_ticker(self, market):
        ret = requests.get(f'https://ftx.com/api/futures/{market}').json()
        return ret['result']['mark']

    def weighted_std(self, values, weights):
        sum_of_weights = np.sum(weights)
        weighted_average = np.sum(values * weights) / sum_of_weights
        n = len(weights)
        numerator = np.sum(n * weights * (values - weighted_average) ** 2.0)
        denominator = (n - 1) * sum_of_weights
        weighted_std = np.sqrt(numerator / denominator)
        return weighted_std

    def calcweightedavg(self, data, weights):
        import pandas as pd
        import numpy as np
        # X is the dataset, as a Pandas' DataFrame
        mean = np.ma.average(data, axis=0,
                             weights=weights)  # Computing the weighted sample mean (fast, efficient and precise)

        # Convert to a Pandas' Series (it's just aesthetic and more
        # ergonomic; no difference in computed values)
        mean = pd.Series(mean, index=list(data.keys()))
        xm = data - mean  # xm = X diff to mean
        xm = xm.fillna(
            0)  # fill NaN with 0 (because anyway a variance of 0 is just void, but at least it keeps the other covariance's values computed correctly))
        sigma2 = 1. / (weights.sum() - 1) * xm.mul(weights, axis=0).T.dot(
            xm)  # Compute the unbiased weighted sample covariance

    def average(self, numbers):
        total = sum(numbers)
        total = float(total)
        total /= len(numbers)
        return total

    def variance(self, data, ddof=0):
        n = len(data)
        mean = sum(data) / n
        return sum((x - mean) ** 2 for x in data) / (n - ddof)

    def stdev(self, data):
        import math
        var = self.variance(data)
        std_dev = math.sqrt(var)
        return std_dev

    def moving_average(self, df, n):
        """Calculate the moving average for the given data.

        :param df: pandas.DataFrame
        :param n:
        :return: pandas.DataFrame
        """
        MA = talib.MA(df, n, matype=0)
        return MA[-1]

    def balance_of_power(self, df, n):
        BOP = talib.BOP(df, n)
        return BOP[-1]

    def exponential_moving_average(self, df, n):
        """

        :param df: pandas.DataFrame
        :param n:
        :return: pandas.DataFrame
        """
        EMA = talib.EMA(df, timeperiod=n)
        return EMA[-1]

    def generate_sar(self, high_array, low_array, acceleration=0.05, maximum=0.2):
        sar = talib.SAR(high_array, low_array, acceleration=acceleration, maximum=maximum)
        ticker = (self.future_ticker(self.market))
        sar = (sar[-3])
        if sar < ticker:
            # under candle, is long
            return 1, ticker, sar
        if sar > ticker:
            # above candle, is short
            return -1, ticker, sar

    def generate_macd(self, close_array, new_time):
        macd, macdsignal, macdhist = talib.MACD(close_array, fastperiod=12, slowperiod=26, signalperiod=9)

        crosses = []
        macdabove = False
        for i in range(len(macd)):
            if np.isnan(macd[i]) or np.isnan(macdsignal[i]):
                pass
            else:
                if macd[i] > macdsignal[i]:
                    if macdabove == False:
                        macdabove = True
                        cross = [new_time[i], macd[i], 'go']
                        crosses.append(cross)
                else:
                    if macdabove == True:
                        macdabove = False
                        cross = [new_time[i], macd[i], 'ro']
                        crosses.append(cross)
        if macdabove:
            return crosses[-1:], 1
        else:
            return crosses[-1:], -1

    def get_ohlcv(self, symbol, period=None):
        """
        Periods in number of seconds:
        15s, 1m,  5m,  15m,  1h,   4h,   1d
        15, 60, 300, 900, 3600, 14400, 86400
        0.01736111111111111 %, 0.06944444444444445 %  0.3472222222222222 % 1.0416666666666665% 4.166666666666666% 16.666666666666664 % 77%
        """
        _close_array = []
        _high_array = []
        _low_array = []
        _open_time_array = []
        _open_array = []

        _volume_array = []

        # candles = api.ftx_api.fetchOHLCV(symbol=symbol, timeframe=period)
        if period is not None:
            # candles = api.ftx_api.fetchOHLCV(symbol=symbol, timeframe=period)
            _candles = requests.get(f'https://ftx.com/api/markets/{symbol}/candles?resolution={period}')
            # print(_candles.json())
            for c in _candles.json()['result']:
                _close_array.append(c['close'])
                _open_array.append(c['open'])
                _high_array.append(c['high'])
                _low_array.append(c['low'])
                _volume_array.append(['volume'])
                _open_time_array.append(c['time'])
            high_array = np.asarray(_high_array)
            low_array = np.asarray(_low_array)
            close_array = np.asarray(_close_array)
            volume_array = np.asarray(_volume_array)
            open_array = np.asarray(_open_array)
            new_time = [datetime.datetime.fromtimestamp(time / 1000) for time in _open_time_array]
            return open_array, close_array, high_array, low_array, volume_array, new_time

    def get_change(self, current, previous):
        if current == previous:
            return 0
        try:
            return (abs(current - previous) / previous) * 100.0
        except ZeroDivisionError:
            return float('inf')

    def score(self, _period):
        """
        Turn FTX intervals into human friendly time periods
        """
        to_human_format = _period / 60
        if float(to_human_format) >= 60:
            to_human_format = to_human_format / 60
            period_str = f'{to_human_format}h'
        elif float(to_human_format) < 1:
            period_str = f'{to_human_format}m'
        elif float(to_human_format) < 60 > 1:
            period_str = f'{to_human_format}m'
        else:
            return False
        self._print(f'Analysis on {period_str}')

        long_score = 0
        short_score = 0
        open_array, close_array, high_array, low_array, volume_array, new_time = self.get_ohlcv(symbol=self.market,
                                                                                                period=_period)
        macdret, rogo = self.generate_macd(close_array, new_time)

        # print('MACD:', macdret, rogo)
        if rogo == 1:
            long_score += 1
        elif rogo == -1:
            short_score += 1
        sar = self.generate_sar(high_array, low_array)
        if not sar:
            return False
        if sar[0] == 1:
            long_score += 1
        elif sar[0] == -1:
            short_score += 1
        s = self.stdev(close_array)
        self._print(('Standard Devation:', s))
        ema_long = self.exponential_moving_average(close_array, n=26)
        ema_short = self.exponential_moving_average(close_array, n=9)
        if ema_short > ema_long:
            long_score += 1
        if ema_short < ema_long:
            short_score += 1
        self._print((f'Analysis for {_period}:', long_score, short_score))
        return long_score, short_score

    def calculate_score(self):
        analysis = ''
        total_score = 0
        weighted_score = 0
        highest_score = 0

        for i in self.periods:
            highest_score += (i * len(self.indicators))

        for period in self.periods:
            long_score, short_score = self.score(period)
            if long_score > short_score:
                total_score += 1
            elif short_score > long_score:
                total_score -= 1
            self._print(('Non weighed score:', total_score))
            weighted = (total_score * period)
            weighted_score += weighted
            self.cp.yellow(f'Weighted Score: {weighted} for {period}, total: {weighted_score}')
        weighted_score = weighted_score / len(self.periods)
        score_pct = 1 / (highest_score / weighted_score) * 100
        self.cp.red(f'Weighted Score: {weighted_score} / Highest Possible: {highest_score} ')

        self.cp.random_color(data='Calculating weighted score!', static_set='bright')
        if weighted_score > 0:
            analysis = 'LONG'
            self.cp.green(f'Finished: score: {analysis}, Percent: {score_pct}')

        elif weighted_score < 0:
            analysis = 'SHORT'
            self.cp.red(f'Finished: score: {analysis}, Percent: {score_pct}')

        elif weighted_score == 0:
            analysis = 'NEUTRAL'
            self.cp.yellow(f'Finished: score: {analysis}')
            score_pct = 0
        self.forward_tester(signal=analysis)
        return analysis, score_pct

    def forward_tester(self, signal):
        """
        {'signal': {'signal': 'NEUTRAL', 'status': None, 'instrument': None, 'open_time': 0.0, 'Entry': 0.0, 'Exit': 0.0, 'closed_at': 0.0}}
        """
        ts = str(datetime.datetime.utcnow())
        current_tick = self.future_ticker(self.market)
        last_sig = self.sig.__get__()

        if last_sig.get('signal').get('signal') != signal:
            self._print(('Signal Closed!'))
            ot = self.sig.__get__().get('signal').get('open_time')
            entry = self.sig.__get__().get('signal').get('Entry')

            self._print((f"Signal {last_sig.get('signal').get('signal')} closed, {signal} now!"))
            self.sig.__record__(
                {'signal': signal, 'status': 'closed', 'instrument': self.market, 'open_time': ot, 'Entry': entry,
                 'Exit': current_tick,
                 'closed_at': ts})
            self.sig.__update__({'signal': {'signal': signal, 'status': 'open', 'instrument': self.market,
                                            'open_time': ts, 'Entry': current_tick, 'Exit': 0.0,
                                            'closed_at': 0.0}})
            self._print((self.sig.__get__()))
        else:
            self._print(('Signal Open!'))
            current = current_tick
            last = self.sig.__get__().get('signal').get('Entry')
            diff = self.get_change(current, last)

            if last_sig.get('signal').get('signal') == 'LONG':
                if current < last:
                    diff = diff * -1
            if last_sig.get('signal').get('signal') == 'SHORT':
                if current > last:
                    diff = diff * -1
            self.cp.white(f'Current Ticker: {current}, Price at open: {last}, PNL if closed now: {diff} %')
            self._print((self.sig.__get__()))
            pass


def main():
    cp = ColorPrint()
    cp.white('If you like this code, then use my FTX referal: https://ftx.com/#a=darkerego , thank you!')
    market = sys.argv[1]
    print('Market', market)

    strategy = Strategy(market, periods=[300, 900, 3600, 14400], quiet=False)
    while 1:
        try:
            signal_, score = strategy.calculate_score()
        except Exception as fuck:
            cp.alert(f"{['errored out']}, {fuck}")
        else:
            print('Updating ....')


if __name__ == '__main__':
    main()
