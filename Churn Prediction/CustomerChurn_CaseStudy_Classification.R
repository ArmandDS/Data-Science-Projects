##########################################
### Customer Analytics Case Study
#     used for classification 
##########################################

# Objective: predict customer churn in a Telco company
# churn: the customer ends their relationship or service with a company
# That's costly problem currently when it's difficult to gain new customers, hence the focus is on reducing customer churn
# The objective is to predict customer churn and explain what features relate to customer churn
# I.e. the company needs to understand who is leaving and why

rm(list = ls())

library(tidyverse)
library(forcats)
library(mice)
library(GGally)
library(MASS)
library(caret)

# Dataset from IBM Watson Telco Dataset: https://www.ibm.com/communities/analytics/watson-analytics-blog/guide-to-sample-datasets/
# This Telco company is concerned about the number of customers leaving their landline business for cable competitors
churnData <- read.csv('ChurnData.csv')
str(churnData)

# The dataset includes information about:
#   Customers who left within the last month: The column is called Churn
#   Services that each customer has signed up for: phone, multiple lines, internet, online security, online backup, device protection, tech support, and streaming TV and movies
#   Customer account information: how long they’ve been a customer, contract, payment method, paperless billing, monthly charges, and total charges
#   Demographic info about customers: gender, age range, and if they have partners and dependents

summary(churnData)

### Missing-values

md.pattern(churnData)
# 11 NAs in TotalCharges. Insignificant. We can drop them or impute them with 0 (not charged yet) 

# Remove NAs and ID column
churnData <- churnData %>%  dplyr::select(-customerID) %>% drop_na()

churnData$SeniorCitizen = as.factor(churnData$SeniorCitizen)

### Some exploratory analysis and feature engineering

table(churnData$Churn)

summary(churnData)

# 26% of customers left the company in the last month

# We will change “No internet service” to “No” for columns: 
# “OnlineSecurity”, “OnlineBackup”, “DeviceProtection”, “TechSupport”, “streamingTV”, “streamingMovies”.
for(i in c(9:14)) {
  churnData[,i] <- fct_collapse(churnData[,i], No = c("No","No internet service"))
}

# We will change “No phone service” to “No” for column “MultipleLines”
churnData$MultipleLines <- fct_collapse(churnData$MultipleLines, No = c("No","No phone service"))


# Split data into training and testing sets using the caret package
in_train <- createDataPartition(churnData$Churn, p = 0.8, list = FALSE)  # 80% for training
training <- churnData[ in_train,]
testing <- churnData[-in_train,]
nrow(training)
nrow(testing)

# Numeric vs categorical plot:
ggplot(training, aes(x=Churn, y=tenure)) +  geom_boxplot(fill="blue") 
# customers with more months with the company have less chances to leave

# The same, different view:
ggplot(training, aes(tenure)) + geom_density(aes(group=Churn, colour=Churn, fill=Churn), alpha=0.1) +xlab("tenure")
# customers with less than 2 years in the company tend to leave more
# customers with more than 5 years in the company tend to stay

# Numeric vs categorical plot:
ggplot(training, aes(MonthlyCharges)) + geom_density(aes(group=Churn, colour=Churn, fill=Churn), alpha=0.1) +xlab("Monthly charges")
# customers paying less than 30/month tend to stay
# those paying more than 60/month tend to leave more

# Categorical vs categorical
# Three views:
table(training$Churn, training$Contract)

ggplot(training, aes(x=Churn,fill = Contract)) + geom_bar()

ggplot(training, aes(x=Contract,fill = Churn)) + geom_bar()
# a long-term contract (1-2 years) decreases chance of leaving

# More categorical vs categorical

ggplot(training, aes(x=Churn,fill = OnlineSecurity)) + geom_bar()

ggplot(training, aes(x=Churn,fill = InternetService)) + geom_bar()

# easy ways to see relationships with categorical variables

ggcorr(training, label = T)
ggpairs(training[,c(18,17,8)],label=T)

X = model.matrix(Churn ~ ., data=training)[,-1]  # skip column of ones
ggcorr(X, label=T, label_alpha=T, digits=1)

