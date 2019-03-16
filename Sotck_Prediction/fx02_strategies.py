# -*- coding: utf-8 -*-
"""
This files contains the code to create the target variable
@author: Pablo Calderon
@date: 20180505
"""
import matplotlib.pyplot as plt

################################################
# Executes the file which generates the matrix #
################################################
exec(open("./fx01_create_matrix.py").read()) # For python 3
# execfile("./fx01_create_matrix.py") # For python 2

#==============================================================================
# Trend Strategy: opens a deal at each hour and close the deal a fix number
#                 of periods before the deal is open.
#==============================================================================
def strategy_trend(open_periods = 48):
    """ This function calculates the number of pips X periods after open deal
    @df: dataframe with index data where the results are copied
    @open_col: dataframe column with prices to open the deals
    @close_col: dataframe column with prices to close the deals
    @take_profit: price to close the deal (win)
    @stop_loss: price to close the deal (loss)
    @open_periods: maximum number of periods the deal is open
    @deal_type: set to 1 for long deals and -1 for short deals
    """    
    # Calculates the number of pips per deal
    long_df["long_pips"] = (eurusd_df["bid_close"].shift(-open_periods) - eurusd_df["ask_close"]) * 1e4
    short_df["short_pips"] = (eurusd_df["bid_close"] - eurusd_df["ask_close"].shift(-open_periods)) * 1e4

#==============================================================================
# TPSL Strategy: opens a deal at each hour. The deals are closed when they
#                touch the stop loss level or the take profit level.
#                The deals are also close at number maximum of periods if the
#                deal is still open.
#==============================================================================
def strategy_tpsl_long(df, instrument, take_profit = 50e-4, stop_loss = -20e-4, open_periods = 48):
    """ This function calculates the pips for each LONG deal with a fix take profit and stop loss
    @df: dataframe with index data where the results are copied
    @instrument: dataframe with instrument OHLC values
    @take_profit: price to close the deal (win)
    @stop_loss: price to close the deal (loss)
    @open_periods: maximum number of periods the deal is open
    """
    df["pips"] = 0
    df["close_index"] = 0
    index = df.index
    for i_open in range(0, index.shape[0]-1):
    #for i_open in range(0, 100):
        # Read open price
        open_price = instrument.loc[index[i_open], "ask_close"]
        
        for i_close in range(0, open_periods):
            # Calculates the index to close the deal
            close_index = i_open + i_close + 1
            # Check index
            if(close_index >= index.shape[0]):
                break
            
            # Check stop loss price
            if((instrument.loc[index[close_index], "bid_low"] - open_price) <= stop_loss):
                df.loc[index[i_open], 'pips'] = stop_loss * 1e4
                df.loc[index[i_open], 'close_index'] = i_close
                break
            # Check take profit price
            elif((instrument.loc[index[close_index], "bid_high"] - open_price) >= take_profit):
                df.loc[index[i_open], 'pips'] = take_profit * 1e4
                df.loc[index[i_open], 'close_index'] = i_close
                break
            # Check maximum number of periods 
            if(i_close >= open_periods-1):
                df.loc[index[i_open], 'pips'] = (instrument.loc[index[close_index], "bid_close"] - open_price) * 1e4
                df.loc[index[i_open], 'close_index'] = i_close
                break

def strategy_tpsl_short(df, instrument, take_profit = 50e-4, stop_loss = -20e-4, open_periods = 48):
    """ This function calculates the pips for each SHORT deal with a fix take profit and stop loss
    @df: dataframe with index data where the results are copied
    @instrument: dataframe with instrument OHLC values
    @take_profit: price to close the deal (win)
    @stop_loss: price to close the deal (loss)
    @open_periods: maximum number of periods the deal is open
    """
    df["pips"] = 0
    df["close_index"] = 0
    index = df.index
    for i_open in range(0, index.shape[0]-1):
    #for i_open in range(0, 1):
        # Read open price
        open_price = instrument.loc[index[i_open], "bid_close"]
        
        for i_close in range(0, open_periods):
            # Calculates the index to close the deal
            close_index = i_open + i_close + 1
            # Check index
            if(close_index >= index.shape[0]):
                break
            # Check stop loss price
            if((open_price - instrument.loc[index[close_index], "ask_high"]) <= stop_loss):
                df.loc[index[i_open], 'pips'] = stop_loss * 1e4
                df.loc[index[i_open], 'close_index'] = i_close
                break
            # Check take profit price
            elif((open_price - instrument.loc[index[close_index], "ask_low"]) >= take_profit):
                df.loc[index[i_open], 'pips'] = take_profit * 1e4
                df.loc[index[i_open], 'close_index'] = i_close
                break
            # Check maximum number of periods 
            if(i_close >= open_periods-1):
                df.loc[index[i_open], 'pips'] = (open_price - instrument.loc[index[close_index], "ask_close"]) * 1e4
                df.loc[index[i_open], 'close_index'] = i_close
                break


