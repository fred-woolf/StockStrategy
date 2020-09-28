
import pandas as pd
import numpy as np

def moving_average(df, num):
    """Calculate the moving average for the given data.

    :param num: int number of days to calculate moving average
    :param ma: series which has the moving average data
    """
    ma = pd.Series(df['Close'].rolling(num, min_periods=num).mean(), name='MA_' + str(num))
    df = pd.DataFrame(ma)
    return df

def stochastic_oscillator_k(df, n):
    """Calculate stochastic oscillator %K for given data.

    :param highest_high_over_lookback: list which has max value over the specified lookback range
    :param pd_highest_high_over_lookback: pandas series from highest_high_over_lookback
    :param lowest_low_over_loopback: list which has min value over the specified lookback range
    :param pd_lowest_low_over_lookback: pandas series from lowest_low_over_loopback

    """

    highest_high_over_lookback = [np.NaN  for x in range(0, len(df["Close"]))]
    for i in range(0, len(df["Close"]) - n ):
        high_val = df["Close"][i:i+n].max()
        highest_high_over_lookback[i+n-1] = high_val

    pd_highest_high_over_lookback = pd.Series(highest_high_over_lookback)

    lowest_low_over_loopback = [np.NaN for x in range(0, len(df["Close"]))]

    for i in range(0, len(df["Close"]) - n):
        low_val = df["Close"][i:i + n].min()
        lowest_low_over_loopback[i + n-1] = low_val

    pd_lowest_low_over_lookback = pd.Series(lowest_low_over_loopback)

    return ((df["Close"] - pd_lowest_low_over_lookback)/(pd_highest_high_over_lookback - pd_lowest_low_over_lookback)) * 100

def stochastic_oscillator_d(df, n, smoothing):
    """Calculate stochastic oscillator %D for given data.

    :param stoch_osc_k dataframe: with stochastics osc %k to use in average %d calculation

    """
    stoch_osc_k = stochastic_oscillator_k(df, n)
    return stoch_osc_k.rolling(n, min_periods=n).mean()

def macd(df, n_fast, n_slow):
    """Calculate MACD, MACD Signal and MACD difference

    :param n_fast: int
    :param n_slow: int

    """
    ema_fast = pd.Series(df['Close'].ewm(span=n_fast, min_periods=n_slow).mean())
    ema_slow = pd.Series(df['Close'].ewm(span=n_slow, min_periods=n_slow).mean())
    _macd = pd.Series(ema_fast - ema_slow, name='MACD_' + str(n_fast) + '_' + str(n_slow))
    macd_sign = pd.Series(_macd.ewm(span=9, min_periods=9).mean(), name='MACDsign_' + str(n_fast) + '_' + str(n_slow))
    macd_diff = pd.Series(_macd - macd_sign, name='MACDdiff_' + str(n_fast) + '_' + str(n_slow))

    df = pd.DataFrame(_macd)
    df = df.join(macd_sign)
    df = df.join(macd_diff)
    return df

def set_williams_scale(x):
    """ Set scaling for Williams %R """
    if x != 0.0 and x != -1.0:
        x = x * (-100)
        if x < -100:
            x = -100
        if x > 0:
            x  = 0
    return x

def williams_R(df, n):
    """ calculate Williams %R
        :param n: int
        :param %R: series
        :param highest_high_over_lookback: list which has max value over the specified lookback range
        :param pd_highest_high_over_lookback: pandas series from highest_high_over_lookback
        :param lowest_low_over_loopback: list which has min value over the specified lookback range
        :param pd_lowest_low_over_lookback: pandas series from lowest_low_over_loopback
    """

    # formula:
    #   param n = number of days lookback
    #   %R = (Highest High - Close) / (Highest High - Lowest Low) * -100
    #   highest high over the lookback period
    #  consider adapting data from stochastics calculation

    highest_high_over_lookback = [np.NaN  for x in range(0, len(df["Close"]))]
    for i in range(0, len(df["Close"]) - n ):
        high_val = df["Close"][i:i+n].max()
        highest_high_over_lookback[i+n] = high_val

    pd_highest_high_over_lookback = pd.Series(highest_high_over_lookback)

    lowest_low_over_loopback = [np.NaN for x in range(0, len(df["Close"]))]
    for i in range(0, len(df["Close"]) - n):
        low_val = df["Close"][i:i + n].min()
        lowest_low_over_loopback[i + n] = low_val

    pd_lowest_low_over_lookback = pd.Series(lowest_low_over_loopback)

    R = (pd_highest_high_over_lookback - df["Close"][:]) / (pd_highest_high_over_lookback - pd_lowest_low_over_lookback)
    f = lambda x: set_williams_scale(x)
    R = [f(x) for x in R]
    R = pd.Series(R)
    return R

def momentum(df, n):
    """ Calcualate momentum
        :param n number of days lookback
        :param mo is momentum for the given lookback
    """
    mo = []
    for index, row in df.iterrows():
        if index > n:
            mo.append((df["Close"][index]) - (df["Close"][index - n]))
        else:
            mo.append(0)

    return pd.Series(mo)
