##########################################
### Credit-Scoring Case Study
#      used for classification 
##########################################

rm(list = ls())

library(tidyverse)
library(MASS)
library(e1071) 
library(caret)

### Motivation
# When a bank receives a loan application, based on the applicant's profile the bank has to make a decision regarding whether 
# to go ahead with the loan approval or not. Two types of risks are associated with the bank's decision:
#
#   If the applicant has a good credit risk, i.e. is likely to repay the loan, then not approving the loan to the client results in a loss of business to the bank
#   If the applicant has a bad credit risk, i.e. is not likely to repay the loan, then approving the loan to the client results in a financial loss to the bank

# To minimize loss from the bank's perspective, the bank needs a decision rule regarding who to give approval of the loan and who not to.
# An applicant's demographic and socio-economic profiles are considered by loan managers before a decision is taken regarding his/her loan application.

# The German Credit Data contains data on 20 variables and the classification whether an applicant is considered a Good or a Bad credit 
# risk for 1000 loan applicants. 
# A predictive model developed on this data is expected to provide a bank manager guidance for making a decision whether to approve a loan to a prospective applicant based on his/her profiles.

# Data can be found in the UCI data repository
# read comma separated file into memory
dataCredit<-read.csv("GermanCredit.csv", header = TRUE, sep = ",")

names(dataCredit)
# Variable 'Creditability' contains the labels: It is common in credit scoring to
# classify bad accounts as those which have ever had a 60 day delinquency or worse (in
# mortgage loans often 90 day plus is often used)

# Features or explanatory variables or predictors:
#
# Account Balance,
# Duration of Credit (month),
# Payment Status of Previous Credit,
# Purpose,
# Credit Amount,
# Value Savings/Stocks,
# Length of current employment,
# Instalment per cent,
# Sex & Marital Status,
# Guarantors,
# Duration in Current address,
# Most valuable available asset,
# Age (years),
# Concurrent Credits,
# Type of apartment,
# No of Credits at this Bank,
# Occupation,
# No of dependents,
# Telephone,
# Foreign Worker

str(dataCredit)

summary(dataCredit)

# Most of the variables are indeed factors or categories:
dataCredit$Creditability = as.factor(dataCredit$Creditability)
# the same for the other categorical variables
indexCat = c(1,2,4,5,7,8,9,10,11,12,13,15,16,17,18,19,20,21)
for(j in indexCat) dataCredit[,j]=as.factor(dataCredit[,j])

str(dataCredit)

### Some exploratory analysis

summary(dataCredit)

table(dataCredit$Creditability)
# 700 good loans, 300 bad loans

# see how Creditability is distributed along some variables:
table(dataCredit$Creditability, dataCredit$Account.Balance)
ggplot(dataCredit, aes(x=Creditability,fill = Account.Balance)) + geom_bar()
# most of the good loans (348) are in very good account balances (label=4)
# the opposite happens with bad balances (label=1)


table(dataCredit$Creditability, dataCredit$Payment.Status.of.Previous.Credit)
ggplot(dataCredit, aes(x=Creditability,fill = Payment.Status.of.Previous.Credit)) + geom_bar()
# most of the good loans (361+243) have a good previous status (2=Paid up, 4=Previous credit paid)

table(dataCredit$Creditability, dataCredit$No.of.dependents)
ggplot(dataCredit, aes(x=Creditability,fill = No.of.dependents)) + geom_bar()
# here the proportions are similar, no much influence

# Now with boxplots for numeric variables:
boxplot(dataCredit$Duration.of.Credit..month. ~ dataCredit$Creditability, col="lightblue",xlab = "Creditability", ylab = "Duration of credit month")
boxplot(dataCredit$Credit.Amount ~ dataCredit$Creditability, col="lightblue", xlab = "Creditability", ylab = "Credit Amount")
boxplot(dataCredit$Age..years. ~ dataCredit$Creditability, col="lightblue", xlab = "Creditability", ylab = "Age (years)")

# Split data into training and testing sets using the caret package
in_train <- createDataPartition(dataCredit$Creditability, p = 0.8, list = FALSE)  # 80% for training
training <- dataCredit[ in_train,]
testing <- dataCredit[-in_train,]
nrow(training)
nrow(testing)

### Logistic regression:
logit.model <- glm(Creditability ~ ., family=binomial(link='logit'), data=training)
summary(logit.model)

# Note some variables are not statistically significant
# Account.Balance is highly significant, and also Credit.Amount, and also credit history
# Remember: log(odds) = ln(p/(1-p)) = b1*x1 + b2*x2 + ... + bp*xp 
# That means since Account.Balance4 is a dummy variable, having that balance increases
# the log odds by 1.8, while a month increase in the Duration of Credit decreases the 
# log odds by -0.0252
# Finally, note a higher credit amount has also a negative effect on creditability

# We should skip some irrelevant variables and maintain the most important ones

