# -*- coding: utf-8 -*-
"""
This files contains the code to create the matrix to train the models
@author: Pablo Calderon
@date: 20171101
"""
import pandas as pd
import numpy as np
from scipy import signal

#==============================================================================
# Reading and plotting stock data
#==============================================================================
# Imports the data from csv file
eurusd_data = pd.read_csv("data/EURUSD_hourly.csv", index_col="date_time", parse_dates=True,
                         delimiter=",", na_values="null")

# Remove lines with null (NaN)
eurusd_data = eurusd_data.dropna()

# Checks data integrity: We check consecutive hours
eurusd_index = eurusd_data.index

ok_counter = 0
nok_counter = 0
for i in range(0, eurusd_index.shape[0]-1):
    idx1 = eurusd_index[i]
    idx2 = eurusd_index[i+1]
    if((idx2.hour - idx1.hour) == 1):
        # Consecutive hours: ok
        #print("{}={}".format(i, idx1))
        ok_counter = ok_counter+1
    elif((idx1.hour == 23) & (idx2.hour == 0) & ((idx2.day-idx1.day) == 1) ):
        # Day change from 23:00 to 0:00
        #print("dc{}={}".format(i, idx1))
        ok_counter = ok_counter+1
        
    elif((idx1.hour == 23) & (idx2.hour == 0) & (idx2.day == 1) & ((idx2.month-idx1.month) == 1) ):
        # Month change
        #print("mc{}={}".format(i, idx1))
        ok_counter = ok_counter+1
    elif( (idx1.isoweekday() == 5) & (idx2.isoweekday() == 7) & (abs(idx2.hour - idx1.hour) <= 2)):
        # Week-end (isoweekday: Monday is 1 and Sunday is 7)
        # Including daylight savings: spring forward hour change ((idx2.hour - idx1.hour) == 2) & (idx1.month == 11)
        #                       autumn fall backward hour change ((idx2.hour - idx1.hour) == 0) & (idx1.month == 3)
        #print("we{}={}".format(i, idx1))
        ok_counter = ok_counter+1
    elif( (idx1.day == 25) & (idx1.month == 12) ):
        # Christmash day
        #print("ch{}={}".format(i, idx1))
        ok_counter = ok_counter+1
    elif( (idx1.day == 31) & (idx1.month == 12) & (idx2.day == 1) & (idx2.month == 1)):
        # New year's day
        #print("ny{}={}".format(i, idx1))
        ok_counter = ok_counter+1
    else:
        nok_counter = nok_counter+1
        print("------- Error:{} -------".format(nok_counter))
        print("{}={}".format(i, idx1))
        print("{}={}".format(i+1, idx2))
        #break
print("{}/{} errors in data".format(nok_counter, ok_counter))

# Creates the range index
dates = pd.date_range("2003-12-01", "2017-12-31", freq="H")
#dates = pd.date_range("2003-05-04", "2015-06-03", freq="H")
# Create an empty dataframe
eurusd_df = pd.DataFrame(index=dates)
# Adds the eurusd data (inner join)
eurusd_df = eurusd_df.join(eurusd_data, how="inner")

# Creates the dataframe for the long deals matrix inputs
long_df = pd.DataFrame(index=eurusd_df.index)
# Creates the dataframe for the Short deals matrix inputs
short_df = pd.DataFrame(index=eurusd_df.index)

# Remove working variables
del dates, i, idx1, idx2, nok_counter, ok_counter, eurusd_index

#==============================================================================
# Calculates the SMA (Simple Moving Average)
#==============================================================================
def calc_sma(data, size=5):
    """ This funciton calculates the Simple Moving Average (SMA)
    @data: DataFrame column with data to calculate the SMA
    @size: number of periods to calculate the SMA
    """
    return data.rolling(size, min_periods=1).sum()/size

# Define the sma sizes
sma_sizes = [5, 18, 45]

# Loop to calculate the SMA's
for n in sma_sizes:
    long_df["ask_sma{}".format(n)] = calc_sma(eurusd_df["ask_close"], n)
    short_df["bid_sma{}".format(n)] = calc_sma(eurusd_df["bid_close"], n)

# Remove working variables
del sma_sizes, n

