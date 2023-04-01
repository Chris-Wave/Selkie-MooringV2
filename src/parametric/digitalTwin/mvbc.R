library("MBC")
library("broman")
library(car)
library(ggplot2)
#This script reads in the traininng and testing data split
#corrects the era5 data based on the m5 and uses the combined dataset - data that is common to both the series
#to correct the entire range of era5 data. 

#read in the combined time series
X_train <- read.csv('data/X-training.csv')
X_test <- read.csv('data/X-test.csv')
y_train <- read.csv('data/y-training.csv')
y_test <- read.csv('data/y-test.csv')

Xt <- data.matrix(X_train)[,-1]
yt <- data.matrix(y_train)[,-1]
Xte <- data.matrix(X_test)[,-1]
############################################
corrected <- R2D2(Xt, yt, Xte) #method fails
############################################

############################################
corrected <- MBCp(Xt, yt, Xte) #method fails due to reasons i can't fully understand in R just yet. 
############################################

############################################
corrected <- MBCn(Xt, yt, Xte) #method fails due to reasons i can't fully understand in R just yet. 
############################################