# make predictions (posterior probabilities)
probability <- predict(logit.model,newdata=testing, type='response')
head(probability)
prediction <- ifelse(probability > 0.5,1,0)
head(prediction)

# Performance: confusion matrix
confusionMatrix(prediction, testing$Creditability)

# The 0.75 accuracy on the test set is ok, but not too good compared with
# a naive classifier predicting always Creditability=1, with accuracy=70% 
# Moreover, this accuracy depends on the specific split of the data 

### Bayes classifiers

# LDA
lda.model <- lda(Creditability ~ ., data=training, prior = c(.3, .7))
lda.model
probability = predict(lda.model, newdata=testing)$posterior
head(probability)
# here two columns
# Obtain prediction of creditability by factors
# We apply the Bayes rule of maximum probability
prediction <- max.col(probability)-1
head(prediction)
# It's equivalent to
prediction = predict(lda.model, newdata=testing)$class

# Performance: confusion matrix
confusionMatrix(prediction, testing$Creditability)

# Quadratic Discriminant Analysis (QDA)
qda.model <- qda(Creditability ~ ., data=training, prior = c(.3, .7))
qda.model
prediction = predict(qda.model, newdata=testing)$class

# Performance: confusion matrix
confusionMatrix(prediction, testing$Creditability)

# Naive Bayes (Gaussian and linear)
naive.model <- naiveBayes(Creditability ~ ., data=training, laplace=1, prior = c(.3, .7))
naive.model
prediction = predict(naive.model, newdata=testing)

# Performance: confusion matrix
confusionMatrix(prediction, testing$Creditability)

# Can we improve the business of the bank?

# classes are unbalanced
# losses are unbalanced
# at this moment, we have two choices to try: changes the prior probabilities, change the Bayes rule (max probability)

### Using Caret

# Each model can be automatically tuned and evaluated 
# In this case, we are goint to use 10 repeats of 5-fold cross validation
ctrl <- trainControl(method = "repeatedcv", 
                     repeats = 10,
                     number = 5)
# we can also choose bootstrap, LOOCV, etc.
# ctrl = trainControl(method = 'LGOCV', p = 0.8, number = 30)
#  means 30 repeated training/test splits

model = Creditability ~ .

# Split data into another training and testing set
train_index <- createDataPartition(dataCredit$Creditability, p = 0.8, list = FALSE)
dataCreditTrain <- dataCredit[train_index,]
dataCreditTest <- dataCredit[-train_index,]

glmFit <- train(model, 
                method = "glmnet", 
                family="binomial",
                data = dataCreditTrain,
                preProcess = c("center", "scale"),
                trControl = ctrl)
print(glmFit)
glmPred = predict(glmFit, dataCreditTest)
confusionMatrix(glmPred,dataCreditTest$Creditability)
glm_imp <- varImp(glmFit, scale = F)
plot(glm_imp, scales = list(y = list(cex = .95)))

ldaFit <- train(model, 
                # method = "lda", "lda2", "rda",
                method = "sda",
                data = dataCreditTrain,
                preProcess = c("center", "scale"),
                trControl = ctrl)
print(ldaFit)
ldaPred = predict(ldaFit, dataCreditTest)
confusionMatrix(ldaPred,dataCreditTest$Creditability)

qdaFit <- train(model, 
                method = "qda", 
                #method = "stepQDA", 
                data = dataCreditTrain,
                preProcess = c("center", "scale"),
                trControl = ctrl)
print(qdaFit)
qdaPred = predict(qdaFit, dataCreditTest)
confusionMatrix(qdaPred,dataCreditTest$Creditability)

# Naive Bayes (gaussian)
nbFit <- train(model, 
               #method = "nb", 
               method = "naive_bayes", 
               data = dataCreditTrain,
               preProcess = c("center", "scale"),
               trControl = ctrl)
print(nbFit)
nbPred = predict(nbFit, dataCreditTest)
confusionMatrix(nbPred,dataCreditTest$Creditability)


# Others:

# Naive Bayes (gaussian)
knnFit <- train(model, method = "knn", 
                data = dataCreditTrain,
                preProcess = c("center", "scale"),
                trControl = ctrl)
print(knnFit)
knnPred = predict(knnFit, dataCreditTest)
confusionMatrix(knnPred,dataCreditTest$Creditability)

svmFit <- train(model, method = "svmRadial", 
                data = dataCreditTrain,
                preProcess = c("center", "scale"),
                trControl = ctrl)
print(svmFit)
svmPred = predict(svmFit, dataCreditTest)
confusionMatrix(svmPred,dataCreditTest$Creditability)

rfFit <- train(model, method = "rf", 
               data = dataCreditTrain,
               preProcess = c("center", "scale"),
               tuneGrid = expand.grid(mtry = c(10,20,30)), 
               trControl = ctrl)
