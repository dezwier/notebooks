import json
import sqlite3
from pprint import pprint
import math
import re

# State of the Union, Inaugural Address, Address to the Nation, Address to Congress, Address to the U.N., Address to a Forein Legislature, Farewell Address

##############################################
## FUNCTIONS TO GENERATE TF_IDFS FROM TEXTS ##
##############################################

# Strips a string from everything but text
def textconverter(text):
    text = re.sub('\[(.*?)\]', '', text)            # Removes all [] parts
    text = re.sub('-|\(|\)', ' ', text)             # Change - ( ) to spaces
    text = text.lower()                             # Change text to lowercase
    text = re.sub('[^(a-z)]| ', ' ', text)          # Change all not-text to spaces
    text = re.sub(' +',' ',text)                    # Remove all redundant spaces
    text = text.strip()                             # Remove outer whitespace
    return text

# Converts a string into a dictionary of wordcounts          
def wordcounter(text):
    wordcounts = dict()
    words = text.split()
    for word in words:
        wordcounts[word] = wordcounts.get(word,0) + 1
    return wordcounts

# Converts a list of texts to a list of tf_idf dictionaries
def tfidfcalculator(textlist, onlyfirst):
    totaldocs = len(textlist)
    wordcountlist = []
    for text in textlist:
        plaintext = textconverter(text)
        wordcounts = wordcounter(plaintext)
        wordcountlist.append(wordcounts)        
        
    tf_idf = []
    docswithworddict = dict()
    count = 0
    for dicto in wordcountlist:
        totalwords = sum(dicto.itervalues())
        tf_idftext = dict()
        for word, wordcount in dicto.iteritems():
            if word not in docswithworddict:
                docswithworddict[word] = 0
                for dicto in wordcountlist:
                    if word in dicto: docswithworddict[word] +=1
            if len(word) > 3: tf_idftext[word] = (wordcount / float(totalwords)) * math.log(totaldocs / float(docswithworddict[word]))
        count += 1
        if onlyfirst: return tf_idftext
        if count % 500 == 0 or count == totaldocs: print "Calculated tf_idfs for words in " + str(count) + " texts."
        tf_idf.append(tf_idftext)   
    return tf_idf

## Writes a list of dictionaries into a JSON file
#def jsonwriter(filename, listo):
#    fhand = open(filename,'w')
#    fhand.write("[")
#    countdoc = 0
#    for dicto in listo:
#        countdoc +=1
#        fhand.write("{")
#        count = 0
#        for key, value in dicto.iteritems():
#            count += 1
#            fhand.write('"' + key + '": ' + str(value))
#            if count != len(dicto) : fhand.write(", ")
#        fhand.write("}")
#        if countdoc != len(listo): fhand.write(",\n")
#    fhand.write( "]")
#    fhand.close()
#    print "List of dictionaries written in " + filename + ".\n"



#####################################################
## COLLECT RELEVANT SPEECHES AND CALCULATE TF_IDFS ##
#####################################################

# Choose which speeches to select
president = raw_input("Give any president: ")
speech = raw_input("Give any speech kind: ")
date = raw_input("Give any date: ")
identity = raw_input("Give an id: ")

# Collect the relevant speeches from tidy data
conn = sqlite3.connect('tidydata.sqlite')
conn.text_factory = str
cur = conn.cursor()
    
if president != "" or speech != "" or date != "" or id != "":
    curstring = "SELECT text FROM Speeches"
    if president != '': curstring += " WHERE (president is '" + re.sub(", ", "' OR president is '", president) + "')"
    if speech != '' and president != '': curstring += " AND (speech is '" + re.sub(", ", "' OR speech is '", speech) + "')"
    if speech != '' and president == '': curstring += " WHERE (speech is '" + re.sub(", ", "' OR speech is '", speech) + "')"
    if len(date) > 10: moredates = "BETWEEN "
    else: moredates = "is "
    if date != '' and (president != '' or speech != ''): curstring += " AND (date " + moredates + "'" + re.sub(", ", "' AND '", date) + "')"    
    if date != '' and (president == '' and speech == ''): curstring += " WHERE (date " + moredates + "'" + re.sub(", ", "' AND '", date) + "')"    
    if identity != '': curstring = "SELECT text FROM Speeches WHERE id = " + identity

    cur.execute(curstring)

    # Concatenate all speeches of interest
    textofinterest = ''
    count = 0
    for row in cur:
        textofinterest += (' ' + row[0])
        count += 1
    print "Speeches of interest found", str(count)
    alltexts = []
    alltexts.append(textofinterest)

    # Collect all other speeches
    cur.execute("SELECT text FROM Speeches WHERE text NOT IN (" + curstring + ")")
    count = 0
    for row in cur:
        alltexts.append(row[0])
        count += 1
    print "Counter speeches found", str(count)

    # Apply tfidfcalculator, with speech(es) of interest at index 0,
    tfidfs = tfidfcalculator(alltexts, True)



    ##################################################
    ## WRITE JSFILE OF SORTED TFIDFS FOR WORD CLOUD ##
    ##################################################

    # Find the top 100 words
    words = sorted(tfidfs, key = tfidfs.get, reverse = True)
    print "Top ten keywords:", words[:10]

    # Spread the font sizes across 20-100 based on the tfidf
    bigsize = 80
    smallsize = 20

    highest = None
    lowest = None
    for w in words[:100]:
        if highest is None or highest < tfidfs[w]:
            highest = tfidfs[w]
        if lowest is None or lowest > tfidfs[w]:
            lowest = tfidfs[w]

    fhand = open('wordcloud.js','w')
    fhand.write("wordcloud = [\n")
    first = True
    for k in words[:100]:
        if not first: fhand.write( ",\n")
        first = False
        size = tfidfs[k]
        size = (size - lowest) / float(highest - lowest)
        size = int((size * bigsize) + smallsize)
        fhand.write("{text: '"+k+"', size: "+str(size)+"}")
    fhand.write( "\n];\n")

    print "Output written to wordcloud.js"
    print "Open wordcloud.htm in a browser to view a wordcloud.\n"



################################################
## CALCULATE ALL TFIDFS AND GENERATE KEYWORDS ##
################################################

choice = raw_input("Add top ten keywords to all texts in tidy dataset (y/n)? ")

if choice == "y":
    # Add all texts to a list, calculate tfidfs
    cur.execute("SELECT text FROM Speeches ORDER BY id")
    alltexts = []
    for row in cur:
        alltexts.append(row[0])
    alltfidfs = tfidfcalculator(alltexts, False)
    
    count = 0
    for tfidf in alltfidfs:
        sorted_words = sorted(alltfidfs[count].items(), key=lambda x: x[1], reverse=True)
        keywords = ""
        for word in sorted_words[:10]:
            keywords += ("{}, ".format(word[0]))
        count += 1
        curstring = 'UPDATE Speeches SET keywords = "' + keywords + '"' + ' WHERE id = ' + str(count)
        cur.execute(curstring)
        if count % 500 == 0 or count == len(alltfidfs):
            conn.commit()
            print "Keywords added to database for " + str(count) + " texts."