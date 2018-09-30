import queue
import urllib.request
import time
import os
from bs4 import BeautifulSoup
import re

class Crawler:
    #TODO: redirect url removal
    def __init__(self,file,seed,dir) :
        #crawl limit is 1000
        self.CRAWL_COUNTER = 0
        self.depth = 1;
        self.MAX_DEPTH = 6;
        self.MAX_PAGES = 1000;
        self.seed = seed
        self.html_doc=""
        self.urls = set()
        os.mkdir(dir)
        self.dir = dir
        self.copy_dir = dir+"/copies/"
        os.mkdir(self.copy_dir)
        self.url_file = open(dir+file,'w+')
        self.frontier = queue.Queue();
        #write seed url to file
        # print("write seed",seed)
        self.write_url(seed,self.depth)


    #write url to file
    def write_url(self,url,depth) :
        self.url_file.write("Depth: ")
        self.url_file.write(str(depth))
        self.url_file.write("\n")
        self.url_file.write(url)
        self.url_file.write("\n")


    #method to fetch resource
    def open_url(self,url):
        time.sleep(1)
        # print("Opening URL ",url)
        with urllib.request.urlopen(url) as response:
            # get contents of resource into html_doc
            self.html_doc = response.read()

    #Function to fetch resource
    def redirected_url(self,url):
        # wait 2 seconds
        time.sleep(1)
        # Send get request to url
        with urllib.request.urlopen(url) as response:
            redirected_url = response.geturl()
            # print("original url",url)
                # print("REDIRECTED to", redirected_url)
                # if  redirected_url != url :
                # print("original url",url)
                # print("REDIRECTED to", redirected_url)
        return redirected_url

    # copy html content as raw txt file
    #TO-DO:trim url to get filename
    def copy_docs(self,url,doc) :
            file_name = url.split("wiki/")[1]
            file_name = file_name.replace("/","_")
            file_name = file_name.replace("*","_")
            with open(self.copy_dir+file_name+".txt",'w+',encoding="utf8") as html_file:
                html_file.write(str(doc))

    #retreive only relevant urls
    def filter_urls(self):
        soup = BeautifulSoup(self.html_doc,'html.parser');
        #remove tables from soup
        for table in soup.find_all("table") :
            if table:
                table.decompose()
        #find and remove table of contents
        toc = soup.find(id="toc")
        if toc :
            toc.decompose()
        #soup with content-block
        content = soup.find(id="mw-content-text")
        return content

    # copy file contents,push url to frontier and urls set, write url to a txt file
    def copy_and_push(self,url,depth) :
        # self.copy_docs(url,content)
        self.frontier.put(url)
        self.urls.add(url)
        # print("pushed",new_url)
        self.write_url(url,depth)

# def test_print_urls():
#
#     for link in filter_urls().find_all('a') :
#         url = link.get('href');
#         print(url)



    # find all relevant urls and put in the frontier queue
    def enqueue_frontier(self,url):
        #retrieve filtered page
        content = self.filter_urls()
        self.copy_docs(url,content)

        #retrieve urls in the filtered page
        for link in content.find_all('a') :
            url = link.get('href');
            #if href is None
            if(url == None):
                return

            #add host prefix
            complete_url = "https://en.wikipedia.org" + url
            #if url is wiki's main page or if url is already crawled, ignore and continue
            if( url == "/wiki/Main_Page" or complete_url in self.urls):
                continue
            else:
                #only get urls that match with /wiki/ to avoid crawling
                # external links
                matchWikiArticles = re.match("^/wiki/.*", url)
                #remove administrative links
                adm_regex =  re.match("^/wiki/.*:.*", url)
                #remove disambiguation links
                disambiguation_regex = re.match(".*(disambiguation)",url)
                #if match is found with all filters
                if  matchWikiArticles is not None and adm_regex is None and disambiguation_regex is None:
                    #avoid section links
                    if  '#' not in url :
                        #TODO:Redirected urls removal
                        # new_url = redirected_url(complete_url)
                        self.copy_and_push(complete_url,self.depth)

    def crawl(self,url,depth):
        self.CRAWL_COUNTER+=1;
        print("CRAWLING URL# ",self.CRAWL_COUNTER)
        if not(self.frontier.empty()) and self.depth <= self.MAX_DEPTH and self.CRAWL_COUNTER <= self.MAX_PAGES :
            #open url
            self.open_url(url)
            #push all urls in 'url' to the frontier queue
            self.enqueue_frontier(url)
            print("lentgh of urls",len(self.urls))
            #pop head of queue
            temp = self.frontier.get()
            # if head of queue is at same depth, crawl with same depth
            if(temp != "NEW-LEVEL"):
                self.crawl(temp,self.depth)
            #increment depth and crawl if head of queue is at a new depth
            else:
                #put None at end of queue
                self.frontier.put("NEW-LEVEL")
                self.depth += 1
                new_temp = self.frontier.get()
                self.crawl(new_temp,self.depth)
        print("END OF CRAWL")
        print("lentgh of urls",len(self.urls))
        return

seed_1 = "https://en.wikipedia.org/wiki/Time_zone";
seed_2 = "https://en.wikipedia.org/wiki/Electric_car";
seed_3 = "https://en.wikipedia.org/wiki/Carbon_footprint";

dir_1 = "crawl_1_dir/"
# dir_2 = "crawl_2_dir/"
# dir_3 = "crawl_3_dir/"
crawl_1 = Crawler("crawl_1.txt",seed_1,dir_1)
# crawl_2 = Crawler("crawl_2.txt",seed_2,dir_2)
# crawl_3 = Crawler("crawl_3.txt",seed_3,dir_3)

urls_1 = crawl_1.urls;
urls_1.add(seed_1)
crawl_1.frontier.put("NEW-LEVEL")
crawl_1.crawl(seed_1,2);
os.rmdir(dir_1)
# os.rmdir(dir_2)
# os.rmdir(dir_3)


# urls_2 = crawl_2.urls;
# urls_2.add(seed_2)
# crawl_2.frontier.put("NEW-LEVEL")
# crawl_2.write_url(seed_2)
# crawl_2.crawl(seed_2,1);
#
#
# urls_3 = crawl_3.urls;
# urls_3.add(seed_3)
# crawl_3.frontier.put("NEW-LEVEL")
# crawl_3.write_url(seed_3)
# crawl_3.crawl(seed_3,1);

# open_url(seed)
# print(filter_urls())
# test_print_urls()
