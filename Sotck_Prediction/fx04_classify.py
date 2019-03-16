# -*- coding: utf-8 -*-
"""
This files contains the code to run multiple classification algorithms.
@author: Pablo Calderon
@date: 20171101
"""
import pandas as pd
# sklearn is on scikit library
from sklearn.linear_model import Perceptron
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.ensemble import BaggingClassifier
from sklearn.ensemble import AdaBoostClassifier

from sklearn.metrics import confusion_matrix

import matplotlib.pyplot as plt

#==============================================================================
# Executes the file which generates the matrix
#==============================================================================
exec(open("./fx03_window.py").read()) # For python 3
# execfile("./fx02_window.py") # For python 2


def predict_algorithm(results, model_list, algorithm, col_name):
    """ This function fits the algorithm in all the Window_model objects and predicts the classification
    @results: data frame with the original types and the pips columns
    @model_list: array list of Window_model objects
    @algorithm: classifier object
    @col_name: name of the column in the dataframe to save the classfication """
    results[col_name] = 0
    # Loop to iterate over the windows to apply the algorithm
    for i in range(0, len(model_list)):
        # Fits the algorithm with the train data
        algorithm = algorithm.fit(model_list[i].getXtrain(), model_list[i].getYtrain())
        # Reads the test data
        resY = model_list[i].getYtest()
        # Predict the class on the test data
        resY.loc[:,"pred"] = algorithm.predict(model_list[i].getXtest())
        # Concatenates the results
        results[col_name] = pd.concat([results[col_name], resY["pred"]], axis=1).fillna(0).sum(axis=1)
        

def run_algorithms(results, model_list):
    """ Run the batch of classifiers
    @results: data frame with the original types and the pips columns
    @model_list: array list of Window_model objects """
    # Run the Linear Discriminant Analysis
    predict_algorithm(results, model_list, clfLDA, "pre_LDA")
    # Run the Quadratic Discriminant Analysis
    predict_algorithm(results, model_list, clfQDA, "pre_QDA")
    # Run the Gaussian Naive Bayes
    predict_algorithm(results, model_list, clfGNB, "pre_GNB")
    # Run the Perceptron
    predict_algorithm(results, model_list, clfPerceptron, "pred_Perceptron")
    # Run the Decision Tree classifier
    predict_algorithm(results, model_list, clfDecisionTree, "pred_DecisionTree")
    # Run the Random Forest classifier
    predict_algorithm(results, model_list, clfRandomForest, "pred_RandomForest")
    # Run the K-nearest neighbor classifier
    predict_algorithm(results, model_list, clfKNeighbors, "pred_KNeighbors")
    # Run the Support Vector Machine classifier
    predict_algorithm(results, model_list, clfSVC, "pred_SVC")
    # Run the extremely randomized tree classifier Extra Tree
    predict_algorithm(results, model_list, clfExtraTree, "pred_ExtraTree")
    # Run the Grading Boosting classifier
    predict_algorithm(results, model_list, clfGradBoosting, "pred_GradBoosting")
    # Run the Bagging meta-estimator
    predict_algorithm(results, model_list, clfBagging, "pred_Bagging")
    # Run the AdaBoost classifier
    predict_algorithm(results, model_list, clfAdaBoost, "pred_AdaBoost")
    

#==============================================================================
# Creates the classifiers
#==============================================================================
# Ref: http://scikit-learn.org/stable/modules/generated/sklearn.discriminant_analysis.LinearDiscriminantAnalysis.html
clfLDA = LinearDiscriminantAnalysis()
# Ref: http://scikit-learn.org/stable/modules/generated/sklearn.discriminant_analysis.QuadraticDiscriminantAnalysis.html
clfQDA = QuadraticDiscriminantAnalysis()
# Ref: http://scikit-learn.org/stable/modules/naive_bayes.html
clfGNB = GaussianNB()
# Ref: http://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Perceptron.html
clfPerceptron = Perceptron()
# Ref: http://scikit-learn.org/stable/modules/tree.html#classification
clfDecisionTree = DecisionTreeClassifier()
# Ref: http://scikit-learn.org/stable/modules/ensemble.html#random-forests
clfRandomForest = RandomForestClassifier(n_estimators=10)
# Ref: http://scikit-learn.org/stable/modules/neighbors.html
clfKNeighbors = KNeighborsClassifier(n_neighbors=7)
# Ref: http://scikit-learn.org/stable/modules/svm.html
clfSVC = SVC(kernel='rbf', probability=True)
# Ref: http://scikit-learn.org/stable/modules/generated/sklearn.tree.ExtraTreeClassifier.html
clfExtraTree = ExtraTreesClassifier(n_estimators=10, max_depth=None, min_samples_split=2, random_state=0)
# Ref: http://scikit-learn.org/stable/modules/ensemble.html#gradient-tree-boosting
clfGradBoosting = GradientBoostingClassifier(n_estimators=100, learning_rate=1.0, max_depth=1, random_state=0)
# Ref: http://scikit-learn.org/stable/modules/ensemble.html#bagging-meta-estimator
clfBagging = BaggingClassifier(KNeighborsClassifier(), max_samples=0.5, max_features=0.5)
# Ref: http://scikit-learn.org/stable/modules/ensemble.html#adaboost
clfAdaBoost = AdaBoostClassifier(n_estimators=100)

