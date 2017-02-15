
# coding: utf-8

# # Generating Keywords on Textual Data

# In[1]:

import sqlite3
import pandas as pd
import numpy as np
import math
from datetime import datetime, timedelta
import re
import sys
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')


# # Data Processing
# ## Load Raw Data
# First, the data is loaded into a Pandas dataframe.

# In[2]:

conn = sqlite3.connect('rawdata.sqlite')
rawData = pd.read_sql("select * from Speeches", conn)
rawData = rawData[rawData.president.str.contains(
    'Barack Obama|William J. Clinton|George W. Bush', regex=True)].sort_values('date', ascending=False)
#rawData = rawData[rawData.speech.str.contains('Weekly Address')]
rawData.tail()


# ## Tidy Data
# The data is raw and we would like to tidy it up. The first function changes the dates into a sortable format. The second one strips the speech from capital letters, non-letter symbols and redundant whitespace.

# In[3]:

def dateconverter(oldate):
    date = datetime.strptime(oldate, "%B %d, %Y")
    year = str(date.year); month = date.month; day = date.day
    if month < 10: month = "0" + str(month)
    else: month = str(month)
    if day < 10:day = "0" + str(day)
    else: day = str(day)
    date = year + "-" + month + "-" + day
    return date


# In[4]:

def textconverter(text):
    text = re.sub('\((.*?)\)', '', text)     # Removes all () parts
    text = re.sub('\[(.*?)\]', '', text)     # Removes all [] parts
    text = text.lower()                      # Change text to lowercase
    text = re.sub('[^(a-z)]| ', ' ', text)   # Change all not-text to spaces
    text = re.sub(' +',' ',text)             # Remove all redundant spaces
    text = text.strip()                      # Remove outer whitespace
    return text


# We select the features we'll be working with, and apply both functions.

# In[5]:

tidyData = rawData[['president','date','speech','text']]
tidyData.date = tidyData.date.apply(dateconverter)
tidyData.text = tidyData.text.apply(textconverter)
tidyData = tidyData.sort('date', ascending=True).reset_index(drop=True)
tidyData.tail(20)

# In[6]:

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer

a = CountVectorizer()
b = CountVectorizer(ngram_range=(2, 2))
c = CountVectorizer(ngram_range=(1, 3))
d = TfidfVectorizer(sublinear_tf=True)
e = TfidfVectorizer(sublinear_tf=True, ngram_range=(1,3))
f = TfidfVectorizer(sublinear_tf=True, ngram_range=(1,3))

#onegrams = pd.DataFrame(a.fit_transform(tidyData.text).toarray(), columns=a.get_feature_names())
#twograms = pd.DataFrame(b.fit_transform(tidyData.text).toarray(), columns=b.get_feature_names())
#trigrams = pd.DataFrame(c.fit_transform(tidyData.text).toarray(), columns=c.get_feature_names())
onetfidf = pd.DataFrame(d.fit_transform(tidyData.text).toarray(), columns=d.get_feature_names())
#twotfidf = pd.DataFrame(e.fit_transform(tidyData.text).toarray(), columns=e.get_feature_names())
#tritfidf = pd.DataFrame(f.fit_transform(tidyData.text).toarray(), columns=f.get_feature_names())


# In[7]:

onetfidf.tail()


# In[8]:

def getTopValues(s):
    tmp = s.order(ascending=False)[:10]
    return tuple(tmp.index) #dict(zip(tmp.index, tmp))

# In[9]:

tidyData['onetfidf'] = onetfidf.apply(getTopValues, axis=1)


tidyData[tidyData.onetfidf.apply(lambda x: True if "isil" in x else False)]


# In[ ]:

tidyData.onetfidf[1326]


# ## Model Building

# In[10]:

from sklearn.model_selection import train_test_split
Xtrain, Xtest, Ytrain, Ytest = train_test_split(
    onetfidf.as_matrix(), tidyData.president, train_size=0.7, random_state=20)


# In[11]:

from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB

clf = LogisticRegression()
gnb = GaussianNB()

clf.fit(Xtrain, Ytrain)
gnb.fit(Xtrain, Ytrain)


# In[12]:

print(clf.score(Xtest, Ytest))
print(gnb.score(Xtest, Ytest))


# In[13]:

print(clf.score(Xtrain, Ytrain))
print(gnb.score(Xtrain, Ytrain))


# In[14]:

print(clf.predict(Xtest[:10]))
print(gnb.predict(Xtest[:10]))


# ## Pipeline for Cross Validation
# The goal here is to search for the optimal hyper-parameters.

# In[15]:

from sklearn.model_selection import train_test_split
Xtrain, Xtest, Ytrain, Ytest = train_test_split(tidyData.text, tidyData.president, train_size=0.7, random_state=20)


# In[16]:

from sklearn.pipeline import make_pipeline
pipe = make_pipeline(TfidfVectorizer(), LogisticRegression(random_state=1))


# In[17]:

from sklearn.model_selection import GridSearchCV
pams = {'logisticregression__C': [100, 1000], 'tfidfvectorizer__stop_words': ['english', None]}
grid = GridSearchCV(pipe, param_grid=pams, cv=5, n_jobs=2)


# In[18]:

grid.fit(Xtrain, Ytrain)


# In[19]:

print(grid.best_params_)
print(grid.score(Xtest, Ytest))
print(grid.score(Xtrain, Ytrain))
print(grid.predict(Xtest[:10]))

# ## Pipeline for PMML

# In[26]:

from sklearn.model_selection import train_test_split
Xtrain, Xtest, Ytrain, Ytest = train_test_split(tidyData.text, tidyData.president, train_size=0.7, random_state=20)

# In[34]:

len(Ytrain)

# In[35]:

from sklearn2pmml import PMMLPipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

pipe = PMMLPipeline([
    ("TFIDF", TfidfVectorizer()),
    ("Model", LogisticRegression(C=1000, random_state=1))
])
pipe.fit(Xtrain, Ytrain)


# In[36]:

print(pipe.score(Xtest, Ytest))
print(pipe.score(Xtrain, Ytrain))
print(pipe.predict(Xtest[:10]))


# In[37]:

from sklearn2pmml import sklearn2pmml
sklearn2pmml(pipe, "Speeches.xml")

