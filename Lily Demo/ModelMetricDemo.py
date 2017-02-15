# Import Data
import pandas as pd
data = pd.read_csv("dataframe.csv", delimiter="|")

# Handle Missing Values
data.dropna(axis=1, thresh=30000, inplace=True)
data.dropna(axis=0, inplace=True)

# Extrac Features
variables = list(data.describe())
data = data[variables]
data.drop('ID', axis=1, inplace=True)

# Training and validation
import random
data = data.sample(frac=1)
breakpoint = int(len(data)*0.7)
training = data.iloc[:breakpoint,]
validation = data.iloc[breakpoint:,]

# Get Format Right
trainTarget = training[['monthlyIncomeReal']]
validTarget = validation[['monthlyIncomeReal']]
training.drop('monthlyIncomeReal', axis=1, inplace=True)
validation.drop('monthlyIncomeReal', axis=1, inplace=True)

# Train Model
lm = PMMLPipeline([("regression", LinearRegression())])
lm.fit(training, trainTarget)

# Write to PMML
from sklearn2pmml import sklearn2pmml
sklearn2pmml(lm, "MetricModelDemo.pmml", with_repr=True, debug=True)