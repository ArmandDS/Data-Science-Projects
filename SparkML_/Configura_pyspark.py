# -*- coding: utf-8 -*-
"""
Configuration file for pyspark with Spyder
"""

import os
import sys



os.environ['SPARK_HOME'] = 'C:\\spark-2.1.1-bin-hadoop2.7'

# Create a variable for our root path
SPARK_HOME = os.environ['SPARK_HOME']

#Add the following paths to the system path. Please check your installation
#to make sure that these zip files actually exist. The names might change
#as versions change.
sys.path.insert(0,os.path.join(SPARK_HOME,"python"))
sys.path.insert(0,os.path.join(SPARK_HOME,"python","lib"))
sys.path.insert(0,os.path.join(SPARK_HOME,"python","lib","pyspark.zip"))
sys.path.insert(0,os.path.join(SPARK_HOME,"python","lib","py4j-0.10.4-src.zip"))

#Initialize SparkSession and SparkContext
from pyspark.sql import SparkSession
from pyspark import SparkContext, SparkConf

#Create a Spark Session
MySparkSession = SparkSession \
    .builder \
    .master("local[2]") \
    .appName("MiPrimer") \
    .config("spark.executor.memory", "6g") \
    .config("spark.cores.max","4") \
    .getOrCreate()
    
#Get the Spark Context from Spark Session    
MySparkContext = MySparkSession.sparkContext

# check Spark is up & running (localhost:4040)

#Test Spark
testData = MySparkContext.parallelize([3,6,4,2])

print( testData.count() )

# TO STOP SPARK: 
# MySparkContext.stop()