#==============================================================================
# Calculates the Exponential Moving Average
#==============================================================================
def calc_ema(values, emaSize):
    """ Calculates the Exponential Moving Average (EMA)
    This method with the scipy signal funciton is faster compared to standard loop
    @data: DataFrame column with data to calculate the ema
    @emaSize: size of the ema to be calculated
    """
    # Calculates the alfa
    alpha = 2./ (emaSize + 1)
    a = np.array([1, alpha - 1.])
    b = np.array([alpha])
    zi = signal.lfilter_zi(b, a)
    ema, _ = signal.lfilter(b, a, values, zi=zi)
    return ema

# This is the standard loop method to calculate the EMA
# The loop requires much more time than the previous method
def calc_ema2(data, emaSize):
    """ Calculates the Exponential Moving Average (EMA)
    @data: DataFrame column with data to calculate the ema
    @emaSize: size of the ema to be calculated
    """
    ema = data
    # Calculates the alfa
    alfa = 2. / (emaSize + 1.);
    alfa_m = 1. - alfa
    data_alfa = data * alfa
    # Loop to go through the data an calculate EMAs
    for i in range(1, data.shape[0]):
        # Calculates the EMA
#        ema[i] = ema[i-1] + alfa * (data[i] - ema[i-1]);
        ema[i] = ema[i-1] * alfa_m + data_alfa[i];
    ema("ema{}".format(emaSize))
    return ema

# Define the ema sizes
ema_sizes = [5, 18, 45]

# Loop to calculate the EMA's
for n in ema_sizes:
    long_df["ask_ema{}".format(n)] = calc_ema(eurusd_df["ask_close"], n)
    short_df["bid_ema{}".format(n)] = calc_ema(eurusd_df["bid_close"], n)

# Remove working variables
del ema_sizes, n

#==============================================================================
# Calculates the ATR (Average True Range column of the data)
# Ref: https://en.wikipedia.org/wiki/Average_true_range
#==============================================================================
def calc_tr(data):
    """ Calculates the TR (True Range column of the data)
    Ref: https://en.wikipedia.org/wiki/Average_true_range
    @data: DataFrame with three columns named as: "high", "low", "close"
    @return: tr
    """
    # Creates the data frame
    tr_data = pd.DataFrame()
    # Calculates high to low column
    tr_data["high_low"] = data["high"] - data["low"]
    # Calculates high to close column
    tr_data["high_close"] = (data["high"] - data["close"].shift(1)).abs()
    # Calculates close to low column
    tr_data["close_low"] = (data["close"].shift(1) - data["low"]).abs()
    # Calculates true range column
    tr_data["tr"] = tr_data.max(axis=1)
    return tr_data

# Creates the DataFrame with ask columns to calculate True Range
data_ask_tr = eurusd_df.loc[:,["ask_high", "ask_low", "ask_close"]]
# Rename the columns for calc_tr function
data_ask_tr.columns = ["high", "low", "close"]
# Calculate True Range fir ask
data_ask_tr = calc_tr(data_ask_tr)

# Creates the DataFrame with bid columns to calculate True Range
data_bid_tr = eurusd_df.loc[:,["bid_high", "bid_low", "bid_close"]]
# Rename the columns for calc_tr function
data_bid_tr.columns = ["high", "low", "close"]
# Calculate True Range for bid
data_bid_tr = calc_tr(data_bid_tr)

# atr_size number of values to calculate the ATR. Must be bigger than 2. Wilder used 14 periods originally.
atr_sizes = [14]

# Loop to calculate the ATR's
for n in atr_sizes:
    data_ask_tr["ask_atr{}".format(n)] = calc_ema(data_ask_tr["tr"], emaSize=n)
    data_bid_tr["bid_atr{}".format(n)] = calc_ema(data_bid_tr["tr"], emaSize=n)
    # Use ATR with factor K 1e4 to convert price to pips and avoid too much decimals
    long_df["ask_atr{}".format(n)] = data_ask_tr["ask_atr{}".format(n)] * 1e4
    short_df["bid_atr{}".format(n)] = data_bid_tr["bid_atr{}".format(n)] * 1e4

# Remove working variables
del atr_sizes, data_ask_tr, data_bid_tr, n

#==============================================================================
# Calculates the MACD (moving average convergence/divergence)
# Ref: https://en.wikipedia.org/wiki/MACD
#==============================================================================
def calc_macd(data, emaFast=12, emaSlow=26, macdSize=9):
    """ Calculates the Moving Average Convergence/Divergence (MACD)
    The MACD is the ema of (ema fast - ema slow)
    Ref: https://en.wikipedia.org/wiki/MACD
    @data: DataFrame column with data to calculate the macd
    @emaFast: number of periods to calculate the EMA fast (typical value is 12)
    @emaSlow: number of periods to calculate the EMA slow (typical value is 26)
    @macdSize: number of periods to calculate the MACD (typical value is 9)
    """
    # Copy data into DataFrame
    macd_data = pd.DataFrame(data)
    # Calculates fast ema
    macd_data["ema_fast"] = calc_ema(data, emaFast)
    # Calculates slow ema
    macd_data["ema_slow"] = calc_ema(data, emaSlow)
    # Calculates ema_fast - ema_slow
    macd_data["fast_slow"] = macd_data["ema_fast"] - macd_data["ema_slow"]
    # Calculates macd
    macd_data["macd{}".format(macdSize)] = calc_ema(macd_data["fast_slow"], macdSize)
    
    return macd_data["macd{}".format(macdSize)]

# Define the MACD sizes
macd_sizes = [9]

# Loop to calculate the MACD's
for n in macd_sizes:
    # Use MACD with factor K 1e4 to convert price to pips and avoid too much decimals
    long_df["ask_macd{}".format(n)] = calc_macd(eurusd_df["ask_close"], macdSize=n) * 1e4
    short_df["bid_macd{}".format(n)] = calc_macd(eurusd_df["bid_close"], macdSize=n * 1e4)

# Remove working variables
del macd_sizes, n

#==============================================================================
# Calculates the RSI (relative strength index)
# Ref: https://en.wikipedia.org/wiki/Relative_strength_index
#==============================================================================
def calc_rsi(data, rsiSize=14):
    """ Calculates the Relative Strength Index indicator (RSI)
    Ref: https://en.wikipedia.org/wiki/Relative_strength_index
    @data: DataFrame column with data to calculate the rsi
    @rsiSize: rsiSize number of periods to calculate the RSI (typical value is 14)
    """
    data = eurusd_df["ask_close"]
    rsiSize=14
    # Copy data into DataFrame
    rsi_data = pd.DataFrame(data)
    # Calculates RSI Upward values
    rsi_data["rsi_up"] = data - data.shift(1)
    rsi_data["rsi_up"][rsi_data["rsi_up"]<0] = 0
    # Calculates RSI Upward values
    rsi_data["rsi_down"] = data.shift(1) - data
    rsi_data["rsi_down"][rsi_data["rsi_down"]<0] = 0
    
    # Remove NaN
    rsi_data = rsi_data.fillna(0.)
    
    # Calculates ema of the rsi upward
    rsi_data["rsi_up_ema"] = calc_ema(rsi_data["rsi_up"], rsiSize)
    # Calculates ema of the rsi downward
    rsi_data["rsi_down_ema"] = calc_ema(rsi_data["rsi_down"], rsiSize)
    
    # Calculates RSI
    rsi_data["rsi_RS"] = rsi_data["rsi_up_ema"] / rsi_data["rsi_down_ema"];
    rsi_data["rsi"] = (100. - 100. / (1. + rsi_data["rsi_RS"]));

    # Replace NaN with RSI=100
    rsi_data = rsi_data.fillna(100)
    # Return RSI
    return rsi_data["rsi"]

# Define the MACD sizes
rsi_sizes = [14]

# Loop to calculate the RSI's
for n in rsi_sizes:
    long_df["ask_rsi{}".format(n)] = calc_rsi(eurusd_df["ask_close"], rsiSize=n)
    short_df["bid_rsi{}".format(n)] = calc_rsi(eurusd_df["bid_close"], rsiSize=n)

# Remove working variables
del rsi_sizes, n

#==============================================================================
# Calculates the BB (Bollinger Bands)
# Ref: https://en.wikipedia.org/wiki/Bollinger_Bands
#==============================================================================
def calc_bb(data, bbSize=20, k_sigma=2):
    """ Calculates the Bollinger Bands ratio column of the data
    Ref: https://en.wikipedia.org/wiki/Bollinger_Bands
    @data: DataFrame column with data to calculate the bollinger bands
    @bbSize: number of values to calculate the BB. Must be bigger than 2. John Bollinger used 20 periods originally.
    @k_sigma: value for the k factor applied to sigma to calculate the Bollinger Bands
    """
    
