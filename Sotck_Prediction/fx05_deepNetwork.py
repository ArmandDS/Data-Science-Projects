# -*- coding: utf-8 -*-
"""
This files contains the code to run the neural network
@author: Pablo Calderon
@date: 20171101
"""
import pandas as pd
# sklearn is on scikit library
from sklearn.neural_network import MLPClassifier

#==============================================================================
# Executes the file which generates the matrix
#==============================================================================
exec(open("./fx03_window.py").read()) # For python 3
# Also load predict_algorithm, filter_byTest, calculateEquity from fx04_classify
# execfile("./fx02_window.py") # For python 2


def run_deep_algorithms(results, model_list):
    """ Run the batch of classifiers
    @results: data frame with the original types and the pips columns
    @model_list: array list of Window_model objects """
    # Run the Multi-layer Perceptron classifier
    predict_algorithm(results, model_list, clfMLP, "pred_MLP")
    # Run the Multi-layer Perceptron classifier
    predict_algorithm(results, model_list, clfMLP1, "pred_MLP1")
    # Run the Multi-layer Perceptron classifier
    predict_algorithm(results, model_list, clfMLP2, "pred_MLP2")
    # Run the Multi-layer Perceptron classifier
    predict_algorithm(results, model_list, clfMLP3, "pred_MLP3")


""" Creates the classifiers """
# Ref: http://scikit-learn.org/stable/modules/generated/sklearn.neural_network.MLPClassifier.html
clfMLP = MLPClassifier(solver='lbfgs', hidden_layer_sizes=(10, 10, 10, 10, 10, 10, 10, 10, 10, 10),
                       early_stopping=True, verbose=True, random_state=1)
clfMLP1 = MLPClassifier(solver='lbfgs', hidden_layer_sizes=(50, 50, 50, 50, 50, 50, 50, 50, 50, 50),
                       early_stopping=True, verbose=True, random_state=1)
clfMLP2 = MLPClassifier(solver='lbfgs', hidden_layer_sizes=(50, 50),
                        early_stopping=True, verbose=True, random_state=1)
clfMLP3 = MLPClassifier(solver='lbfgs', hidden_layer_sizes=(100,100,100,100,100,100,100,100,100,100,100,100,100,100,100,100,100,100,100,100),
                        early_stopping=True, verbose=True, random_state=1)

""" Creates the data frame with the original types and the pips columns """
results_deep_long = long_df.loc[:,("real_type", "pips")]
results_deep_short = short_df.loc[:,("real_type", "pips")]

# Run the algorithms
run_deep_algorithms(results_deep_long, long_model_list)
run_deep_algorithms(results_deep_short, short_model_list)

# Filter the results data frames
results_deep_long = filter_byTest(results_deep_long, long_model_list)
results_deep_short = filter_byTest(results_deep_short, short_model_list)

# Calculate the equity for each classificator for the long deals
equity_deep_long = calculateEquity(results_deep_long, "pips", 0.5)
# Calculate the equity for each classificator for the short deals
equity_deep_short = calculateEquity(results_deep_short, "pips", 0.5)

# Create equity plots
plotEquity(equity_deep_long, "Equity data for Longs")
plotEquity(equity_deep_short, "Equity data for Shorts")

plotEquity(equity_deep_long.iloc[:,1:], "Equity data for Longs")
plotEquity(equity_deep_short.iloc[:,1:], "Equity data for Short")


""" Combine long and short """    
equity_deep = equity_deep_long + equity_deep_short
# Plot the equity combined (long + short)
plotEquity(equity_deep.iloc[:,1:], "Equity deep data")

#==============================================================================
# Calculates the score for each algorithm
#==============================================================================
# Creates the score data frame
score_deep = pd.DataFrame()
# Calculates the score for the long algorithms
results_deep_long_score = results_deep_long.sub(results_deep_long["real_type"], axis=0)
# Removes the pips column
results_deep_long_score.drop("pips", axis=1, inplace=True)
# Saves the results to the data frame
score_deep["long"] = (results_deep_long_score == 0).sum(axis=0) / len(results_deep_long_score)

# Calculates the score for the short algorithms
results_deep_short_score = results_deep_short.sub(results_deep_short["real_type"], axis=0)
# Removes the pips column
results_deep_short_score.drop("pips", axis=1, inplace=True)
# Saves the results to the data frame
score_deep["short"] = (results_deep_short_score == 0).sum(axis=0) / len(results_deep_short_score)

# Calculates the average score
score_deep["avg"] = (score_deep["long"] + score_deep["short"]) / 2.


# =============================================================================
# Calculates the Account performance
# =============================================================================
def algo_performance_deep(algo_name = "pre_MLP", doShort=False):
    """ This function calculates the algorithm performance and save results to score df
    @algo_name: Define the algorithm name to calculate the equity parameters
    @equity_selected: Select the equity
    @calmar_col_name: name of the column to store calmar value
    @maxdd_col_name: name of the column to store max draw down value
    """
    # Select the equity
    equity_selected = equity_deep_long
    results_df = results_deep_long
    calmar_col_name="calmar_long"
    ppd_col_name="ppd_long"
    maxdd_col_name="max_dd_long"
    
    if doShort:
        # Select the equity
        equity_selected = equity_deep_short
        results_df = results_deep_short
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
    
    score_deep.loc[algo_name, calmar_col_name] = my_calmar
    score_deep.loc[algo_name, ppd_col_name] = my_equity_pips[-1] / results_df[algo_name].sum()
    score_deep.loc[algo_name, maxdd_col_name] = min(my_equity_drawdown_pips)
    #print("calmar = ", my_calmar)

# Remove real_type row
score_deep = score_deep[score_deep.index != "real_type"]

#score= score.loc[:,{"long","short","avg"}]
# Creates the columns in score data_dataframe
score_deep["calmar_long"] = 0
score_deep["calmar_short"] = 0
score_deep["ppd_long"] = 0
score_deep["ppd_short"] = 0
score_deep["max_dd_long"] = 0
score_deep["max_dd_short"] = 0
# Calculate algorithms performances
for s in score_deep.index:
    print(s)
    algo_performance_deep(algo_name=s, doShort=False)
    algo_performance_deep(algo_name=s, doShort=True)





#==============================================================================
# Iterator example to monitor accuracy
#==============================================================================
# Creates the classifier
mlp = MLPClassifier(solver='adam', alpha=1e-5, warm_start=True, max_iter=20,
                       hidden_layer_sizes=(10, 10, 10, 10),
                       early_stopping=True, verbose=0, random_state=1)

# Creates the array to save the accuracy over iterations
loss = []
# Limit to stop loop
N_EPOCHS = 1000
# EPOCH
epoch = 1
while epoch < N_EPOCHS:
    predict_algorithm(results_deep_long, long_model_list, mlp, "pred_mlp")
    loss.append(mlp.loss_)
    epoch += 1

# Creates the dataframe to plot accuracy
loss_df = pd.DataFrame()
# Add data to data frame
loss_df["loss"] = loss
# Plot the accuracy curve
plotEquity(loss_df, "Accuracy over epochs", xlab="epochs", ylab="accuracy")

## End of file ##