print(rfFit)
rfPred = predict(rfFit, dataCreditTest)
confusionMatrix(rfPred,dataCreditTest$Creditability)


# Can we improve the business of the bank?

#
### Incorporing economic impact
#

# If the bank is more worried about false Creditable loans (financial loss) 
# than false non-Creditable ones (loss of business), then
# in the confusion matrix, better to decrease the element (2,1) at the cost of increasing the (1,2)
# In that case, better to increase the threshold 

# Note in the naive-manager classifier, all loans are approved, the only error (30%) comes from the 
# false creditable loans (there are no false non-creditable loans)

# We can reduce the false positives by increasing the probability threshold

# partition data intro training (75%) and testing sets (25%)
d <- createDataPartition(dataCredit$Creditability, p = 0.8, list = FALSE)

# select training and testing samples
train<-dataCredit[d,]
test <-dataCredit[-d,]

model = Creditability ~ .

full.model <- lda(model, data=train, prior = c(.5, .5))

# posterior probabilities
full.pred = predict(full.model, test)$posterior
head(full.pred)

# probability threshold: increase the number and check the false positives decrease 
# (but the false negatives increase)
threshold = 0.4

Cred.pred = rep(0, nrow(test))
Cred.pred[which(full.pred[,2] > threshold)] = 1

# Produce a confusion matrix
confusionMatrix(Cred.pred, dataCredit$Creditability[-d])

# Note the overall performance (accuracy) is reduced 
# but now both errors are better balanced for the bank

# We can also change (in LDA) the prior probabilities 
p1=0.7
p0=1-p1
full.model <- lda(model, data=train, prior = c(p0, p1))

# posterior probabilities
full.pred = predict(full.model, test)$posterior
head(full.pred)

# probability threshold: increase the number and check the false positives decrease 
# (but the false negatives increase)
threshold = 0.5

Cred.pred = rep(0, nrow(test))
Cred.pred[which(full.pred[,2] > threshold)] = 1

# Produce a confusion matrix
confusionMatrix(Cred.pred, dataCredit$Creditability[-d])

# Note as we increase p1, the false positives decrease again

# Now with more specific economic effects.
# Assume the bank predicts an application to be credit-worthy and 
# it actually turns out to be credit worthy. That implies, for that application, 
# a 35% profit at the end of 5 years.
# On the other hand, if the application turns out to be a default, then the loss is 100%.
# If the bank predicts an application to be non-creditworthy, then the profit is 0% if the application
# turns out to be a default, but there is an opportunity loss (5% in 5 years) if the application 
# is really credit-worthy.

# Table of profits
#
#     Actual  0     1
#           -------------  
#  predicted  
#    0        0.0  -0.05
#    1       -1.0   0.35


# For instance, a naive manager would incur a profit per applicant of
# [0.0*0.0 - 1.0*0.3 - 0.05*0.0 + 0.35*0.7] = -0.055
# which is indeed a loss


profit.unit <- c(0.0, -1.0, -0.05, 0.35)

# profit per applicant for lda classifier with threshold 0.5 (last executed)
profit.applicant <- sum(profit.unit*table(Cred.pred, dataCredit$Creditability[-d])/length(Cred.pred))
profit.applicant
# If the average loan amount is 5000 euros, and there are over 10000 applicants in one month
# then
profit.applicant*5000*10000
# is the expected profit in 5 years

# But this is for threshold=0.6
# With this economic information, how to select the optimal threshold?

### Selecting the optimal threshold to give the loan

profit.i = matrix(NA, nrow = 100, ncol = 10)
# 100 replicates for training/testing sets for each of the 10 values of threshold

p1=0.7
p0=1-p1

j <- 0
for (threshold in c(0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85)){
#for (p1 in c(0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.75, 0.8, 0.9)){
    
  j <- j + 1
  
  for(i in 1:100){
    
    # partition data intro training (75%) and testing sets (25%)
    d <- createDataPartition(dataCredit$Creditability, p = 0.8, list = FALSE)
    # select training sample
    
    train<-dataCredit[d,]
    test <-dataCredit[-d,]  
    
    #p0=1-p1
    
    # consider the lda classifier, but any other classifier should be considered
    full.model <- lda(model, data=train, prior = c(p0, p1))
    
    # posterior probabilities
    full.pred = predict(full.model, test)$posterior
    
    #threshold = 0.5
    Cred.pred = rep(0, nrow(test))
    Cred.pred[which(full.pred[,2] > threshold)] = 1
    
    profit.applicant <- sum(profit.unit*table(Cred.pred, dataCredit$Creditability[-d])/length(Cred.pred))
    profit.i[i,j] <- profit.applicant
    
  }
}

boxplot(profit.i, main = "Threshold selection",
        ylab = "unit profit",
        xlab = "threshold value",names = c(0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85),col="royalblue2")

# values around 0.7 are reasonable

