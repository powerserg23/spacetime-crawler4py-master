import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup

DBDictionary = dict()
MaxTokens = 0
MaxURL = ""

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]


def extract_next_links(url, resp):
    # Implementation required.
    if resp.status is not 200:
        return []
    webResponse = BeautifulSoup(resp.raw_response.content, 'html.parser')

    # tokenizes the web contents and checks if the page has more tokens then the max. If it is greater the max number
    # is updated and the MaxURL is changed to the new url
    global MaxTokens
    global MaxURL
    urlTokens = tokenize(webResponse)
    if len(urlTokens) > MaxTokens:
        MaxTokens = len(urlTokens)
        MaxURL = url

    # takes the list of tokens created and adds them to the DBDictionary
    updateDBD(urlTokens)

    tags = webResponse.find_all('a')
    urlList = []
    for tag in tags:
        urlList.append(tag.get('href'))
    return urlList


def tokenize(resp):
    # Tokenizes a text file looking for an sequence of 2+ alphanumerics while ignoring stop words
    regularPattern = '[A-Za-z0-9]{2,}'
    stopWords = {"a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't",
                 "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", "by",
                 "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't",
                 "down", "during", "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't", "have",
                 "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here", "here's", "hers", "herself", "him",
                 "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't",
                 "it", "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself", "no", "nor",
                 "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out",
                 "over", "own", "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so",
                 "some", "such", "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then",
                 "there", "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this", "those",
                 "through", "to", "too", "under", "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll",
                 "we're", "we've", "were", "weren't", "what", "what's", "when", "when's", "where", "where's", "which",
                 "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would", "wouldn't", "you", "you'd",
                 "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves"}
    tokenList = []
    wordlist = re.findall(regularPattern, resp.get_text())
    templist = wordlist
    for word in templist:
        if word in stopWords:
            wordlist.remove(word)
    tokenList.extend(wordlist)
    return tokenList



def updateDBD(Tokens):
    # Take list of tokens updates the DBDictionary to include these tokens
    global DBDictionary
    for word in Tokens:
        DBDictionary[word] = DBDictionary.get(word, 0) + 1


def Top50(wordDict):
    # takes the DBDictionary and prints the 50 most common words in dictionary
    sortedWords = sorted(wordDict.items(), key=lambda x: 0 - x[1])
    n = 50;
    for word, val in sortedWords:
        if n > 0:
            print("<" + word + "> <" + str(wordDict[word]) + ">")
            n -= 1
        else:
            break

def is_valid(url):
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print("TypeError for ", parsed)
        raise
