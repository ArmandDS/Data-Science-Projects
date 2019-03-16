# -*- coding: utf-8 -*-
"""
This files contains the code to split the matrix into window
@author: Pablo Calderon
@date: 20171101
"""
import pandas as pd
#from numpy import inf
################################################
# Executes the file which generates the matrix #
################################################
exec(open("./fx02_strategies.py").read()) # For python 3
# execfile("./fx01_create_matrix.py") # For python 2


class Window_model:
    """ This class stores the model data for the Machine Learning analisys """
    
    """ Object instance id """
    model_id = 0
    """ DataFrame to store the train matrix """
    train_data = pd.DataFrame()
    """ DataFrame to store the test matrix """
    test_data = pd.DataFrame()
    
    idx = pd.IndexSlice

    def __init__(self, model_id, train_data, test_data):
        """ Class constructor """
        self.model_id = model_id
        self.train_data = train_data
        self.test_data = test_data
    
    def info(self):
        """ This function prints the main information of the object instance """
        print(self.model_id, ": trainSize=", self.train_data.shape[0], ", testSize=", self.test_data.shape[0],
              ", train:", self.train_data.index[0], "-",  self.train_data.index[-1],
              ", test:", self.test_data.index[0],
              "-",  self.test_data.index[-1])
    
    def getXtrain(self):
        """ Returns the X matrix for the train data """
        return self.getData(self.train_data, "ask|bid")
        #return self.train_data.loc[self.idx[:,self.train_data.columns.str.contains("ask|bid")]]

    def getYtrain(self):
        """ Returns the Y matrix for the train data """
        return self.getData(self.train_data, "type")
        #return self.train_data.loc[self.idx[:,self.train_data.columns.str.contains("type")]]

    def getXtest(self):
        """ Returns the X matrix for the test data """
        return self.getData(self.test_data, "ask|bid")
        #return self.test_data.loc[self.idx[:,self.test_data.columns.str.contains("ask|bid")]]

    def getYtest(self):
        """ Returns the Y matrix for the test data """
        return self.getData(self.test_data, "type")
        #return self.test_data.loc[self.idx[:,self.test_data.columns.str.contains("type")]]
    
    def getData(self, data=train_data, var_text="ask|long"):
        """ Returns the matrix with the filter columns by the var_text """
        return data.loc[self.idx[:,data.columns.str.contains(var_text)]]
    
    def testSize(self):
        """ Returns the size of the test data """
        return self.test_data.shape[0]
    
    def trainSize(self):
        """ Returns the size of the train data """
        return self.train_data.shape[0]
    
    def testInitDate(self):
         return self.test_data.index[0]
     
    def testEndDate(self):
         return self.test_data.index[-1]

def create_windows(data, trainSize=1440, testSize=120, gap=48):
    """ This function creates the list with sindow object
    @data: DataFrame with matrix data to create the window objects 
    @trainSize: number of periods of the train window (by default 40days: 24*40=960)
    @testSize: number of periods of the test window (by default 20days: 24*20=480)
    @gap: number of periods between train and test to allow data collection
    """
    # List with window objects created
    win_model_list = []
    # Calculate the number of windows to be created
    num_windows = (int)((data.shape[0]-trainSize-gap) / testSize)
    # Loop to create all the window objects
    for i in range(0, num_windows):
        # This is the point where the test window starts (and where the train stops)
        start_test = trainSize + gap + i * testSize
        # Point where the test ends
        end_test = start_test + testSize
        
        # Point where the train ends
        end_train = start_test - gap
        # This is the point where each window starts
        start_train = end_train - trainSize
        
        # Slice the train matrix
        i_train = data.iloc[start_train : end_train]
        # Slice the train matrix
        i_test = data.iloc[start_test : end_test]
        
        # Creates the model
        window_model = Window_model(i, i_train, i_test)
        # Adds the model to the list
        win_model_list.append(window_model)
        
    # Returns the list of window objects
    return win_model_list

# Creates the model lists
long_model_list = create_windows(long_df, gap=periods)
short_model_list = create_windows(short_df, gap=periods)

if False:
    # Plot the long model list object info
    for i in range(0, len(long_model_list)):
        long_model_list[i].info()
    
    # Creates object for debbuging purposes
    debug_train_obj = long_model_list[0].train_data
    debug_test_obj = long_model_list[0].test_data


"""
long_model_list[0].train_data.index[0]
long_model_list[0].train_data.info()
long_model_list[len(long_model_list)-1].train_data.info()
"""
# Remove working variables
del periods
## End of file ##