""" Creates the data frame with the original types and the pips columns """
results_long = long_df.loc[:,("real_type", "pips")]
results_short = short_df.loc[:,("real_type", "pips")]

#==============================================================================
# Run the algorithms
#==============================================================================
run_algorithms(results_long, long_model_list)
run_algorithms(results_short, short_model_list)

def filter_byTest(results, model_list):
    """ Filter the matrix to remove the data before the test start date and after the test end date """
    # Reads the test start date
    start_test = model_list[0].testInitDate()
    # Reads the test stop date
    stop_test = model_list[len(model_list)-1].testEndDate()
    # Filter the matrix to remove the data before the test start date
    results = results[results.index>=start_test]
    # Filter the matrix to remove the data after the test end date
    results = results[results.index<=stop_test]
    return results

# Filter the results data frames
results_long = filter_byTest(results_long, long_model_list)
results_short = filter_byTest(results_short, short_model_list)

#==============================================================================
# Calculates the confusion matrices
# Ref: https://en.wikipedia.org/wiki/Confusion_matrix
#==============================================================================
# Creates a dictionary to save the confusion matrices
confusionMatrix_long = {}
confusionMatrix_short = {}
# Loop through the results to calculate the confusion matrix
for i in range(2,results_long.shape[1]):
    confusionMatrix_long[results_long.columns[i]] = confusion_matrix(results_long["real_type"], results_long[results_long.columns[i]])
    confusionMatrix_short[results_short.columns[i]] = confusion_matrix(results_short["real_type"], results_short[results_short.columns[i]])

# Print confusion matrices
for i in confusionMatrix_long.keys():
    print("LONG:",i,"\n",confusionMatrix_long[i])
    print("SHORT:",i,"\n",confusionMatrix_short[i])

# Remove working variables
del i

#==============================================================================
# Calculates the score for each algorithm
#==============================================================================
# Creates the score data frame
score = pd.DataFrame()
# Calculates the score for the long algorithms
results_long_score = results_long.sub(results_long["real_type"], axis=0)
# Removes the pips column
results_long_score.drop("pips", axis=1, inplace=True)
# Saves the results to the data frame
score["long"] = (results_long_score == 0).sum(axis=0) / len(results_long_score)

# Calculates the score for the short algorithms
results_short_score = results_short.sub(results_short["real_type"], axis=0)
# Removes the pips column
results_short_score.drop("pips", axis=1, inplace=True)
# Saves the results to the data frame
score["short"] = (results_short_score == 0).sum(axis=0) / len(results_short_score)

# Calculates the average score
score["avg"] = (score["long"] + score["short"]) / 2.

#==============================================================================
# Calcualte the equity for each classifier
#==============================================================================
def calculateEquity(results, pips_label="pips", type_value=0.5):
    """ Calculate the equity for each algorithm solution """
    # Copy the matrix of data
    equity_results = results.copy()
    # Remove the columns with pips
    del equity_results[pips_label]
    
    # Set 1 for the deals which confirm the condition and zero to the rest
    equity_results = (equity_results >= type_value)
    # Convert boolean to integer (0 or 1)
    equity_results = equity_results.astype(int)
    # Multiply the deals done by the pips done per deal
    equity_results = equity_results.multiply(results[pips_label], axis=0)
    # Calculate the equity by cumulative sum of the pips per deal
    equity_results = equity_results.cumsum(axis=0)
    # Return equity data frame
    return equity_results

# Calculate the equity for each classificator for the long deals
equity_long = calculateEquity(results_long, "pips", 0.5)
# Calculate the equity for each classificator for the short deals
equity_short = calculateEquity(results_short, "pips", 0.5)


#==============================================================================
# Create equity plots
#==============================================================================
plotEquity(equity_long.iloc[:,1:], "Equity data for Longs")
plotEquity(equity_short.iloc[:,1:], "Equity data for Short")

