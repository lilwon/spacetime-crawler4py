import re
from urllib.parse import urlparse, urldefrag, urljoin
from bs4 import BeautifulSoup as bs

import requests 

def scraper(url, resp): # will receive a URL and the response given by the caching server for the requested URL (the webpage) 
    # links = extract_next_links(url, resp)
    if resp.status in [200, 201, 202, 203, 205, 206]:
        links = extract_next_links(url,resp)
        return [link for link in links if is_valid(link)] # scrapped list of URLs from the page 

    return list()

# only focus on resp.status 200-203, 205 & 206
def extract_next_links(url, resp):
    # links to return  
    links = []

    # resp.raw_response.content will give content of HTML webpage     
    # some web pages will not have a raw_response

    if resp.raw_response is None:
        return list()

    # Beautiful soup will do it's magic and extract data into lmxl 
    # and then helps us get all the tags from lxml file
    soup = bs(resp.raw_response.content, 'lxml') 

    # get anchor tag for all websites
    # tags = soup.find_all('a')
    # still get string queries like "?=..." 
    for anchor_tag in soup.find_all('a'):
        temp = anchor_tag.get('href') 
        defrag,_ = urldefrag(temp)
        # creates absolute paths 

        if is_valid(urljoin(url,defrag)):
            links.append(urljoin(url,defrag))



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

        # aren't being detected.. from wics pages
        if "?action" in url:
            return False

        # ?replytocom from evoke website.. we already see the comments in the evoke link 
        if re.match(r".*(\?replytocom).*$", parsed.path):
            return False

        # ?share= from wics share with google, twitter, etd..
        if "?share=" in url:
            return False

        # wp-content = evoke website 

        # doku.php from swiki and wp-content = img , event(s) from wics calendar pg 
        # ....eppstein/pix/ so many.. pictures.. horrible.
        # looks for all events, so hack.uci events arent seen
        if re.search(r"(/doku.php/|/pix/|/events/|/event/)", parsed.path):
            return False 
        
        # block any url that contains calendar
        if re.match(r"^.*calendar.*$", parsed.path):
            return False

        #  some websites have PDF in middle of url = becomes a trap
        # must re.match or something 
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

