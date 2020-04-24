import re
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer


from urllib.parse import urlparse
from bs4 import BeautifulSoup

TokenList = []
MaxTokens = 0
MaxURL = ""
UniqueUrl=set()

def scraper(url, resp):
    if resp.status!=200:
        return[]
    else:
        links = extract_next_links(url, resp)
        return [link for link in links if is_valid(link)]


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
        possibleInd=''
        tempURL=tag.get('href')
        if tempURL==None:
            continue
        possibleInd=tempURL.find('#')
        if possibleInd!=-1:
            urlList.append(tempURL)
            depURL=tempURL[:possibleInd]
            if depURL not in UniqueUrl:
                UniqueUrl.add(depURL)
        else:
            urlList.append(tempURL)
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
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]) or (url.find("?") != -1):
            return False
        if '.ics.uci.edu' in parsed.netloc\
            and not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz|ppt|pptx"
            + r"|docs|docx|css|js|)$", parsed.path.lower()):
            return True
        else:
            return False

    except TypeError:
        print("TypeError for ", parsed)
        raise
