import queue
import urllib.request
import time
from bs4 import BeautifulSoup
import re

depth = 1;
MAX_DEPTH = 6;
MAX_PAGES = 1000;
#crawl limit is 1000
CRAWL_COUNTER = 0
#frontier with maximum depth 6
frontier = queue.Queue();
seed = "/wiki/Time_zone";

html_doc=""

file_count=1

urls = set()
url_file = open("urls.txt",'w+')

#TODO: add seed to frontier
#TODO: unique urls -- change queue to set

frontier.put("depth-inc")

# find all urls in content block and put in the frontier queue
def enqueue_frontier():

    soup = BeautifulSoup(html_doc,'html.parser');
    for table in soup.find_all("table") :
        table.decompose()
    toc = soup.find(id="toc")
    toc.decompose()
    content = soup.find(id="mw-content-text")
    #soup with content-block



    #retrieve urls in content-block
    for link in content.find_all('a') :
        url = link.get('href');

        #if href tag's value is None or wiki's main page, ignore and continue
        if(url == None or url == "/wiki/Main_Page" or url in urls): #or complete_url in frontier
            continue
            #if href has a value
        else:


            #only get urls that match with /wiki/ to avoid crawling
            # external links
            matchWikiArticles = re.match("^/wiki/.*", url)
            # print("matchWikiArticles",matchWikiArticles)
            #filter administrative links
            adm_regex =  re.match("^/wiki/.*:.*", url)
            # print(url)
            # print("adm_regex ",adm_regex)
            disambiguation_regex = re.match(".*(disambiguation)",url)

            #if match is found
            if  matchWikiArticles is not None and adm_regex is None and disambiguation_regex is None:

                #filter section links
                if  '#' not in url :

                    # print("match if")
                    #create the full URL name
                    complete_url = "https://en.wikipedia.org" + url
                    new_url = redirected_url(complete_url)
                    print("pushed",new_url)

                    #copy docs
                    copy_docs(new_url)
                    #add the URL to frontier

                    frontier.put(new_url)
                    urls.add(new_url)
                    #write url to urls.txt
                    url_file.write(new_url)
                    url_file.write("\n")

#filter

#Function to fetch resource
def open_url(url):
    # wait 2 seconds
    time.sleep(2)
    complete_url = "https://en.wikipedia.org" + url
    # Send get request to url
    with urllib.request.urlopen(complete_url) as response:
        global html_doc
        html_doc = response.read()




#Function to fetch resource
def redirected_url(url):
    # wait 2 seconds
    time.sleep(1)
    # Send get request to url
    with urllib.request.urlopen(url) as response:
        redirected_url = response.geturl()
        print("original url",url)
        print("REDIRECTED to", redirected_url)
        if  redirected_url != url :
            print("original url",url)
            print("REDIRECTED to", redirected_url)
        return redirected_url



# copy html content as raw txt file
def copy_docs(url) :
    with open(str(CRAWL_COUNTER)+".txt",'w+') as html_file:
        html_file.write(str(html_doc))







def crawl(url,depth):

                            global CRAWL_COUNTER
                            CRAWL_COUNTER+=1;
                            print ("depth",depth);

                            #write depth to urls.txt
                            url_file.write("Depth: ")
                            url_file.write(str(depth))
                            url_file.write("\n")
                            #TO-DO:trim url to get filename
                            #url.split("wiki/")[1]
                            if not(frontier.empty()) and depth <= MAX_DEPTH and CRAWL_COUNTER <= MAX_PAGES :

                                #open url
                                open_url(url)
                                #push all urls in url to the frontier queue
                                enqueue_frontier()

                                #pop head of queue
                                temp = frontier.get()
                                # print("temp",temp)
                                # if head of queue is not None, crawl with same depth
                                if(temp != "depth-inc"):
                                    crawl(temp,depth)

                                    #increase depth and crawl if head of queue is None
                                else:
                                    #put None at end of queue
                                    frontier.put("depth-inc")
                                    depth += 1
                                    new_temp = frontier.get()
                                    # print("new_temp",new_temp)
                                    crawl(new_temp,depth)

urls.add(seed)
crawl(seed,depth);