h.col = findCorrelation(cor(X), cutoff=0.8)  
colnames(X)[h.col]

# there are some variables with high correlations; should skip them
# training2 = training[,-c(h.col)]
# testing2 = testing[,-c(h.col)]


### Probabilistic-learning models 

ctrl <- trainControl(method = "none")

#ctrl <- trainControl(method = "repeatedcv", 
#                     number = 5)

# We have many predictors, hence use penalized logistic regression
lrFit <- train(Churn ~ ., 
               method = "glmnet",
               family = "multinomial",
               tuneGrid=data.frame(alpha = 0.5, lambda=0.001),
               data = training,
               preProcess = c("center", "scale"),
               trControl = ctrl)
print(lrFit$bestTune)
lrPred = predict(lrFit, testing)
confusionMatrix(testing$Churn,lrPred)

# LDA (with penalties)
ldaFit <- train(Churn ~ ., 
               method = "sparseLDA", #"sda", 
               tuneGrid=data.frame(NumVars = 12, lambda=0.01),
               #tuneGrid=data.frame(diagonal = T, lambda=0.01),# for "sda"
               data = training,
               preProcess = c("center", "scale"),
               trControl = ctrl)
print(ldaFit$bestTune)
ldaPred = predict(ldaFit, testing)
confusionMatrix(testing$Churn,ldaPred)

### Risk learning

# there are customers who provide more income to the company than others
# hence, we should focus on them if their churn probability is high

# churn probability
ldaProb = predict(ldaFit, testing, type="prob")

# Money at risk:
Risk.customer.year=testing$MonthlyCharges*ldaProb$Yes*12
hist(Risk.customer.year,col="lightblue")

# We should focus on customers with money.at.risk>500 eur
sum(Risk.customer.year>500)/length(Risk.customer.year)
# around 20% of customers would incur high losses
# who are them?

sort.risk = sort(Risk.customer.year,decreasing=T,index.return=T)
# Most risky positions:
head(sort.risk$x)
# Most risky customers:
head(sort.risk$ix)

# offer them a discount or better service, etc.

### ROC curve

# ROC curve shows true positives vs false positives in relation with different thresholds
# y-axis = Sensitivity (TP)
# x-axis = Specificity (1-FP)

library(pROC)
plot.roc(testing$Churn, ldaProb[,2],col="darkblue", print.auc = TRUE,  auc.polygon=TRUE, grid=c(0.1, 0.2),
         grid.col=c("green", "red"), max.auc.polygon=TRUE,
         auc.polygon.col="lightblue", print.thres=TRUE)

# Seems a threshold around 0.3 is reasonable

# Very convenient to plot ROC by groups (factors)
plot.roc(testing$Churn[testing$SeniorCitizen == "0"], ldaProb[testing$SeniorCitizen == "0",2],print.auc = TRUE, col = "blue", print.auc.col = "blue",print.auc.y = 0.98, print.auc.x = 0.6)
plot.roc(testing$Churn[testing$SeniorCitizen == "1"], ldaProb[testing$SeniorCitizen == "1",2],add=T,print.auc = TRUE, col = "green", print.auc.col = "green",print.auc.y = 0.7, print.auc.x = 0.8)


### Cost-sensitive learning

# Features increasing chances of leaving:
#  Tenure (especially < 12 Months)
#  Internet Service = Fiber Optic
#  Payment Method = Electronic Check

# Features decreasing chances of leaving:
#  Contract = two ear
#  Total/monthly charges 

# Accuracy is ok, around 80%. But are the two errors equally important?
# The company will be concerned with balancing: 
#   i) the cost of a customer who is leaving and has not been targeted, 
#   ii) the cost of inadvertently targeting customers that are not planning to leave 
# Usually, the first cost (associated with false negatives) is the most dangerous for the company

# Hence, how can we reduce that cost (at the expense of increasing the other cost)?

# Assume the following (company's data):
#  Cost of true negatives is 0: the model is correctly identified a happy customer, no need to offer discounts
#  Cost of false negatives is 500: most problematic error, we lose the customer 
#  Cost of false positives is 100: retention incentive
#  Cost of true positives is 100: retention incentive

