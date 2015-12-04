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
import BeautifulSoup

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
