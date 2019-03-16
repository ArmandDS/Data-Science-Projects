"""
===============================================================================
----------------------------   Spark-ML HOME WORK   ---------------------------
===============================================================================

When creating ML models, the conceot of efficiency has two sides:
    (1) the time dedicated by the analyst to build the model
    (2) the computer tima and resources needed by the final model

Efficiency is a combination of both

In this project, you are asked to optimize the second. Spark is the best tool
to build models over massive datasets

If you need to create Spark+Python Machine Learning models that "run fast" on the
cluster, you must avoid using Python code or working with RRD+python. Try to use
the already existing methods that do what you need (do not reinvent the wheel)

Therefore try to use the implemented object+methods inside the Spark SQL and ML
modules. They are very fast, because it is complied Java/Scala code. Try to
use: DataFrames, Feature Transfomers, Estimators, Pipelines, GridSearch, CV, ...

For this homework, you are asked to create a classification model that:
    (1) uses ALL variables in the dataset (homework TRAIN.xlsx) to predict label "loan_status"
    (2) your solution must be a python scripts that:
        (3.1) reads the "bank.csv" file, transform and select variables as you wish
            ( but start using use ALL)
        (3.2) tune the model and hyperparameters using gridsearch (using a minimun
                of 10 sets of hyperparameters ans using 3 folds for validation)
        (3.3) compute the AUC for the test set
    (3) Your work will be evaluated under the following scoring schema
        (30%) a clean, clever and efficient use of the Python and Spark objects
                and methods
        (30%) timing that takes your code to run on my computer (I will time it)
        (40%) AUC on the test set (I will use my own train and test sets)

Enjoy it and best of luck!!

"""


#==============================================================================
# Read the Data
#==============================================================================

#start = time.time()
import pyspark.sql.types as typ

labels = [
        ('id', typ.IntegerType()),
        ('loan_amnt', typ.FloatType()),
        ('term', typ.StringType()),
        ('int_rate', typ.FloatType()),
        ('installment', typ.FloatType()),
        ('emp_length', typ.StringType()),
        ('home_ownership', typ.StringType()),  
        ('annual_inc', typ.FloatType()),
        ('purpose', typ.StringType()),
        ('title', typ.StringType()),
        ('state', typ.StringType()),
        ('delinq_2yrs', typ.IntegerType()),
        ('revol_bal', typ.FloatType()),
        ('revol_util', typ.StringType()),
        ('total_pymnt', typ.FloatType()),
        ('loan_status', typ.StringType())
]

## DEFINE THE SCHEMA
schema = typ.StructType( [typ.StructField(e[0], e[1], True) for e in labels] )

## Import as dataframe

loan_df = MySparkSession.read.csv("homework TRAIN.csv", 
                        header=True, 
                        schema=schema,sep=";",
                        nullValue='')

#loan_df.show(2)



#==============================================================================
# Clean/Preprocess the Data
#==============================================================================

## Function to mark ' - ' as missing
def changeToMissing(string):
        try:
            return float(string)
        except: 
            return None
            


import pyspark.sql.functions as func
change_spk = func.udf(changeToMissing, typ.FloatType())

loan_df = loan_df.withColumn('revol_util_parse', change_spk( func.col('revol_util')))
#loan_df.show(1)


############################
#### Drop NA
############################
# drop all rows with  missings
loan_df_droped = loan_df.dropna()




#==============================================================================
# Create Dummys
#==============================================================================
from pyspark.ml.feature import StringIndexer


#==============================================================================
# one-hot encoding
#==============================================================================

from pyspark.ml.feature import OneHotEncoder

# build indexer

categorical_columns = ['term', 'emp_length', 'home_ownership', 'purpose', 'state']
stringindexer_stages = [StringIndexer(inputCol=c, outputCol='stringindexed_' + c) for c in categorical_columns]
onehotencoder_stages = [OneHotEncoder(inputCol='stringindexed_' + c, outputCol='onehotencoded_' + c) for c in categorical_columns]
all_stages_transf1 = stringindexer_stages + onehotencoder_stages

## build pipeline model for transformation of Data
from pyspark.ml import Pipeline
pipeline = Pipeline(stages=all_stages_transf1)

## fit pipeline model
pipeline_mode = pipeline.fit(loan_df_droped)

## transform data
df_coded = pipeline_mode.transform(loan_df_droped)

## remove uncoded columns
selected_columns = ['onehotencoded_' + c for c in categorical_columns] + [
 'loan_amnt',
 'int_rate',
 'installment',
 'annual_inc',
 'delinq_2yrs',
 'revol_bal',
 'total_pymnt',
 'loan_status',
 'revol_util_parse']
df_coded = df_coded.select(selected_columns)


################
# Change to binary the variable to predict
###############3
stringIndexer = StringIndexer(inputCol="loan_status", outputCol="LOANIndex")
si_model = stringIndexer.fit(df_coded)
td = si_model.transform(df_coded)


from pyspark.ml.feature import VectorAssembler
assembler = VectorAssembler(
    inputCols=[
  'onehotencoded_term',
 'onehotencoded_emp_length',
 'onehotencoded_home_ownership',
 'onehotencoded_purpose',
 'onehotencoded_state',
 'loan_amnt',
 'int_rate',
 'installment',
 'annual_inc',
 'delinq_2yrs',
 'revol_bal',
 'total_pymnt',
 'revol_util_parse'],
    outputCol="features")

df_features = assembler.transform(td)


#==============================================================================
# Build the model with Grid Paramerters and CV
#==============================================================================

#Split into training and testing data
(train, test) = df_features.randomSplit([0.8, 0.2])


from pyspark.ml.classification import GBTClassifier
gbt = GBTClassifier(seed=30, labelCol="LOANIndex", \
                featuresCol="features", maxMemoryInMB=512	
)

#==============================================================================
# Build the Evaluator
#==============================================================================

from pyspark.ml.evaluation import BinaryClassificationEvaluator
evaluator = BinaryClassificationEvaluator(rawPredictionCol="prediction", \
                    labelCol="LOANIndex",metricName="areaUnderROC")

#==============================================================================
# Training and Evaluation
#==============================================================================

from pyspark.ml.tuning import CrossValidator, ParamGridBuilder


pipeline_gbt = Pipeline(stages=[gbt])
paramGrid_gbt = ParamGridBuilder() \
    .addGrid(gbt.maxDepth, [ 6,10]) \
    .addGrid(gbt.maxIter, [3]) \
    .addGrid(gbt.maxBins, [32,64])\
    .addGrid(gbt.stepSize, [0.7, 0.5, 0.6])\
     .build()

crossval_gbt = CrossValidator(estimator = pipeline_gbt,
                          estimatorParamMaps = paramGrid_gbt,
                          evaluator = evaluator,
                          numFolds =3)  # use 3+ folds in practice

# Run cross-validation, and returns the best model.
cvModel_gbt= crossval_gbt.fit(train)

# NOW WE will predict over test set
predictionCV_gbt = cvModel_gbt.transform(test)
print(evaluator.evaluate(predictionCV_gbt))
#print ('It took', time.time()-start, 'seconds.')


