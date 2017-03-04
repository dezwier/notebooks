import sqlite3
import time
import urllib
import re
import zlib
import string
from datetime import datetime, timedelta
import dateutil.parser as parser 
import math
#   import graphlab

print "This program creates an sqlite-file for tidy data.\n"



####################################
## FUNCTIONS FOR FEATURE MUTATION ##
####################################

# Converts dates from March 10, 2001 format to 2001-03-10 format
def dateconverter(oldate):
    date = datetime.strptime(oldate, "%B %d, %Y")
    year = str(date.year); month = date.month; day = date.day
    if month < 10: month = "0" + str(month)
    else: month = str(month)
    if day < 10:day = "0" + str(day)
    else: day = str(day)
    date = year + "-" + month + "-" + day
    return date

def textconverter(text):
    text = re.sub('\[(.*?)\]', '', text)            # Removes all [] parts
    text = re.sub('\((.*?)\)', '', text)            # Removes all () parts
    text = re.sub('\|', '', text)                   # Removes all |
    text = text.lower()                      # Change text to lowercase
    text = re.sub('[^(a-z)]| ', ' ', text)   # Change all not-text to spaces
    text = re.sub(' +',' ',text)                    # Remove all redundant spaces
    text = text.strip()                             # Remove outer whitespace
    return text

######################################
## ADD MUTATED DATA TO TIDY DATASET ##
######################################

# Collect relevant data from the raw dataset
conn = sqlite3.connect('/Users/desiredewaele/Google Drive/Datasets/rawdata.sqlite')
conn.text_factory = str
cur = conn.cursor()
cur.execute('''SELECT text FROM Speeches ORDER BY id''')
        
# Create a database for the tidy data
conn_2 = sqlite3.connect('/Users/desiredewaele/Google Drive/Datasets/tidydata.sqlite')
conn_2.text_factory = str
cur_2 = conn_2.cursor()
cur_2.execute('''DROP TABLE IF EXISTS Speeches ''')
cur_2.execute('''CREATE TABLE IF NOT EXISTS Speeches (id INTEGER PRIMARY KEY, president TEXT, date TEXT, speech TEXT, text TEXT UNIQUE, keywords TEXT)''')

# Mutate the collected raw data, and insert in tidy dataset
print "Process raw data and insert in tidy data..."
cur.execute('''SELECT president, date, speech, text FROM Speeches ORDER BY id''')
count = 0
for row in cur:
    president = row[0]
    date = dateconverter(row[1])
    speech = row[2]
    text = textconverter(row[3])

    count += 1
    cur_2.execute('INSERT INTO Speeches (president, date, speech, text) VALUES (?, ?, ?, ?)', (president, date, speech, text))
    if count % 500 == 0:
        conn_2.commit()
        print str(count) + " speeches processed."
conn_2.commit()
print str(count) + " speeches processed."
print "Tidy dataset complete."

# Close the connections
cur.close()
cur_2.close()