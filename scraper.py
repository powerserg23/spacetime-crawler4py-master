import re
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from simhash import Simhash, SimhashIndex
from utils.response import Response
from collections import Counter
from urllib.parse import urlparse
from bs4 import BeautifulSoup

TokenList = []
MaxTokens = 0
MaxURL = ""
UniqueUrl=set()
Subdomains = dict()
prevsimHash=''
updateOutput = 1500

def scraper(url, resp):
    global prevsimHash
    global updateOutput
    if resp.status!=200 or resp.raw_response.content==None:
        return[]
    links = extract_next_links(url, resp)
    if updateOutput == 1:
        getOutput()
        updateOutput = 1500
    else:
        updateOutput -=1
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    # Implementation required.

    webResponse = BeautifulSoup(resp.raw_response.content, 'html.parser')

    # tokenizes the web contents and checks if the page has more tokens then the max. If it is greater the max number
    # is updated and the MaxURL is changed to the new url
    global MaxTokens
    global MaxURL
    urlTokens=tokenize(webResponse.getText())

    if len(urlTokens) > MaxTokens:
        MaxTokens = len(urlTokens)
        MaxURL = url

    # takes the list of tokens created and adds them to the DBDictionary
    #updateDBD(urlTokens)
    tags = webResponse.find_all('a')
    urlList = []
    for tag in tags:
        tempURL = tag.get('href')
        # if the url is emtpy
        if tempURL == None:
            continue
        # finds the fragment tag in url and takes it off
        possibleInd = tempURL.find('#')
        if possibleInd != -1:
            tempURL = tempURL[:possibleInd]
            urlList.append(tempURL)
            # note: i think you can remove the if statement on lines 70 and 75 because sets dont have repeats
        else:
            urlList.append(tempURL)

    return urlList



def tokenize(resp):
    # Tokenizes a text file looking for an sequence of 2+ alphanumerics while ignoring stop words
    urlTokens = []

    exclusionWords = {'january','jan','feb','february','march','mar','april','apr','may','june','jun','jul','july'\
                      ,'aug','august','september','sept','aug','august','october','oct','november','nov','dec','december','monday',\
                      'mon','tues','tuesday','wednesday','wed','thursday','thurs','friday','fri','sat','saturday','sun','sunday'}

    myTokenizer = RegexpTokenizer(r'\w+{2,}')
    tempTokens = myTokenizer.tokenize(resp)
    sw = stopwords.words('english')
    # checks if tokens are stop words, if not then it adds it to the list of tokens
    for tokens in tempTokens:
        checkToken = tokens.lower()
        if checkToken not in sw and checkToken not in exclusionWords and not re.search(r"[0-9]",checkToken):
            urlTokens.append(checkToken)
        else:
            continue
    updateDBD(urlTokens)
    return urlTokens


def updateDBD(Tokens):
    # Take list of tokens updates the DBDictionary to include these tokens
    global TokenList
    TokenList.extend(Tokens)


def print50(wordList):
    #prints the frequencies of the list of words that it is passed
    freqList=Counter(wordList)
    finalList = []

    for word in freqList.most_common(50):
        finalList.append(word[0])
    return finalList



def updateSubdomains(UniqueUrl):
    #takes the set containing all unique urls and builds a dictionary that hold subdomain as key
    # and number of page as value
    global Subdomains
    Subdomains.clear()
    for url in UniqueUrl:
        parsed = urlparse(url)
        Subdomains[parsed.hostname] = Subdomains.get(parsed.hostname, 0) + 1


def getOutput():
    # returns a string with the answer to all four problems TO DO make it output to a textfile
    global UniqueUrl, MaxURL, MaxTokens
    output = "1. Number of unique pages found: " + str(len(UniqueUrl)) + "\n\n"
    output += "2. Longest page in terms of number of words is " + str(MaxURL) + " with " + str(
        MaxTokens) + " words total\n\n"
    output += "3. 50 most common words in order of most frequent to least frequent are \n   "
    commonWords = print50(TokenList)
    for word in commonWords:
        output += word + "\n  "
    output += "\n4. Subdomains found: \n"
    updateSubdomains(UniqueUrl)
    for key, value in Subdomains.items():
        output += "   subdomain name: " + str(key) + ", pages found: " + str(value) + "\n"
    try:
        f = open("output.txt", "x")
    except:
        f = open("output.txt", "w")
    finally:
        f.write(output)
        f.close()



def is_valid(url):
    global prevsimHash
    global UniqueUrl


    try:
        parsed = urlparse(url)
        if parsed.hostname==None or parsed.netloc==None:
            return False
        validDomains=[".ics.uci.edu","cs.uci.edu",".informatics.uci.edu",".stat.uci.edu",\
               "today.uci.edu/department/information_computer_sciences"]
        if parsed.scheme not in set(["http", "https"]) or (url.find("?") != -1) or (url.find("&") != -1):
            return False
        if any(dom in parsed.hostname for dom in validDomains) \
            and not re.search(r"(css|js|bmp|gif|jpe?g|ico"
                              + r"|png|tiff?|mid|mp2|mp3|mp4"
                              + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
                              + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
                              + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
                              + r"|epub|dll|cnf|tgz|sha1|php|z"
                              + r"|thmx|mso|arff|rtf|jar|csv"
                              + r"|rm|smil|wmv|swf|wma|zip|rar|gz|ppt|pptx|ppsx"
                              + r"|january|february|march|april|may|june|july"
                              + r"|august|september|october|november|december"
                              + r"|jan|feb|mar|apr|jun|jul|aug|sep|oct|nov|dec"
                              + r"|docs|docx|css|js|blog|page|calendar|archive|events|event)", parsed.path.lower()):
            if url in UniqueUrl:
                return False
            else:
                return True
        else:
            return False


    except TypeError:
        print("TypeError for ", parsed)
        raise