#    data = eurusd_df["ask_close"]
#    bbSize=20
#    k_sigma=2
    # Copy data into DataFrame
    bb_data = pd.DataFrame(data)
    # Calculates SMA
    bb_data["bb_sma"] = calc_sma(data, bbSize)
    # Calculates the standard deviation of the sma values
    # Delta Degrees of Freedom. The divisor used in calculations is N - ddof, where N represents the number of elements
    bb_data["bb_smaStd"] = bb_data["bb_sma"].rolling(bbSize, min_periods=1).std(ddof=0)
    
    bb_data["upperBand"] = bb_data["bb_sma"] + k_sigma * bb_data["bb_smaStd"];
    bb_data["lowerBand"] = bb_data["bb_sma"] - k_sigma * bb_data["bb_smaStd"];
    
    bb_data["bb{}".format(bbSize)] = (data - bb_data["lowerBand"]) / (bb_data["upperBand"] - bb_data["lowerBand"])
    # Replace NaN with RSI=100
    bb_data = bb_data.replace([np.inf, -np.inf], 0.5)
     # Return BB
    return bb_data["bb{}".format(bbSize)]
     
# Define the MACD sizes
bb_sizes = [14, 20]

# Loop to calculate the Bollinger Bands
for n in bb_sizes:
    long_df["ask_bb{}".format(n)] = calc_bb(eurusd_df["ask_close"], bbSize=n)
    short_df["bid_bb{}".format(n)] = calc_bb(eurusd_df["bid_close"], bbSize=n)

# Remove working variables
del bb_sizes, n

#==============================================================================
# Calculates the VI (Vortex Indicator)
# Ref: https://en.wikipedia.org/wiki/Vortex_indicator
#==============================================================================
def calc_vi(data, toDataFrame, viSize=14):
    """ Calculates the Vortex Indicator column of the data
    Ref: https://en.wikipedia.org/wiki/Vortex_indicator
    @highData: DataFrame column with data candle high values.
    @lowData: DataFrame column with data candle low values.
    @closeData: DataFrame column with data candle close values.
    @viSize: number of values to calculate the VI. Must be bigger than 2. Wilder used 14 periods originally.
    @return [VIUP, VIDOWN] BigData_column
    """
    # Copy data into DataFrame
    vi_data = pd.DataFrame(index=data.index)
    
    # Calculates the True Range
    vi_data["tr"] = calc_tr(data)["tr"]
    # Calculates the SMA of the True Range
    vi_data["tr_SMA"] = calc_sma(vi_data["tr"], size=viSize) #VI_TR
    # Calculates the Vortex Movement Up (VM+): highData(i) - lowData(i-1)
    vi_data["VM_UP"] = data["high"] - data["low"].shift(1)
    # Calculates the Vortex Movement Down (VM-): lowData(i) - highData(i-1)
    vi_data["VM_DOWN"] = data["low"] - data["high"].shift(1)
    # Calculates the Vortex Indicator (VI+)
    vi_data["VI_UP"] = calc_sma(vi_data["VM_UP"], size=viSize)
    # Calculates the Vortex Indicator (VI-)
    vi_data["VI_DOWN"] = calc_sma(vi_data["VM_DOWN"], size=viSize)

    # Calculates the final Vortex Indicator UP values
    toDataFrame["vi_up{}".format(viSize)] = vi_data["VI_UP"] / vi_data["tr"]
    # Calculates the final Vortex Indicator DOWN values
    toDataFrame["vi_down{}".format(viSize)] = vi_data["VI_DOWN"] / vi_data["tr"]

# Prepare the data to calculate ask VI
data_ask_vi = eurusd_df.loc[:,["ask_high", "ask_low", "ask_close"]]
data_ask_vi.columns = ["high", "low", "close"]
# Prepare the data to calculate bid VI
data_bid_vi = eurusd_df.loc[:,["bid_high", "bid_low", "bid_close"]]
data_bid_vi.columns = ["high", "low", "close"]

# Define the MACD sizes
vi_sizes = [13, 21, 34]

# Loop to calculate the Vortex Indicator
for n in vi_sizes:
    calc_vi(data_ask_vi, long_df, viSize=n)
    calc_vi(data_bid_vi, short_df, viSize=n)

# Remove working variables
del data_ask_vi, data_bid_vi, vi_sizes, n

## End of file ##