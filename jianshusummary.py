import httplib
from bs4 import BeautifulSoup
import json

urlTemplate = '/u/e6367cf15710?order_by=shared_at&page={0}'
cookie = 'remember_user_token=W1syOTQ5NzUwXSwiJDJhJDEwJDdoOVlBRkhwSk9nMXdLanliSUNNSWUiLCIxNDk5MTQ3MTU5Ljg1ODcwNDMiXQ%3D%3D--7c5dc200db966f1d819e4c5e2650d8cc5f49a05e; _ga=GA1.2.669366992.1497926671; _gid=GA1.2.34677441.1499066591; _gat=1; Hm_lvt_0c0e9d9b1e7d617b3e6842e85b9fb068=1498703353,1499066591,1499135531,1499135540; Hm_lpvt_0c0e9d9b1e7d617b3e6842e85b9fb068=1499311733; _session_id=RTROUDJibXlnU0xyTnZQNEp0OUFBbXFYdUN6N3A1NitTUGR0N2t4dmNtMXFWcU9nanh1aVFtRTZ2RGV0b3ZmeG8yamkzd1ArNVdySG9zVXhFb2pJUXBabWc1K09xblU1NjdEelpCSFJuVHkxZ3ErK21PUi9lSXcwaUNTUDNRVVU5WXdESkJaODVZd0ZLMWNMMTVDbkxFLzhxaTdCVUk0UGZ4MUhFMDBjSHhjM3FHWWcxWUNycnk2RUt2OGJsY2doMjNPYWdUMlVQb3luMGhvemN0aEpxTnVqYlpCM1FmWk1vU2s4d3pkdnA3L2FsQzBuRmp1N2Z3bmFnYUV5SVF5cTJPYlEvSlRsUmdVSFNkQkRWdjkxRHdyQUZQbTh0SGpCemRWSkNIWVZwRGt3WERiRWZsK0FsS3FxREtTbTBjT0c1TWtGTUdKSHREZ3E0ZFgvcTlqNkcyN1V1Wk5MQ1NDeDRuOVlhQ0FmVmVWT3BGbFQ5TGtRQkNSc1FYc3ZsRkZORWwvRHIxditpMDJlN3ZxMDh3N3ZkT3UzR1AwbTJXcVZ6WEd6SHB0ZGtEbz0tLVNheUczZzU5WWFZQkQvT2cyazRLWmc9PQ%3D%3D--1b3fbe3886b77020dae65067dbca59215f5f3939; remember_user_token=W1syOTQ5NzUwXSwiJDJhJDEwJDdoOVlBRkhwSk9nMXdLanliSUNNSWUiLCIxNDk5MTQ3MTU5Ljg1ODcwNDMiXQ%3D%3D--7c5dc200db966f1d819e4c5e2650d8cc5f49a05e; _session_id=Tk81cXRsUXA1TExXcW1uazZZNzVsT1h5ZkN6WVAzbHJiTkdRbkh5dmpUWHMxZllqaTgxd3pIcHA2QkVJMG9IYkZhcG1HSUxidlgvOXV3MVJQNGtJeml1TVg4dkZvZWJNZnV5ZjYwUDE0OE5XeTFnM2FHNW54Qm9GOVM1cnd6bW81bUJ6TXo5R3lQdGwzT29iUUZRUFhQUGd1OXRQVEh1L2hNNDl0dDlhOVU1QURuNG5HZkhPNFFKNVdsU0Nqam94STZReXdGdGgxNlVNcWt5TTE1OEV4ejdsWlF3UUNxTHM2NkxUZ1ZwbTFYSUF2Q1RwTmgxNzFOOTdmbkdrZVJzSHp2V3NWb0VPWTIrbVhiTGNWNEY2ZzY2eVd1QzRSMzBMWVd2dTdocHJMaWpqM2dnZWE3dHVrdjYzeVNIYzc5bjNsODVZTTdRcER2Y05kaHh2Ryt1U1pKeE5pZUFnYnc0OHNhVnExekpaL3pvRzNMaExzNVRQSzc3aHVQT21IVGQ2N1pSQ2lqN3BJZVhRbWhuekdJa0p4ckdqOGRGNVJ5RGFWM3djVHZ5RzMyWT0tLWQ3MkVjRC9yQTNucTI4dHFQdkg0cXc9PQ%3D%3D--fd2d4e8f24bdb9cd731b223d143e9e484eb02b87; _ga=GA1.2.669366992.1497926671; _gid=GA1.2.34677441.1499066591; Hm_lvt_0c0e9d9b1e7d617b3e6842e85b9fb068=1498703353,1499066591,1499135531,1499135540; Hm_lpvt_0c0e9d9b1e7d617b3e6842e85b9fb068=1499319512 If-None-Match: W/"30c2e128a60740cd508d2e3fd1252865"'



def requestUrl(url, headers):
    conn = httplib.HTTPConnection('www.jianshu.com')
    conn.request("GET", url, headers=headers)
    response = conn.getresponse()
    responseData = response.read()
    return responseData

def requestAll():
    index = 0
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

articles = requestAll()
jsonStr = json.dumps(articles)

with open('./public/summary.json', 'w') as file:
    file.write(jsonStr)

