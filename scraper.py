# This is a template for a Python scraper on morph.io (https://morph.io)
# including some code snippets below that you should find helpful

# import scraperwiki
# import lxml.html
#
# # Read in a page
# html = scraperwiki.scrape("http://foo.com")
#
# # Find something on the page using css selectors
# root = lxml.html.fromstring(html)
# root.cssselect("div[align='left']")
#
# # Write out to the sqlite database using scraperwiki library
# scraperwiki.sqlite.save(unique_keys=['name'], data={"name": "susan", "occupation": "software developer"})
#
# # An arbitrary query against the database
# scraperwiki.sql.select("* from data where 'name'='peter'")

# You don't have to do things with the ScraperWiki and lxml libraries.
# You can use whatever libraries you want: https://morph.io/documentation/python
# All that matters is that your final data is written to an SQLite database
# called "data.sqlite" in the current working directory which has at least a table
# called "data".
import requests
from bs4 import BeautifulSoup as bs
import scraperwiki
from datetime import datetime
from multiprocessing.dummy import Pool
from multiprocessing import cpu_count
import grequests

start_urls = ['http://www.tvmao.com/drama/KSExaik=/actors#']
pool = Pool(cpu_count() * 20)

def scrape(response, **kwargs):
        listing_soup = bs(response.text, 'lxml')
        asin_nums = listing_soup.find_all('div', 'zg_itemImmersion')
        for asin_num in asin_nums:
            asin = ''
            try:
                asin = asin_num.find('a')['href'].split('dp/')[-1].strip()
            except:
                pass
            amazon_price = ''
            try:
                amazon_price = asin_num.find('strong', 'price').text.strip()
            except:
                pass
            total_offer_count = ''
            try:
                total_offer_count = asin_num.find('div', 'zg_usedPrice').find('a').text.strip().split(u'\xa0')[0].replace('used & new', '')
            except:
                pass
            lowest_price = ''
            try:
                lowest_price = asin_num.find('div', 'zg_usedPrice').find('span', 'price').text.strip()
            except:
                pass
            today_date = str(datetime.now())
            scraperwiki.sqlite.save(unique_keys=['Date'], data={'ASIN': asin, 'Date': today_date, 'Amazon Price': amazon_price, 'Total Offer Count': total_offer_count, 'Lowest Price': lowest_price})


def multiparse(links):
         l = links.find('a')['href'].encode('utf-8')
         if l:
             return l


def parse(url):
    if url in start_urls:
        async_list = []
        print (url)
        for i in xrange(1, 6):
            rs = (grequests.get(url+'?&pg={}'.format(i), hooks = {'response' : scrape}))
            async_list.append(rs)
        grequests.map(async_list)
    page = requests.get(url)
    soup = bs(page.text, 'lxml')
    try:
        active_sel = soup.find('span', 'zg_selected').find_next()
        if active_sel.name == 'ul':
            links_lists= active_sel.find_all('li')
            asins = pool.map(multiparse, links_lists)
            for asin in asins:
                async_list = []
                print (asin)
                for i in xrange(1, 6):
                    rs = (grequests.get(asin+'?&pg={}'.format(i), hooks = {'response' : scrape}))
                    async_list.append(rs)
                parse(asin)
                grequests.map(async_list)


    except:
        parse(url)


if __name__ == '__main__':

   for start_url in start_urls:
       parse( start_url)



url = 'http://www.tvmao.com/drama/KSExaik=/actors#'
headers = {
        'Accept-Charset': 'UTF-8,*;q=0.5',
        'Accept-Encoding': 'gzip,deflate,sdch',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
        'Accept': '*/*',

    }

def make_dict(table):
    result = []
    allrows = table.findAll('tr')
    keys = allrows[0].findAll('td',text=True)
    
    for row in allrows[1:]:
        item = {}
        allcols = row.findAll('td')
        for k in range(len(keys)):
            col = allcols[k]
            if col.find('a'):
                a = col.find('a')
                v = {}
                v['@type'] = "uri"
                v['href'] = a['href']
                v['name'] = a.text
                item[keys[k]] = v
            else:
                item[keys[k]] = col.text
        result.append(item)
    return result
    
r = requests.get(url,headers=headers)
soup = BeautifulSoup.BeautifulSoup(r.content)
table = soup.findAll('table',{'class':'tbcrew'})[0]
juese = make_dict(table)
