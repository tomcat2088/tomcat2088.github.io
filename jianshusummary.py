import httplib
from bs4 import BeautifulSoup
import json
import datetime

urlTemplate = '/u/e6367cf15710?order_by=shared_at&page={0}'
cookie = ''



def requestUrl(url, headers):
    conn = httplib.HTTPConnection('www.jianshu.com')
    conn.request("GET", url, headers=headers)
    response = conn.getresponse()
    responseData = response.read()
    return responseData

def requestAll():
    index = 1
    articles = []
    requestNeedStop = False
    while requestNeedStop == False:
        url = str.format(urlTemplate, index)
        html = requestUrl(url, { 'Cookie': cookie, 'X-INFINITESCROLL': 'true', 'Referer':'http://www.jianshu.com/u/e6367cf15710', 'X-CSRF-Token': 'kATLbzovGXIinqi5giGhu+YO4C8+OoXyBgFWCRB/DpadhFpGQJAOMErdpMiT5yTC7yIJuqqZrN+6wszD7WiRTQ==' })
        if html.strip() == "":
            requestNeedStop = True
            print(str.format('Process Complete.'))    
        print(str.format('Process Page {0} ', index))
        soup = BeautifulSoup(html, 'html.parser')
        for item in soup.find_all('li'):
            article = {}
            article['title'] = item.find_all('a', 'title')[0].string
            article['readCount'] = int(item.find_all('i', 'iconfont ic-list-read')[0].next_sibling)
            article['commentCount'] = int(item.find_all('i', 'iconfont ic-list-comments')[0].next_sibling)
            article['loveCount'] = int(item.find_all('i', 'iconfont ic-list-like')[0].next_sibling)
            articles.append(article)

        index += 1
    return articles

def processJianshuSummary():
    articles = requestAll()
    if len(articles) == 0:
        return False
    jsonStr = json.dumps(articles)

    filename = str.format('./public/jianshu-summary/{0}.json', datetime.datetime.today().strftime('%Y-%m-%d'))
    with open(filename, 'w') as file:
        file.write(jsonStr)
    return True

