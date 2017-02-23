import sqlite3
import urllib
from urlparse import urljoin
from urlparse import urlparse
from bs4 import BeautifulSoup



# Create a database for the raw data
conn = sqlite3.connect('rawdata.sqlite')
cur = conn.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS Speeches (id INTEGER PRIMARY KEY, president TEXT, \
date TEXT, speech TEXT, text TEXT UNIQUE, url TEXT UNIQUE)''')
cur.execute('''CREATE TABLE IF NOT EXISTS Links (speech TEXT, url TEXT UNIQUE, retrieved TEXT)''')



#########################################################
## Creating unretrieved speech links if none available ##
#########################################################

cur.execute('SELECT url FROM Links WHERE retrieved is NULL ORDER BY RANDOM() LIMIT 1')
row = cur.fetchone()

if row is None:
    choice = int(raw_input("Select the kind of speeches to retrieve:\n1. Custom collection \n2. Inaugural Addresses \n3. State of the Unions \n4. Weekly Addresses \n5. Fireside Chats \nEnter choice: "))
    
    if choice is 1:
        speechkind = raw_input("Give the kind of speeches: ")
        starturl = raw_input("Give the local path: ")
    elif choice is 2:
        speechkind = "Inaugural Address"
        starturl = "http://www.presidency.ucsb.edu/inaugurals.php"
    elif choice is 3:
        speechkind = "State of the Union"
        starturl = "http://www.presidency.ucsb.edu/sou.php"
    elif choice is 4:
        speechkind = "Weekly Address"
        year = raw_input("Enter a year: ")
        starturl = "http://www.presidency.ucsb.edu/satradio.php?year=" + str(year) + "&Submit=DISPLAY"
    elif choice is 5:
        speechkind = "Fireside Chat"
        starturl = "http://www.presidency.ucsb.edu/fireside.php"

    document = urllib.urlopen(starturl)
    html = document.read()
    if document.getcode() != 200: print "Error on page: ", document.getcode()
    if document.info().gettype() != 'text/html': print "Ignore non text/html page"

    print "\nRetrieving links to " + speechkind + "..."
    soup = BeautifulSoup(html, "lxml")
    tags = soup('a')
    
    new = 0 #Keeping track of old and new links
    old = 0
    for tag in tags:
        href = tag.get('href', None)
        if href is not None and "/ws/index.php?pid=" in href:
            
            #Mutate href to proper format
            if href.startswith(".."): href = "http://www.presidency.ucsb.edu" + href[2:]
            if choice is 1: href = href[:-9]

            # Add link if its not already in database
            cur.execute('SELECT url FROM Links WHERE url is ?', (href,))
            row = cur.fetchone()
            if row is None:
                new += 1
                print str(new) + ". Found link to " + speechkind + ": " + href
                cur.execute('INSERT OR IGNORE INTO Links (speech, url, retrieved) VALUES \
                            (?, ?, NULL)', (speechkind, href)) 
                conn.commit()
            else: old += 1
            
    if new != 0: print "Retrieved " + str(new) + " new links to a "+ speechkind
    if old != 0: print "Retrieved " + str(old) + " old links already in database\n"

else: print "Found unretrieved links."
        
        
        
#######################################################
## Retrieving speeches from unretrieved speech links ##
#######################################################

count = 0
while True:
    
    # Try to select an unretrieved link
    cur.execute('SELECT url,speech FROM Links WHERE retrieved is NULL ORDER BY RANDOM() LIMIT 1')
    try:
        row = cur.fetchone()
        url = row[0]
        speechkind = row[1]
    except:
        print 'No more unretrieved HTML pages found'
        break
    
    # Read selected speech link
    count += 1
    print str(count) + ". Retrieving " + row[1] + " from " + row[0]
    try:
        document = urllib.urlopen(url)
        html = document.read()
        if document.getcode() != 200: print "Error on page: ",document.getcode()
        if document.info().gettype() != 'text/html': print "Ignore non text/html page"
    except KeyboardInterrupt:
        print 'Program interrupted by user.'
        break
    except:
        print "Unable to retrieve or parse page",url
        print sys.exc_info()[0]
        break
        
    # Retrieve relevant pieces and add to database
    soup = BeautifulSoup(html, "lxml")
    president = soup.select('img[src^="http://www.presidency.ucsb.edu/images/names/"]')[0]['alt']
    date = soup.find(class_='docdate').contents[0]
    text = soup.find(class_="displaytext").get_text(" | ")
    title = soup.find(class_='paperstitle').contents[0]
    notes = soup.find(class_="displaynotes").get_text(" | ")
    
    cur.execute('INSERT OR IGNORE INTO Speeches (president, date, speech, text, url, title, notes) \
    VALUES (?, ?, ?, ?, ?, ?, ?)', (president, date, speechkind, text, url, title, notes)) 
    cur.execute('UPDATE Links SET retrieved = "yes" WHERE url = ?', (url,))
    conn.commit()
    
cur.close()