#==============================================================================
# This function automates the TPSL Strategy to calculate long and short deals.
#==============================================================================
def strategy_tpsl_ls(long_df, short_df, instrument,
                   take_profit = 50e-4,
                   stop_loss = -20e-4,
                   open_periods = 48):
    """ This function calculates the pips for each deal with a fix take profit and stop loss
    @long_df: dataframe with index data where the long deals results are copied
    @short_df: dataframe with index data where the short deals results are copied
    @instrument: dataframe with instrument ask and bid data (open, high, low, close)
    @take_profit: price to close the deal (win)
    @stop_loss: price to close the deal (loss)
    @open_periods: maximum number of periods the deal is open
    """
    # Calculates the pips for long deals
    strategy_tpsl_long(long_df, instrument, take_profit, stop_loss, open_periods)

    # Calculates the pips for short deals
    strategy_tpsl_short(short_df, instrument, take_profit, stop_loss, open_periods)

#==============================================================================
# Function to create equity lines plots
#==============================================================================
def plotEquity(data, plotTitle="Equity data", xlab="Years", ylab="Equity [pips]"):
    #plt.figure()
    # Create plots
    ax = data.plot(kind='line')

    # Set plot labels
    ax.set_xlabel(xlab)
    ax.set_ylabel(ylab)
    
    # Set plot title
    plt.title(plotTitle, fontsize = 20)
    # X axis grid lines
    ax.grid()
    
    # Show legend
    plt.legend(loc="lower left")
    
    # Shot plot
    plt.show()
    
#==============================================================================
# Defines the one hot encoding functions #
#==============================================================================
def getType4(data):
    """ This function get the One-Hot encoding for the pips
    @data: DataFrame column with data to calculate the one hot encoding
    """
    # Copy data into DataFrame
    type_data = pd.DataFrame(data)
    # One-Hot encoding function of number of pips
    type_data[type_data<=0] = 0
    type_data[(type_data>0) & (type_data<=10)] = 1
    type_data[(type_data>10) & (type_data<20)] = 2
    type_data[type_data>=20] = 3
    
    return type_data

def getType(data):
    """ This function get the One-Hot encoding for the pips
    @data: DataFrame column with data to calculate the one hot encoding
    """
    # Copy data into DataFrame
    type_data = pd.DataFrame(data)
    # One-Hot encoding function of number of pips
    type_data[type_data<=10] = 0
    type_data[type_data>10] = 1
    
    return type_data


#==============================================================================
# Runs the strategy for defined parameters.
#==============================================================================
# Defines the parameters for the strategy
tp = 140e-4
sl = -80e-4
periods = 48
# Calculates the long and short deals
strategy_tpsl_ls(long_df, short_df, eurusd_df, tp, sl, periods)

#strategy_tpsl_long(long_df, eurusd_df, tp, sl, periods)
#strategy_tpsl_short(short_df, eurusd_df, tp, sl, periods)

# Calculates the mean pips per deal
long_df["pips"].mean()
short_df["pips"].mean()

# Calculates the total pips
long_df["pips"].sum()
short_df["pips"].sum()

# Plot equities
plotEquity(short_df["pips"].cumsum())
plotEquity(long_df["pips"].cumsum())

# Plots the histogram of the pips
plt.hist(long_df["pips"],50)
plt.hist(short_df["pips"],50)

# Calculate the one hot encoding for the pips
long_df["real_type"] = getType(long_df["pips"])
short_df["real_type"] = getType(short_df["pips"])

del long_df["close_index"]
del short_df["close_index"]

# =============================================================================
# Removes the first section of the long and short data frames where the
# moving averages are not stables.
# =============================================================================
# Filters the long_df
long_df = long_df[long_df.index>'2004-01-01']
# Filters the short_df
short_df = short_df[short_df.index>'2004-01-01']

del sl, tp

if False:
    # This lines just prepare the data for export
    datav=eurusd_df
    datav["long_pips"] = long_df["pips"]
    datav["short_pips"] = short_df["pips"]

