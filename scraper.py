import re
from urllib.parse import urlparse, urldefrag
from bs4 import BeautifulSoup as bs

import requests

def scraper(url, resp): # will receive a URL and the response given by the caching server for the requested URL (the webpage) 
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)] # scrapped list of URLs from the page 

def extract_next_links(url, resp):
    # html_page = "https://www.ics.uci.edu"

    links = []
    # 204 = Response successful, no content
    if ( resp.status < 200 or resp.status > 400 or resp.status == 204): 
        return list()# these response are bad

    # resp.raw_response.content will give content of HTML webpage     
    # data = resp.raw_response.content 

    # some websites have no raw_response.content.. is that 404 error?

    # list of links to return

    # Beautiful soup will do it's magic and extract data into lmxl 
    # and then helps us get all the tags from lxml file
    soup = bs(resp.raw_response.content, 'lxml') 

    # get anchor tag for all websites
    tags = soup.find_all('a')

    # still get string queries like "?=..." 
    for tag in tags:
        temp = tag.get('href')
        defrag,_ = urldefrag(temp)

        links.append(defrag)

    return list(links) 


''' 
    urllib.parse -> parses scheme, netloc, path, params, query, fragment
    https://docs.python.org/3/library/urllib.parse.html

'''

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

        #  some websites have PDF in middle of url = becomes a trap
        # must re.match or something 
        # Ex of trap in middle of URL: Downloaded http://www.informatics.uci.edu/files/pdf/InformaticsBrochure-March2018
        if "pdf" in url:
            return False

        # query strings that aren't being detected..
        if "?action" in url:
            return False

        # 3 ifs below removes the evoke..comment thread traps -_-
        if "#comment" in url:
            return False
        
        if "#respond" in url:
            return False

        if "?replytocom" in url:
            return False

        # manually block wics events calendar
        if re.search(r"(\bevent\b)", parsed.path):
            return False

        if re.search(r"(\bevents\b)", parsed.path):
            return False

        # this only checks for urls ending in these extensions
        # added php, ppsx, and odc extensions
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv|z|php"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz|ppsx|odc)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise
