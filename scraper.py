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

# list containing every token found on every pages tokenized
TokenList = []
# Maxtokens is the highest number of tokens found on a url, and MaxURL is the url which has the highest number of tokens
MaxTokens = 0
MaxURL = ""
# this is a set containing every URL that we have checked, not including url fragments
UniqueUrl=set()
# a dictionary containing the subdomain as a key and the amount of pages in that subdomain as the value
Subdomains = dict()
prevsimHash=''
# a counter that increments down to 1 before being reset, used in updating the output file containing our report.
updateOutput = 1500

def scraper(url, resp):
    global prevsimHash
    global updateOutput
    # if the response status isn't 200 or the page is empty, we don't check it
    if resp.status!=200 or resp.raw_response.content==None:
        return[]
    links = extract_next_links(url, resp)

    # updateOutput acts as a counter and, after every 1500 pages checked, updates our output file answers to the report
    if updateOutput == 1:
        getOutput()
        updateOutput = 1500
    else:
        updateOutput -=1
    # checks the list of urls found on a page using the is_valid function to decide whether or not to return each url
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    # Implementation required.

    webResponse = BeautifulSoup(resp.raw_response.content, 'html.parser') #make sure to change back to resp.raw_response.content

    # tokenizes the web contents and checks if the page has more tokens then the max. If it is greater the max number
    # is updated and the MaxURL is changed to the new url
    global MaxTokens
    global MaxURL
    urlTokens=tokenize(webResponse.getText())

    # compares current webpage's token count to the highest count to see if we have a new highest num of tokens
    if len(urlTokens) > MaxTokens:
        MaxTokens = len(urlTokens)
        MaxURL = url

    # takes the list of tokens created and adds them to the DBDictionary
    #updateDBD(urlTokens)
    tags = webResponse.find_all('a')
    urlList = []
    for tag in tags:
        tempURL = tag.get('href')
        # if the url is emtpy don't check it
        if tempURL == None:
            continue
        # if it finds the fragment tag in url it takes it off, the it appends the url to our list of urls to search
        possibleInd = tempURL.find('#')
        if possibleInd != -1:
            tempURL = tempURL[:possibleInd]
            urlList.append(tempURL)
        else:
            urlList.append(tempURL)

    return urlList



def tokenize(resp):
    # Tokenizes a text file looking for an sequence of 2+ alphanumerics while ignoring stop words
    urlTokens = []
    # exclusionWords is a list of words that we dont want to include in out list of tokens. These include months and
    # days, which appear in disproportionatly high numbers
    exclusionWords = {'january','jan','feb','february','march','mar','april','apr','may','june','jun','jul','july'\
                      ,'aug','august','september','sept','aug','august','october','oct','november','nov','dec','december','monday',\
                      'mon','tues','tuesday','wednesday','wed','thursday','thurs','friday','fri','sat','saturday','sun','sunday'}

    # tokenizes with the pattern '[a-z]{2,}' which finds two letters or more. We excluded numbers because there were
    # no instances where we found numbers to have important meaning
    myTokenizer = RegexpTokenizer('[a-z]{2,}')
    tempTokens = myTokenizer.tokenize(resp)
    sw = stopwords.words('english')

    # this loop checks if tokens are stop words or words we want to exclude, if not then it adds it to the token list
    for tokens in tempTokens:
        checkToken = tokens.lower()
        if checkToken not in sw and checkToken not in exclusionWords:
            urlTokens.append(checkToken)
        else:
            continue
    # updataDBD adds all tokens found on this page to our master list containing all tokens found on all pages
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
        if 'ics.uci.edu' in parsed.netloc.lower():
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
                              + r"|docs|docx|css|js|blog|page|calendar|archive|events|event|date)", parsed.path.lower())\
            and not re.match(r'\/(19|20)[0-9]{2}/|\/(19|20)[0-9]{2}$|\/(19|20)[0-9]{2}-[0-9]{1,2}|\/[0-9]{1,2}-(19|20)[0-9]{2}|[0-9]{1,2}-[0-9]{1,2}-(19|20)[0-9]{2}',parsed.path.lower()):
            if url in UniqueUrl:
                return False
            else:
                UniqueUrl.add(url)
                return True
        else:
            return False


    except TypeError:
        print("TypeError for ", parsed)
        raise