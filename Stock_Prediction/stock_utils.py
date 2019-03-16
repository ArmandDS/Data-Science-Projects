# -*- coding: utf-8 -*-
"""
File with util functions
@author: pcalderon
@date: 20170816
"""
import pandas as pd
from time import time

def read_stock(stock_name, usecols_value=['Date', 'Adj Close']):
    """ This function reads the csv file from the data folder and loads the Adj Close column to a Data Frame.
    @stock_name: name of the csv file in the data folder """
    # Imports the data from csv file
    stock_data = pd.read_csv("data/{}.csv".format(stock_name), index_col="Date", parse_dates=True,
                             usecols=usecols_value, delimiter=",", na_values="null")
    # Remove lines with null (NaN)
    stock_data = stock_data.dropna()
    # Rename column
    stock_data = stock_data.rename(columns={'Adj Close':stock_name})
    return stock_data

def create_df(start_date, end_date):
    """ This function creates an empty data frame with a range date as index.
    @start_date: first date of the range, format '2017-01-01'
    @end_date: final date of the range, format '2017-01-01' """
    # Creates the range index
    dates = pd.date_range(start_date, end_date)
    # Create an empty dataframe
    return pd.DataFrame(index=dates)

def read_stock_list(stock_list, start_date, end_date):
    """ This function creates an empty data frame with a range date as index.
    @stock_list: list with the names of the csv files in the data folder.
    @start_date: first date of the range, format '2017-01-01'
    @end_date: final date of the range, format '2017-01-01' """
        # Create data frame
    df = create_df(start_date, end_date)
    # Read stocks and adds to data frame
    for stock_name in stock_list:
        # Load data from csv file
        stock_data = read_stock(stock_name)
        # Adds the stock data (inner join)
        df = df.join(stock_data, how='inner')
    return df

def normalize_data(df):
    """ This function normalizes the data by dividing each set of data by the first value of each serie
    @df Data Frame with dat to be normalized """
    return df / df.iloc[0]

def normalize_standard_core(data):
    """ Normalizes the data by the standard score method: (X - mean) / stddev """
    return (data - data.mean()) / data.std()

def how_long(func, *args):
    """ Executes function with given arguments and measure execution time."""
    t0 = time()
    result = func(*args)
    t1 = time()
    return result, t1 - t0

