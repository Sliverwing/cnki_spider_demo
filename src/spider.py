from time import time
import requests
from bs4 import BeautifulSoup
import csv

baseUrl = "http://kns.cnki.net/kns/brief/brief.aspx?pagename=ASP.brief_default_result_aspx&dbPrefix=SCDB&dbCatalog=%e4%b8%ad%e5%9b%bd%e5%ad%a6%e6%9c%af%e6%96%87%e7%8c%ae%e7%bd%91%e7%bb%9c%e5%87%ba%e7%89%88%e6%80%bb%e5%ba%93&ConfigFile=SCDBINDEX.xml&research=off&t={0}&keyValue=%E7%BB%8F%E6%96%B9&S=1&curpage={1}&recordsperpage=50"
detailUrl = "http://kns.cnki.net/kns/detail/detail.aspx?dbcode={0}&dbname={1}&filename={2}.nh"
prefix = "http://kns.cnki.net"

s = requests.Session()


def url_generator():
    page_num = 1
    while True:
        yield baseUrl.format(int(time()), page_num)
        page_num += 1

def parse_content(raw_html, ori_url, r):
    soup = BeautifulSoup(raw_html)
    _table = soup.find('table', class_="GridTableContent")
    _trs = _table.find_all("tr")
    _trs.pop(0)
    num = (r - 1) * 50 
    result_set = []

    with open('result.csv', 'a') as csv_file:
        spamwriter = csv.writer(csv_file, delimiter=',')

        for _tr in _trs:
            _td = _tr.find_all('td')
            _title_td = _td[1]
            target_link = _title_td.a['href']
            title = _title_td.text
            author = _td[2].text
            source = _td[3].text
            public_time = _td[4].text
            db = _td[5].text

            _detail_res = s.get(prefix + target_link, headers={"Referer": ori_url}).text
            _summary_soup = BeautifulSoup(_detail_res)
            _summary = _summary_soup.find('span', id='ChDivSummary')
            _keyword_nearby = _summary_soup.find('label', id='catalog_KEYWORD')
            if _keyword_nearby:
                _as = _keyword_nearby.parent.find_all('a')
            else:
                _as = None
            key_words = ""
            if _as:
                for _a in _as:
                    key_words += _a.text.strip()

            if _summary:
                summary = _summary.text
            else:
                summary = None
            num += 1
            result = [item.strip() for item in  [str(num), target_link, title, author, source, public_time, db, key_words, summary]]
            spamwriter.writerow(result)
            print(result)


def get_cookies():
    s.get('http://kns.cnki.net/kns/brief/default_result.aspx')
    s.get('http://kns.cnki.net/kns/request/SearchHandler.ashx?action=&NaviCode=*&ua=1.11&PageName=ASP.brief_default_result_aspx&DbPrefix=SCDB&DbCatalog=%e4%b8%ad%e5%9b%bd%e5%ad%a6%e6%9c%af%e6%96%87%e7%8c%ae%e7%bd%91%e7%bb%9c%e5%87%ba%e7%89%88%e6%80%bb%e5%ba%93&ConfigFile=SCDBINDEX.xml&txt_1_sel=SU%24%25%3D%7C&txt_1_value1=%E7%BB%8F%E6%96%B9&txt_1_special1=%25&his=0&__=Thu%20Apr%2006%202017%2019%3A38%3A02%20GMT%2B0800%20(CST)')

url = url_generator()
get_cookies()

r = 1
while True:
    _url = next(url)
    _result = s.get(_url).text
    parse_content(_result, _url, r)
    r += 1

