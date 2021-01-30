import re
from urllib.parse import urlparse, urldefrag, urljoin
from bs4 import BeautifulSoup as bs
from collections import defaultdict
from nltk.tokenize import WordPunctTokenizer 

import requests
import pickle 

# didn't include haven --> haven't, won --> won't
stop_words = ['a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 
             'and', 'any', 'are', 'as', 'at', 'be', 'because', 'been', 'before', 
             'being', 'below', 'between', 'both', 'but', 'by', 'cannot', 'could',
             'could', 'couldn', 'did', 'didn', 'do', 'does', 'doesn', 'doing', 
             'do', 'does', 'doesn', 'doing', 'don', 'down', 'during', 'each',
             'few', 'for', 'from', 'further', 'had', 'hadn', 'has', 'hasn', 'have',
             'having', 'he', 'here', 'hers', 'herself', 'him', 'himself', 'his',
             'how', 'i', 'if', 'in', 'into', 'is', 'isn', 'it', 'its', 'itself',
             'me', 'more', 'most', 'mustn', 'my', 'myself', 'no', 'nor', 'not',
             'of', 'off', 'on', 'once', 'or', 'other', 'ought', 'ours', 'our',
             'only', 'ourselves', 'out', 'over', 'own', 'same', 'she', 'should',
             'shouldn', 'so', 'some', 'such', 'than', 'that', 'the', 'their',
             'theirs', 'them', 'themselves', 'then', 'there', 'these', 'they',
             'this', 'those', 'through', 'to', 'too', 'under', 'until', 'up', 
             'very', 'was', 'wasn', 'we', 'were', 'weren', 'what', 'when', 
             'where', 'which', 'while', 'who', 'whom', 'why', 'with', 'would',
             'wouldn', 'you', 'your', 'yours', 'yourself', 'yourselves' ]

contract_endings = [ 't', 'd', 'll', 've', 's', 'n', 're', 'm']

def scraper(url, resp): # will receive a URL and the response given by the caching server for the requested URL (the webpage) 
    # links = extract_next_links(url, resp)
    if resp.status in [200, 201, 202, 203, 205, 206]:
        links = extract_next_links(url,resp)
        return [link for link in links if is_valid(link)] # scrapped list of URLs from the page 

    return list()


word_length = dict()
current_longest = ""
most_common = defaultdict(int)

# only focus on resp.status 200-203, 205 & 206
def extract_next_links(url, resp):
    # links to return  
    links = []
    word_num = []

    # resp.raw_response.content will give content of HTML webpage     
    # some web pages will not have a raw_response
    if resp.raw_response is None:
        return list()

    # Beautiful soup will do it's magic and extract data into lmxl 
    # and then helps us get all the tags from lxml file
    soup = bs(resp.raw_response.content, 'lxml') 


    tokens = WordPunctTokenizer().tokenize(soup.get_text())

    for word in tokens:
        if word.isalnum() and word not in stop_words and word not in contract_endings:
            word_num.append(word.lower())


    word_length[url] = len(word_num)
    with open("longest_page.txt","w") as longest:
        '''
        for key,val in word_length.items():
            longest.write(key+" --> " + str(val) + " words!\n")
        '''
        current_longest = max(word_length,key = word_length.get)
        longest.write("Longest page in terms of the number of words --> " + current_longest + "\n")

    # "w" instead of "a"
    with open ("most_common.txt", "w") as common:
        for i in word_num:
            most_common[i] += 1
        common_list = sorted(most_common.items(), key=lambda x:x[1])
        final_list = common_list[:51]
        for i in final_list:
            common.write(str(i)+"\n")

    # get anchor tag for all websites
    # tags = soup.find_all('a')
    # still get string queries like "?=..." 
    for anchor_tag in soup.find_all('a'):
        temp = anchor_tag.get('href') 
        defrag,_ = urldefrag(temp)
        # creates absolute paths 

        new_link = urljoin(url, defrag)
        if is_valid(new_link): # would check again when added but it would crawl the page too!
            links.append(new_link)

    longest.close()
    return list(links) 


# is_valid checks if url is good or not. 
# so it avoids all traps and stuff
def is_valid(url):
    try:
        parsed = urlparse(url)

        if parsed.scheme not in set(["http", "https"]):
            return False

        # only get links that we can crawl pertaining to assignment.. 
        if not re.match(r"^(\w*.)(ics.uci.edu|cs.uci.edu|informatics.uci.edu|stat.uci.edu)", parsed.netloc):
            return False

        if re.match(r"^(today.uci.edu)", parsed.netloc ):
            if not re.match(r"^(\/department/information_computer_sciences\/).*", parsed.path):
                return False


        # ?replytocom from evoke website.. we already see the comments in the evoke link 
        # parsed.path doesn't detect ?replytocom
        if re.search(r'(\?action|\?share|\?replytocom)', url):
            return False

        # doku.php from swiki and wp-content = img , event(s) from wics calendar pg 
        # ....eppstein/pix/ so many.. pictures.. horrible.
        # looks for all events, so hack.uci events arent seen
        if re.search(r"(/doku.php/|/pix/|/events/|/event/|/figs/)", parsed.path):
            return False 
        
        # block any url that contains calendar
        if re.match(r"^.*calendar.*$", parsed.path):
            return False

        # websites with these extensions in the middle
        #  some websites have PDF in middle of url = becomes a trap
        if re.match(
            r".*(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz).*$", parsed.path):
            return False

        # only removes url with paths ending in these extensions
        # added php, ppsx, odc, apk,  extensions
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv|z|php"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz|ppsx|odc|apk|war|img)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise

