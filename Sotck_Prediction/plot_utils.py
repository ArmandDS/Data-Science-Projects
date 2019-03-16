# -*- coding: utf-8 -*-
"""
File with plot util functions
@author: pcalderon
@date: 20170819
"""
import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt

def scatter_plot(data, x_name, y_name):
    """ This function creates the scatter plot """
    plt = data.plot(kind='scatter', x=x_name, y=y_name)
    # Calculates the linear regression (order=1) of the two series and returns beta and alpha
    # Which represents: y = beta * x + alpha
    beta, alpha = np.polyfit(data[x_name], data[y_name], 1) # order=1
    # Plot the regression line y=mx+b, where m is the beta and alpha is the intersection b
    plt.plot(data[x_name], beta * data[x_name] + alpha, '-', color='r')
    # Calculates the correlation coefficient
    corr_value = (data[[x_name, y_name]].corr(method='pearson'))[y_name][x_name]
    # Draw the beta and alpha values in the plot
    plt.text(0.3, 0.8,'beta='+str(beta)+'\nalpha='+str(alpha)+'\ncorr='+str(corr_value), ha='center', va='center', transform=plt.transAxes)
    # Show plot
    #plt.show()


def function_plot(f, x, x_delta=10, x_points=201, title="Function value around point"):
    """ This function plots the line defined by f around X point """
    # Creates the x serie points
    Xplot = np.linspace(x-x_delta, x+x_delta, x_points)
    # Creates the y serie points
    Yplot = f(Xplot)
    # Creates the plot
    fig, ax1 = plt.subplots()
    # Plot the function line
    plt.plot(Xplot, Yplot)
    # Plot the point
    plt.plot(x, f(x), 'ro')
    # Set plot labels
    plt.title(title)
    ax1.set_xlabel('X')
    ax1.set_ylabel('Y')
    # X axis grid lines
    ax1.grid()
    # Show plot
    plt.show()

