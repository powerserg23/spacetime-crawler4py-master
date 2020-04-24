import re
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from simhash import Simhash, SimhashIndex
from utils.response import Response
from urllib.parse import urlparse
from bs4 import BeautifulSoup

TokenList = []
MaxTokens = 0
MaxURL = ""
UniqueUrl=set()
prevsimHash=''

def scraper(url, resp):
    global prevsimHash
    if resp.status!=200:
        return[]
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

#this get_features is being used from https://leons.im/posts/a-python-implementation-of-simhash-algorithm/
#to get the raw text from a html file to be able to compute the simhash function
def get_features(s):
    width = 3
    s = s.lower()
    s = re.sub(r'[^\w]+', '', s)
    return [s[i:i + width] for i in range(max(len(s) - width + 1, 1))]

def simhash(content):
    global prevsimHash
    if Simhash(prevsimHash).distance(Simhash(content))<=3:
        return False
    else:
        return True

def extract_next_links(url, resp):
    # Implementation required.

    webResponse = BeautifulSoup(resp.raw_response.content, 'html.parser')

    # tokenizes the web contents and checks if the page has more tokens then the max. If it is greater the max number
    # is updated and the MaxURL is changed to the new url
    global MaxTokens
    global MaxURL
    global UniqueUrl
    urlTokens=tokenize(webResponse.getText())

    if len(urlTokens) > MaxTokens:
        MaxTokens = len(urlTokens)
        MaxURL = url

    # takes the list of tokens created and adds them to the DBDictionary
    #updateDBD(urlTokens)
    tags = webResponse.find_all('a')
    urlList = []
    for tag in tags:
        tempURL=tag.get('href')
        #if the url is emtpy
        if tempURL==None:
            continue
        #finds the fragment tag in url and takes it off
        possibleInd=tempURL.find('#')
        if possibleInd!=-1:
            tempURL=tempURL[:possibleInd]
            urlList.append(tempURL)
            if tempURL not in UniqueUrl:
                UniqueUrl.add(tempURL)
        else:
            urlList.append(tempURL)
            if tempURL not in UniqueUrl:
                UniqueUrl.add(tempURL)

    return urlList



def tokenize(resp):
    # Tokenizes a text file looking for an sequence of 2+ alphanumerics while ignoring stop words
    urlTokens = []
    myTokenizer = RegexpTokenizer('\w+')
    tempTokens = myTokenizer.tokenize(resp)
    sw = stopwords.words('english')
    # checks if tokens are stop words, if not then it adds it to the list of tokens
    for tokens in tempTokens:
        checkToken = tokens.lower()
        if checkToken not in sw:
            urlTokens.append(checkToken)
        else:
            continue
    updateDBD(urlTokens)
    return urlTokens



def updateDBD(Tokens):
    # Take list of tokens updates the DBDictionary to include these tokens
    global TokenList
    TokenList.append(Tokens)

def print50(wordList):
    #prints the frequencies of the list of words that it is passed
    freqList=nltk.FreqDist(wordList)
    [print(word[0]) for word in freqList.most_common(50)]

def is_valid(url):
    global prevsimHash

    try:
        parsed = urlparse(url)
        if parsed.hostname==None or parsed.netloc==None:
            return False
        validDomains=[".ics.uci.edu","cs.uci.edu",".informatics.uci.edu",".stat.uci.edu",\
               "today.uci.edu/department/information_computer_sciences"]
        if parsed.scheme not in set(["http", "https"]) or (url.find("?") != -1) or (url.find("&") != -1):
            return False
        if any(dom in parsed.hostname for dom in validDomains) \
            and not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz|ppt|pptx"
            + r"|docs|docx|css|js|blog|page|calendar|archive)$", parsed.path.lower()) and not \
                re.search(r"(blog|page|calendar|archive|)",parsed.path.lower()):
            return True
        else:
            return False


    except TypeError:
        print("TypeError for ", parsed)
        raise