# Cost matrix:
#                 no yes
# predicted no     0 500
# predicted yes  100 100

# Unit cost is then:
#  0*TN + 100*FP + 500*FN + 100*TP

cost.unit <- c(0, 100, 500, 100)

# Naive classifier (no analytics knowledge): 
# cost = 0*.74 + 100*0 + 500*.26 +  + 100*0
#      = 130eur/customer on average

# Basic LDA or Logistic Reg. classifier (some analytics knowledge): 

# Logistic regression:
CM = confusionMatrix(lrPred, testing$Churn)$table
CM = CM/sum(CM)
cost = sum(as.vector(CM)*cost.unit)
cost
# saving per customer around 40-50 eur

# LDA:
CM = confusionMatrix(ldaPred, testing$Churn)$table
CM = CM/sum(CM)
cost = sum(as.vector(CM)*cost.unit)
cost
# saving per customer around 40-50eur

# Advanced classifier (more analytics knowledge): 

threshold = 0.4

lrProb = predict(lrFit, testing, type="prob")[(nrow(testing)+1):(2*nrow(testing)),]
lrPred = rep("No", nrow(testing))
lrPred[which(lrProb[,2] > threshold)] = "Yes"
confusionMatrix(testing$Churn,lrPred)

ldaProb = predict(ldaFit, testing, type="prob")
ldaPred = rep("No", nrow(testing))
ldaPred[which(ldaProb[,2] > threshold)] = "Yes"
confusionMatrix(testing$Churn,ldaPred)

# Logistic regression:
CM = confusionMatrix(lrPred, testing$Churn)$table
CM = CM/sum(CM)
cost = sum(as.vector(CM)*cost.unit)
cost
# saving per customer around 50eur

# LDA:
CM = confusionMatrix(ldaPred, testing$Churn)$table
CM = CM/sum(CM)
cost = sum(as.vector(CM)*cost.unit)
cost
# saving per customer around 50eur


# Cost-sensitive classifier (expert level): 

cost.i = matrix(NA, nrow = 20, ncol = 10)
# 20 replicates for training/testing sets for each of the 10 values of threshold

j <- 0
for (threshold in seq(0.05,0.5,0.05)){

  j <- j + 1
  
  for(i in 1:20){
    
    # partition data intro training (75%) and testing sets (25%)
    d <- createDataPartition(churnData$Churn, p = 0.8, list = FALSE)
    # select training sample
    
    training <- churnData[d,]
    testing  <- churnData[-d,]  
    
    # consider the lda classifier, but any other classifier should be considered
    ldaFit <- train(Churn ~ ., 
                    method = "sda", 
                    data = training,
                    preProcess = c("center", "scale"),
                    trControl = ctrl)
    
    # posterior probabilities and classification by threshold
    ldaProb = predict(ldaFit, testing, type="prob")
    ldaPred = rep("No", nrow(testing))
    ldaPred[which(ldaProb[,2] > threshold)] = "Yes"
    
    CM = confusionMatrix(ldaPred, testing$Churn)$table
    CM = CM/sum(CM)
    cost = sum(as.vector(CM)*cost.unit)
    cost
    
    cost.i[i,j] <- cost
    
  }
}

boxplot(cost.i, main = "Threshold selection",
        ylab = "unit cost",
        xlab = "threshold value",
        names = seq(0.05,0.5,0.05),col="royalblue2",las=2)

# values around 0.25 are reasonable
# savings around 62eur/customer on average (respect to naive classifier)
# savings around 17eur/customer on average (respect to basic Bayes rule)

# Can you imagine the savings with just 100,000 customers?
  
# Even more advanced ideas:

# instead of using a fixed cost matrix for each customer, we could consider a 
# different matrix for each, depending on the value of each customer for the company

# besides threshold, other methods have other parameters that can be tuned
# to reduce even more the cost. For instance:
# prior probabilities in LDA or penalty parameters in shrinkage methods
# or mtry in RFs, etc.
# This is computationally expensive

# Ensemble learning: combine the best classifiers and form a meta-classifier
# This is quite computationally expensive if cost-sensitive learning is taken into account

