
# coding: utf-8

# # Lily

# ## Load Data

# In[71]:

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import warnings
warnings.filterwarnings('ignore')


# In[72]:

data = pd.read_csv("dataframe.csv", delimiter="|")
data.tail()


# ## Handle Missing Values

# In[73]:

print(data.isnull().sum().sum(), 'Before deleting anything')
data.dropna(axis=1, thresh=1000, inplace=True)
print(data.isnull().sum().sum(), 'After deleting columns with less than 1000 non values')
data.flagStudent = data.flagStudent.apply(lambda x: 0 if np.isnan(x) else 1)
data.flagRetired = data.flagRetired.apply(lambda x: 0 if np.isnan(x) else 1)
data.flagHouseOwner = data.flagHouseOwner.apply(lambda x: 0 if np.isnan(x) else 1)
data.flagHomeTenant = data.flagHomeTenant.apply(lambda x: 0 if np.isnan(x) else 1)
data.flagValueProperty = data.flagValueProperty.apply(lambda x: 0 if np.isnan(x) else 1)
data.flagLandlord = data.flagLandlord.apply(lambda x: 0 if np.isnan(x) else 1)
data.flagWealthyRegion = data.flagWealthyRegion.apply(lambda x: 0 if np.isnan(x) else 1)
print(data.isnull().sum().sum(), 'After changing binary columns')
data.dropna(axis=0, inplace=True)
print(data.isnull().sum().sum(), 'After deleting rows with any missing values')

targets = data.loc[:,'monthlyIncomeReal']
data.drop('monthlyIncomeReal', axis=1, inplace=True)

data.drop(['ID', 'zipcode', 'crmId', 'referenceTime', 'originalSourceIds', 'lastName', 'firstName', 'middleName',
             'streetAddress', 'state', 'emailAddress', 'phoneNumber', 'occupation', 'resCity', 'resCountry'],
             axis=1, inplace=True)


# In[74]:

data.tail()


# In[65]:

dummies, nDummies = [], []
for i in range(len(data.columns)):
    possibleValues = len(data.iloc[:,i].unique())
    feature = data.columns[i]
    featureType = data.iloc[:,i].dtype
    if featureType == 'object' and possibleValues in range(2, 10):
        dummies.append(feature)
        print(feature, data.iloc[:,i].unique())
    else:
        nDummies.append(feature)


# In[67]:

from sklearn.model_selection import train_test_split
trainX, validX, trainY, validY = train_test_split(data, targets, train_size=0.7, random_state=100)


# In[132]:

from sklearn_pandas import DataFrameMapper
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import LabelBinarizer

mapper = DataFrameMapper(
    [(a, StandardScaler()) for a in nDummies] +
    [(d, LabelBinarizer()) for d in dummies]
)


# In[134]:

from sklearn2pmml import PMMLPipeline
from sklearn.linear_model import Ridge

pipe = PMMLPipeline([
    ("mapper", mapper),
    ("regressor", Ridge(alpha=2))
])


# In[140]:

pipe.fit(data, targets)
print(pipe.score(trainX, trainY))
print(pipe.score(validX, validY))



# In[142]:

from sklearn2pmml import sklearn2pmml
sklearn2pmml(pipe, "MetricModelDemo.xml")