if False:
    #==============================================================================
    # Optimization analysis to find optimum take profit and stop loss.
    #==============================================================================
    # Creates the empty dataframe to save optimization results
    opt_results = pd.DataFrame(columns=["tp","sl","periods","long_ppd", "short_ppd"])
    # Dataframe to save long deals results
    opt_deals_long = pd.DataFrame(index=long_df.index)
    # Dataframe to save short deals results
    opt_deals_short = pd.DataFrame(index=short_df.index)
    
    # Defines the ranges and counter
    counter = 0
    tp_range = range(40,310,20)
    sl_range = range(-20,-110,-10)
    total = len(tp_range) * len(sl_range)
    
    # This loop takes about 10 hours running for total of 126 results!!!
    # Optimization analysis loop
    for i_tp in tp_range:
        tp = i_tp * 1e-4
        for i_sl in sl_range:
            sl = i_sl * 1e-4
            periods = 48
            print("tp=" + str(tp) + ", sl="+str(sl))
            counter = counter + 1
            # Calculates the long and short deals
            strategy_tpsl_ls(long_df, short_df, eurusd_df, tp, sl, periods)
            # Appends results to dataframe
            opt_results.loc[counter] = [tp, sl, periods, long_df["pips"].mean(), short_df["pips"].mean()]
            opt_deals_long["pips"+str(counter)] = long_df["pips"]
            opt_deals_short["pips"+str(counter)] = short_df["pips"]
            # Print progress
            print("so far: "+ str(round((counter/total)*100,2)) + "%")
        
    
    
    ########################################################################
    # Creates the pilot table for pips per deal (take profit vs stop loss) #
    # Pilot table ref: http://pbpython.com/pandas-pivot-table-explained.html
    ########################################################################
    opt_results_pt_long = pd.pivot_table(opt_results, index=["tp"], columns=["sl"], values=["long_ppd"])
    opt_results_pt_short = pd.pivot_table(opt_results, index=["tp"], columns=["sl"], values=["short_ppd"])
    
    #################################
    # Calculates the equity in pips #
    #################################
    opt_deals_long_equity = opt_deals_long.cumsum(axis=0)
    opt_deals_short_equity = opt_deals_short.cumsum(axis=0)
    
    ###########################################
    # Calculates the account drawdown in pips #
    ###########################################
    opt_deals_long_drawdown_pips = opt_deals_long_equity - opt_deals_long_equity.cummax()
    opt_deals_short_drawdown_pips = opt_deals_short_equity - opt_deals_short_equity.cummax()
    
    ############################################################################
    # Calculate annualized calmar: total profit / maximum drawdown / num years #
    ############################################################################
    # Calculate the total number of years
    years = (long_df.index[-1] - long_df.index[1]).total_seconds() / 3600 / 24 /365
    # Calculate the calmar = total pips / maximum draw down / years
    my_calmar_long = -opt_deals_long_equity.iloc[-1,:] / (opt_deals_long_drawdown_pips.min()) / years
    my_calmar_short = -opt_deals_short_equity.iloc[-1,:] / (opt_deals_short_drawdown_pips.min()) / years
    # Reset index
    my_calmar_long.index = opt_results.index
    my_calmar_short.index = opt_results.index
    
    opt_results["long_calmar"] = my_calmar_long
    opt_results["short_calmar"] = my_calmar_short
    ##############################
    # Calculate the max drawdown #
    ##############################
    maxdd_long =  opt_deals_long_drawdown_pips.min()
    maxdd_short =  opt_deals_short_drawdown_pips.min()
    # Reset index
    maxdd_long.index = opt_results.index
    maxdd_short.index = opt_results.index
    
    opt_results["long_max_dd"] = maxdd_long
    opt_results["short_max_dd"] = maxdd_short
    
    # Plots the pilot table for calmar (take profit vs stop loss)
    opt_results_pt_long_calmar = pd.pivot_table(opt_results, index=["tp"], columns=["sl"], values=["long_calmar"])
    opt_results_pt_short_calmar = pd.pivot_table(opt_results, index=["tp"], columns=["sl"], values=["short_calmar"])
    
    # Plots the pilot table for maximum draw down (take profit vs stop loss)
    opt_results_pt_long_maxdd = pd.pivot_table(opt_results, index=["tp"], columns=["sl"], values=["long_max_dd"])
    opt_results_pt_short_maxdd = pd.pivot_table(opt_results, index=["tp"], columns=["sl"], values=["short_max_dd"])
    
    
    del counter, i_sl, i_tp, maxdd_long, maxdd_short, my_calmar_long, my_calmar_short, periods, sl, total, tp, tp_range, sl_range
    
    
    
    
    plotEquity(opt_deals_long_equity["pips52"])
    plotEquity(opt_deals_short_equity["pips52"])



"""
# =============================================================================
# Candlestick plot with bokeh library
# =============================================================================
from math import pi
import pandas as pd
from bokeh.plotting import figure, show, output_file

eurusd_df_plot = eurusd_df.iloc[1:100,:]

inc = eurusd_df_plot.bid_close > eurusd_df_plot.bid_open
dec = eurusd_df_plot.bid_open > eurusd_df_plot.bid_close
w = 12*60*60*40
TOOLS = "pan,wheel_zoom,box_zoom,reset,save"
p = figure(x_axis_type="datetime", tools=TOOLS, plot_width=1000, title="Candlestick")
p.xaxis.major_label_orientation = pi/4
p.grid.grid_line_alpha=0.5
p.segment(eurusd_df_plot.index, eurusd_df_plot.bid_high, eurusd_df_plot.index, eurusd_df_plot.bid_low, color="black")
p.vbar(eurusd_df_plot.index[inc], w, eurusd_df_plot.bid_open[inc], eurusd_df_plot.bid_close[inc], fill_color="#D5E1DD", line_color="black")
p.vbar(eurusd_df_plot.index[dec], w, eurusd_df_plot.bid_open[dec], eurusd_df_plot.bid_close[dec], fill_color="#F2583E", line_color="black")
output_file("candlestick.html", title="candlestick.py example")
show(p)

# Remove working variables
del inc, dec, w, TOOLS, eurusd_df_plot, pi
"""


## End of file ##