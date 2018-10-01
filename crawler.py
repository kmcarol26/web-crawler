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
        self.url = seed;
        self.CRAWL_COUNTER = 0
        self.depth = 1;
        self.MAX_DEPTH = 6;
        self.MAX_PAGES = 999;
        self.seed = seed
        self.html_doc=""
        self.unique_crawled_urls = list()
        # self.unique_crawled_urls.append(str(self.depth))
        os.mkdir(dir)
        self.dir = dir
        self.copy_dir = dir+"/copies/"
        os.mkdir(self.copy_dir)
        self.url_file = open(dir+file,'w+')
        self.frontier = queue.Queue();


    #write url to file
    def write_url(self,url,depth) :
        self.url_file.write("Depth: ")
        self.url_file.write(str(depth))
        self.url_file.write("\n")
        self.url_file.write(url)
        self.url_file.write("\n")


    #method to fetch resource.add()
    def open_url(self,url):
        time.sleep(1)
        # print("Opening URL ",url)
        with urllib.request.urlopen(url) as response:
            # get contents of resource into html_doc
            self.html_doc = response.read()

    # copy html content as raw txt file
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
        # print("pushed",new_url)
        # if url in self.unique_crawled_urls
        # self.write_url(url,depth+1)

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
            if( url == "/wiki/Main_Page" ):
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


    def crawl(self):
        while not(self.frontier.empty()) and self.CRAWL_COUNTER <= self.MAX_PAGES and self.depth-1 <= self.MAX_DEPTH  :

            print(self.url)
            if (str(self.depth) not in self.unique_crawled_urls) :
                self.unique_crawled_urls.append(str(self.depth))
            if (self.url not in self.unique_crawled_urls) :
                print("not in crawled urls")
                self.unique_crawled_urls.append(self.url)
                self.CRAWL_COUNTER+=1;
            self.write_url(self.url,self.depth)
            print("CRAWLING URL# ",self.CRAWL_COUNTER)
            #open url
            self.open_url(self.url)
            #push all urls in 'url' to the frontier queue
            self.enqueue_frontier(self.url)
            #pop head of queue
            temp = self.frontier.get()
            # if head of queue is at same depth, crawl with same depth
            if( temp != str(self.depth) ): #and temp not in self.unique_crawled_urls
                self.url = temp;
                continue
            else:
                    self.depth+=1
                    self.frontier.put(str(self.depth))
                    new_temp = self.frontier.get()
                    self.url = new_temp
                    continue
        return self.unique_crawled_urls


seed_1 = "https://en.wikipedia.org/wiki/Time_zone";
seed_2 = "https://en.wikipedia.org/wiki/Electric_car";
seed_3 = "https://en.wikipedia.org/wiki/Carbon_footprint";

dir_2 = "crawl_2_dir/"
# dir_2 = "crawl_2_dir/"
# dir_3 = "crawl_3_dir/"
crawl_2 = Crawler("crawl_2.txt",seed_2,dir_2)
# crawl_2 = Crawler("crawl_2.txt",seed_2,dir_2)
# crawl_3 = Crawler("crawl_3.txt",seed_3,dir_3)
crawl_2.unique_crawled_urls.append("1")
crawl_2.frontier.put("1")
crawl_2.frontier.put(seed_2)
print(crawl_2.crawl());
print("LENFG",len(crawl_2.unique_crawled_urls))
# os.rmdir(dir_1)
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