#plotEquity(equity_long, "Equity data for Longs")
#plotEquity(equity_short, "Equity data for Shorts")


""" Combine long and short """    
equity = equity_long + equity_short
# Plot the equity combined (long + short)
plotEquity(equity.iloc[:,1:], "Equity data")




# =============================================================================
# Calculates the Account performance
# =============================================================================
def algo_performance(algo_name = "pre_LDA", doShort=False):
    """ This function calculates the algorithm performance and save results to score df
    @algo_name: Define the algorithm name to calculate the equity parameters
    @equity_selected: Select the equity
    @calmar_col_name: name of the column to store calmar value
    @maxdd_col_name: name of the column to store max draw down value
    """
    # Select the equity
    equity_selected = equity_long
    results_df = results_long
    calmar_col_name="calmar_long"
    ppd_col_name="ppd_long"
    maxdd_col_name="max_dd_long"
    
    if doShort:
        # Select the equity
        equity_selected = equity_short
        results_df = results_short
        calmar_col_name="calmar_short"
        ppd_col_name="ppd_short"
        maxdd_col_name="max_dd_short"
        
    # Calculate the total number of years
    years = (equity_selected.loc[:,algo_name].index[-1] - equity_selected.loc[:,algo_name].index[1]).total_seconds() / 3600 / 24 /365
    
    # Calculate the equity in pips
    my_equity_pips = equity_selected.loc[:,algo_name]
    # Calculates the account drawdown in pips
    my_equity_drawdown_pips = my_equity_pips - my_equity_pips.cummax()
    # Calculate annualized calmar: total profit / maximum drawdown / num years
    my_calmar = -my_equity_pips[-1] / min(my_equity_drawdown_pips) / years
    
    score.loc[algo_name, calmar_col_name] = my_calmar
    score.loc[algo_name, ppd_col_name] = my_equity_pips[-1] / results_df[algo_name].sum()
    score.loc[algo_name, maxdd_col_name] = min(my_equity_drawdown_pips)
    #print("calmar = ", my_calmar)

# Remove real_type row
score = score[score.index != "real_type"]

#score= score.loc[:,{"long","short","avg"}]
# Creates the columns in score data_dataframe
score["calmar_long"] = 0
score["calmar_short"] = 0
score["ppd_long"] = 0
score["ppd_short"] = 0
score["max_dd_long"] = 0
score["max_dd_short"] = 0
# Calculate algorithms performances
for s in score.index:
    print(s)
    algo_performance(algo_name=s, doShort=False)
    algo_performance(algo_name=s, doShort=True)


# =============================================================================
# Calculates the Account performance
# =============================================================================
# Define the algorithm name to calculate the equity parameters
algo_name = "pre_GNB"
# Select the equity
equity_selected = equity_short
# Calculate the total number of years
years = (equity_selected.loc[:,algo_name].index[-1] - equity_selected.loc[:,algo_name].index[1]).total_seconds() / 3600 / 24 /365

# Calculate the equity in pips
my_equity_pips = equity_selected.loc[:,algo_name]
# Calculates the account drawdown in pips
my_equity_drawdown_pips = my_equity_pips - my_equity_pips.cummax()
# Calculate annualized calmar: total profit / maximum drawdown / num years
my_calmar = -my_equity_pips[-1] / min(my_equity_drawdown_pips) / years
print("calmar = ", my_calmar)


# Define the initial account value (€)
init_account = 50000
# Defines the amount per deal (€)
amount_per_deal = 5000
# Calculates the account equity (€)
my_equity = init_account + my_equity_pips * amount_per_deal / 1e4
# Calculates the account drawdown in pct
my_equity_drawdown_pct = (my_equity / my_equity.cummax())-1.
# Calculates the account drawdown in €
my_equity_drawdown = my_equity - my_equity.cummax()

# Annual profit in €
annual_profit = (my_equity[-1] - init_account -1) / years
print("annual profit = ", annual_profit, "€")
# Annual profit pct
annual_profit = (my_equity[-1]/init_account -1) / years
print("annual profit = ", annual_profit*100, "%")
# Maximum drawdown in €
print("max drawdown=", min(my_equity_drawdown), "€")

# Plots
plotEquity(my_equity, "My Equity", ylab="Account Equity [€]")
plotEquity(my_equity_drawdown, "My Equity drawdown", ylab="Equity drawdown [€]")

plotEquity(my_equity_drawdown_pct, "My Equity drawdown pct", ylab="Equity drawdown [pct]")


del algo_name, equity_selected, years, my_calmar, init_account, amount_per_deal, annual_profit
## End of file ##