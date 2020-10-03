import time
from bs4 import BeautifulSoup
import requests
from datetime import timedelta, date
import random
from headers import Headers
from langdetect import detect
import boto3
from botocore.exceptions import ClientError


def send_email(message):
    # Both the ids must be verified via aws sns
    SENDER = "vipul@newzera.com"
    RECIPIENT = "vipul@newzera.com"

    #CONFIGURATION_SET = "ConfigSet"
    AWS_REGION = "ap-south-1"

    SUBJECT = "Errornous Url's found while crawling"

    BODY_TEXT = (message)

    BODY_HTML = """<html>
    <head></head>
    <body>
    <h1></h1>
    <p>""" + message+"""</p>
    </body>
    </html>
                """

    CHARSET = "UTF-8"

    client = boto3.client('ses', region_name=AWS_REGION)

    try:
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    RECIPIENT,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': BODY_HTML,
                    },
                    'Text': {
                        'Charset': CHARSET,
                        'Data': BODY_TEXT,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
            Source=SENDER,
            # ConfigurationSetName=CONFIGURATION_SET,
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])


class CommonClass():

    @staticmethod
    def get_page(url):
        retries = 1
        for i in range(10):
            print("Try : ", i, url)
            try:
                userAgentDict = Headers.get_user_agent()
                proxyDict = Headers.get_proxy()
                print(url)

                response = requests.get(
                    url, proxies=proxyDict, headers=userAgentDict, timeout=10)

                status = response.status_code
                print(status)
                if status == 200:
                    return response.text
                print("Got the response code:", status)
            except Exception as e:
                if(i == 9):
                    send_email("Exception  occurred for this url while getting the html for archive :" +
                               url + "the error: " + e)
                print("Exception  occurred for this url while getting the html for archive :",
                      url, "the error: ", e)
                wait = retries*2
                time.sleep(wait)
                retries += 1
        return ""


class TheHinduCrawler():
    def __init__(self, interval):
        self.interval = interval

    def makeURL(self):
        url = []
        dateList = []
        dateList = self.date_dt()
        count_dt = 0
        while count_dt < len(dateList):
            url.append('https://www.thehindu.com/archive/web/' +
                       dateList[count_dt])
            count_dt += 1
        # print(*url, sep="\n")
        return url

    def date_dt(self):
        print("Entered the dt of The Hindu")
        startYear = self.interval.get("startYear")
        startMonth = self.interval.get("startMonth")
        startDay = self.interval.get("startDay")
        endYear = self.interval.get("endYear")
        endMonth = self.interval.get("endMonth")
        endDay = self.interval.get("endDay")
        # print(startYear)
        dateList = []

        def daterange(date1, date2):
            for n in range(int((date2 - date1).days)+1):
                yield date1 + timedelta(n)
        start_dt = date(startYear, startMonth, startDay)
        end_dt = date(endYear, endMonth, endDay)
        for dt in daterange(start_dt, end_dt):
            dateList.append(dt.strftime("%Y/%m/%d/"))
        # print(dateList, "datelist")
        return dateList

    def get_links(self, url):
        links = []
        for i in range(10):
            page = CommonClass.get_page(url)
            try:
                print("Try: ", i)
                soup = BeautifulSoup(page)
            # decompose an element from the soup that we dont have to print from the unwanted href tags
                soup.find('div', id='subnav-tpbar-latest').decompose()
                section = soup.find('div', class_='tpaper-container')
                for a in section.findAll('a'):
                    href = a.get('href')
                    if not "crossword.thehindu.com" in str(href):
                        links.append(href)
                break
            except Exception as e:
                send_email("Exception occurred while fetching the links in The Hindu" +
                           e + "url is " + url)
                print("Exception occurred while fetching the links in The Hindu",
                      e, "url is ", url)
        return links

    def parse(self):
        url_count = 0
        url = self.makeURL()
        links = []
        # retries = 1
        # print("entered parse")
        while (url_count < len(url)):
            hrefs = self.get_links(url[url_count])
            links.extend(hrefs)
            url_count += 1
        # filter and remove the none from the list. =>  list(filter(None, links))
        # filter the list that end with ".ece" . This the final required list of article links
        return list(filter(lambda x: x.endswith(".ece"), list(filter(None, links))))


class EconomicTimesCrawler():
    def __init__(self, interval):
        self.interval = interval

    def makeURL(self):

        url = []
        dateList = []
        # start date should be from and above 1st jan 2001 (TOI data is available from 2001)
        dateList = self.date_dt()
        count_dt = 0
        while count_dt < len(dateList):
            url.append('https://economictimes.indiatimes.com/' +
                       dateList[count_dt])
            count_dt += 1
        return url

    def date_dt(self):
        print("Entered the dt of economic times")
        startYear = self.interval.get("startYear")
        startMonth = self.interval.get("startMonth")
        startDay = self.interval.get("startDay")
        endYear = self.interval.get("endYear")
        endMonth = self.interval.get("endMonth")
        endDay = self.interval.get("endDay")
        # print(startYear)
        dateList = []

        def daterange(date1, date2):
            for n in range(int((date2 - date1).days)+1):
                yield date1 + timedelta(n)
        start_dt = date(startYear, startMonth, startDay)
        end_dt = date(endYear, endMonth, endDay)
        if start_dt > end_dt:
            print("Exception: end date should be greater than or equal to start date")
            return []
        if start_dt < date(2001, 1, 1):
            print(
                "Exception: Start date for economic times should be after 1st january 2001")
            return []
        d0 = date(2001, 1, 1)
        delta = start_dt - d0
        # 36892 is a serial date(excel) of 1st jan 2001.
        start_time = 36892 + delta.days
        for dt in daterange(start_dt, end_dt):
            dateList.append(dt.strftime(
                "%Y/%m/%d/" + 'archivelist/year-%Y,month-%m,starttime-'+str(start_time) + '.cms'))
            start_time += 1
        return dateList

    def get_links(self, url):
        links = []
        for i in range(10):
            page = CommonClass.get_page(url)
            try:
                print("Try: ", i)
                soup = BeautifulSoup(page)
                section = soup.find('table', cellpadding="0",
                                    cellspacing="0", border="0", width="100%")
                for a in section.findAll('a'):
                    href = a.get('href')
                    links.append(
                        'https://economictimes.indiatimes.com/' + href)
                break
            except Exception as e:
                send_email("Exception occurred while fetching the links in Economic Times" +
                           e + "url is " + url)
                print("Exception occurred while fetching the links in Economic Times",
                      e, "url is ", url)
        return links

    def parse(self):
        url_count = 0
        links = []
        url = self.makeURL()
        while (url_count < len(url)):
            hrefs = self.get_links(url[url_count])
            links.extend(hrefs)
            url_count += 1
        # filter the links that ends with .cms
        return list(dict.fromkeys(filter(lambda x: x.endswith(".cms"), (links))))


class TimesOfIndiaCrawler():

    def __init__(self, interval):
        self.interval = interval

    def makeURL(self):
        archive_string = 'https://timesofindia.indiatimes.com/'

        url = []
        dateList = []
        # start date should be from and above 1st jan 2001 (TOI data is available from 2001)
        dateList = self.date_dt()
        count_dt = 0
        while count_dt < len(dateList):
            url.append(archive_string + dateList[count_dt])
            count_dt += 1
        return url

    def date_dt(self):
        date_format = "%Y/%m/%d/"
        print("Entered the dt of Times of India")
        startYear = self.interval.get("startYear")
        startMonth = self.interval.get("startMonth")
        startDay = self.interval.get("startDay")
        endYear = self.interval.get("endYear")
        endMonth = self.interval.get("endMonth")
        endDay = self.interval.get("endDay")
        dateList = []

        def daterange(date1, date2):
            for n in range(int((date2 - date1).days)+1):
                yield date1 + timedelta(n)
        start_date = date(startYear, startMonth, startDay)
        end_date = date(endYear, endMonth, endDay)
        if start_date > end_date:
            print(
                "Exception: end date should be greater than or equal to start date")
            return []
        elif start_date < date(2001, 1, 1):
            print(
                "Exception: Start date for Times of India should be after 1st january 2001")
            return []
        delta = start_date - date(2001, 1, 1)
        # 36892 is a serial date of 1st jan 2001.
        start_time = 36892 + delta.days
        for date_ in daterange(start_date, end_date):
            dateList.append(date_.strftime(
                date_format + 'archivelist/year-%Y,month-%m,starttime-'+str(start_time) + '.cms'))
            start_time += 1
        return dateList

    def get_links(self, url):
        links = []
        for i in range(10):
            page = CommonClass.get_page(url)
            try:
                print("Try: ", i)
                soup = BeautifulSoup(page)
                section = soup.find(
                    'div', style="font-family:arial ;font-size:12;font-weight:bold; color: #006699")
                for a in section.findAll('a'):
                    href = a.get('href')
                    links.append('https://timesofindia.indiatimes.com/' + href)
                break
            except Exception as e:
                send_email("Exception occurred while fetching the links in Time of India" +
                           e + "url is " + url)
                print("Exception occurred while fetching the links in Times of India",
                      e, "url is ", url)
        return links

    def parse(self):
        url_count = 0
        links = []
        url = self.makeURL()
        # retries = 1
        while (url_count < len(url)):
            hrefs = self.get_links(url[url_count])
            links.extend(hrefs)
            url_count += 1
        return list(dict.fromkeys(
            list(filter(lambda x: x.endswith(".cms"), (links)))
        ))  # filter the links that ends with .cms


class IndianExpressCrawler():

    def __init__(self, interval):
        self.interval = interval

    def makeURL(self):
        url = []
        dateList = []
        dateList = self.date_dt()
        count_dt = 0
        while count_dt < len(dateList):
            url.append(
                'http://archive.indianexpress.com/archive/news/' + dateList[count_dt])
            count_dt += 1
        return url

    def date_dt(self):
        dateList = []
        print("Entered the dt of Indian Express")
        startYear = self.interval.get("startYear")
        startMonth = self.interval.get("startMonth")
        startDay = self.interval.get("startDay")
        endYear = self.interval.get("endYear")
        endMonth = self.interval.get("endMonth")
        endDay = self.interval.get("endDay")

        def daterange(date1, date2):
            for n in range(int((date2 - date1).days)+1):
                yield date1 + timedelta(n)
        start_dt = date(startYear, startMonth, startDay)
        end_dt = date(endYear, endMonth, endDay)
        for dt in daterange(start_dt, end_dt):
            # if you add a hash '#' between the % and the letter, you can remove the leading zero.
            dateList.append(dt.strftime("%-d/%-m/%Y/"))
        # print(dateList)
        return dateList

    def get_links(self, url):
        links = []
        for i in range(10):
            page = CommonClass.get_page(url)
            try:
                print("Try: ", i)
                soup = BeautifulSoup(page)
                section = soup.find('div', id='box_left')
                for a in section.findAll('a'):
                    href = a.get('href')
                    links.append(href)
                break
            except Exception as e:
                send_email("Exception occurred while fetching the links in Indian express" +
                           e + "url is " + url)
                print("Exception occurred while fetching the links in Indian Express",
                      e, "url is ", url)
        return links

    def parse(self):
        url_count = 0
        url = self.makeURL()
        links = []
        while (url_count < len(url)):
            hrefs = self.get_links(url[url_count])
            links.extend(hrefs)
            url_count += 1
        # filter and remove the none from the list. =>  list(filter(None, links))
        # filter the list that end with ".ece" . This the final required list of article links
        return list(dict.fromkeys(list(filter(None, links))))


class NDTVCrawler():

    def __init__(self, interval):
        self.interval = interval

    def makeURL(self):
        url = []
        dateList = []
        dateList = self.date_dt()
        count_dt = 0
        while count_dt < len(dateList):
            url.append('http://archives.ndtv.com/articles/' +
                       dateList[count_dt])
            count_dt += 1
        return url

    def date_dt(self):
        dateList = []
        print("Entered the dt of NDTV")
        startYear = self.interval.get("startYear")
        startMonth = self.interval.get("startMonth")
        startDay = self.interval.get("startDay")
        endYear = self.interval.get("endYear")
        endMonth = self.interval.get("endMonth")
        endDay = self.interval.get("endDay")

        def daterange(date1, date2):
            for n in range(int((date2 - date1).days)+1):
                yield date1 + timedelta(n)
        start_dt = date(startYear, startMonth, startDay)
        end_dt = date(endYear, endMonth, endDay)
        for dt in daterange(start_dt, end_dt):
            dateList.append(dt.strftime("%Y-%m%d" + ".html"))
        return dateList

    def get_links(self, url):
        links = []
        day_temp = url[-7:-5]
        url_temp = url.rstrip('.html')[:-2] + '.html'
        day_temp = int(day_temp.lstrip('0'))
        for i in range(10):
            page = CommonClass.get_page(url_temp)
            # print(url_temp)
            try:
                print("Try: ", i)
                soup = BeautifulSoup(page)
                # print("Reached here 0")
                days = soup.find('div', {'id': 'main-content'}
                                 ).find_all('ul')[day_temp-1]
                # print(days)
                # print("Reached here 1")
                # print (soup)
                for li in days.findAll('li'):
                    txt = li.a.get_text()
                    href = li.a.get('href')
                    if ('en' == detect(txt) and 'ndtv.com' in str(href)):
                        links.append(href)
                        # print(href)
                # print("Reached here 2")
                break
            except Exception as e:
                send_email("Exception occurred while fetching the links in NDTV" +
                           e + "url is " + url)
                print("Exception occurred while fetching the links in NDTV",
                      e, "url is ", url_temp)
        return links

    def parse(self):
        url = self.makeURL()
        url_count = 0
        links = []
        while url_count < len(url):
            hrefs = self.get_links(url[url_count])
            links.extend(hrefs)
            url_count += 1
        return(links)


class DailyMailCrawler():

    def __init__(self, interval):
        self.interval = interval

    def makeURL(self):
        url = []
        dateList = []
        dateList = self.date_dt()
        count_dt = 0
        while count_dt < len(dateList):
            url.append('https://www.dailymail.co.uk/home/sitemaparchive/day_' +
                       dateList[count_dt] + '.html')
            count_dt += 1
        return url

    def date_dt(self):
        dateList = []
        startYear = self.interval.get("startYear")
        startMonth = self.interval.get("startMonth")
        startDay = self.interval.get("startDay")
        endYear = self.interval.get("endYear")
        endMonth = self.interval.get("endMonth")
        endDay = self.interval.get("endDay")

        def daterange(date1, date2):
            for n in range(int((date2 - date1).days)+1):
                yield date1 + timedelta(n)
        start_dt = date(startYear, startMonth, startDay)
        end_dt = date(endYear, endMonth, endDay)
        for dt in daterange(start_dt, end_dt):
            dateList.append(dt.strftime("%Y%m%d"))
        return dateList

    def get_links(self, url):
        links = []
        for i in range(10):
            page = CommonClass.get_page(url)
            try:
                soup = BeautifulSoup(page)
                section = soup.find(
                    'ul', class_="archive-articles debate link-box")
                for a in section.findAll('a'):
                    href = a.get('href')
                    links.append('https://www.dailymail.co.uk' + href)
                break
            except Exception as e:
                send_email("Exception occurred while fetching the links in Daily Mail" +
                           e + "url is " + url)
                print("Exception occurred while fetching the links in DailyMail",
                      e, "url is ", url)
        return links

    def parse(self):
        url_count = 0
        url = self.makeURL()
        request_number = 0
        links = []
        while (url_count < len(url)):
            if request_number > 50:
                request_number = 0
                # sleep for random seconds between 1sec to 3sec
                time.sleep(random.randint(0, 3))
                pass
            hrefs = self.get_links(url[url_count])
            links.extend(hrefs)
            url_count += 1
            request_number += 1
        # return filter (lambda x:x.endswith(".html"),list(links))  # filter the links that ends with .cms
        return list(dict.fromkeys(links))


class IndiaTodayCrawler():
    def __init__(self, interval):
        self.interval = interval

    def makeURL(self):
        url = []
        dateList = []
        dateList = self.date_dt()
        count_dt = 0
        while count_dt < len(dateList):
            a = dateList[count_dt]
            url.append('https://www.indiatoday.in/archives/story/'+str(a.day)+'-'+str(a.month)+'-'+str(a.year) +
                       '?bundle_name=Story&hash=itbxf0&ds_changed='+str(a.year)+'-'+str(a.month)+'-'+str(a.day)+'&page=')
            count_dt += 1
        return url

    def date_dt(self):
        dateList = []
        startYear = self.interval.get("startYear")
        startMonth = self.interval.get("startMonth")
        startDay = self.interval.get("startDay")
        endYear = self.interval.get("endYear")
        endMonth = self.interval.get("endMonth")
        endDay = self.interval.get("endDay")

        def daterange(date1, date2):
            for n in range(int((date2 - date1).days)+1):
                yield date1 + timedelta(n)
        start_dt = date(startYear, startMonth, startDay)
        end_dt = date(endYear, endMonth, endDay)
        for dt in daterange(start_dt, end_dt):
            dateList.append(dt)
        return dateList

    def get_links(self, url):
        links = []
        for i in range(10):
            for pageno in range(1000):
                length = len(links)
                page = CommonClass.get_page(url + str(pageno))
                try:
                    print("Try: ", i)
                    soup = BeautifulSoup(page)
                    mydivs = soup.findAll(
                        "div", {"class": "views-field views-field-nothing-1"})
                    for division in mydivs:
                        href = division.find('a')
                        links.append(
                            'https://www.indiatoday.in/' + href.get('href'))
                    if(len(links) == length):
                        return links
                except Exception as e:
                    send_email("Exception occurred while fetching the links in India Today" +
                               e + "url is " + url)
                    print("Exception occurred while fetching the links in India Today",
                          e, "url is ", url)
        return links

    def parse(self):
        url_count = 0
        links = []
        url = self.makeURL()
        while (url_count < len(url)):
            hrefs = self.get_links(url[url_count])
            links.extend(hrefs)
            url_count += 1
        # filter the links that ends with .cms
        return links


class OneIndiaCrawler():

    def __init__(self, interval):
        self.interval = interval

    def makeURL(self):
        url = []
        dateList = []
        dateList = self.date_dt()
        count_dt = 0
        while count_dt < len(dateList):
            url.append('https://www.oneindia.com/' + dateList[count_dt])
            count_dt += 1
        return url

    def date_dt(self):
        dateList = []
        startYear = self.interval.get("startYear")
        startMonth = self.interval.get("startMonth")
        startDay = self.interval.get("startDay")
        endYear = self.interval.get("endYear")
        endMonth = self.interval.get("endMonth")
        endDay = self.interval.get("endDay")

        def daterange(date1, date2):
            for n in range(int((date2 - date1).days)+1):
                yield date1 + timedelta(n)
        start_dt = date(startYear, startMonth, startDay)
        end_dt = date(endYear, endMonth, endDay)
        for dt in daterange(start_dt, end_dt):
            dateList.append(dt.strftime("%Y/%m/%d/"))
        return dateList

    def get_links(self, url):
        links = []
        for i in range(10):
            page = CommonClass.get_page(url)
            try:
                print("one")
                soup = BeautifulSoup(page)
                sections = soup.find(
                    'div', {'class': 'content clearfix'}).find_all('ul')
                for section in sections:
                    for li in section.findAll('li'):
                        href = li.a.get('href')
                        links.append('https://www.oneindia.com/' + href)
                break
            except Exception as e:
                send_email("Exception occurred while fetching the links in OneIndia" +
                           e + "url is " + url)
                print("Exception occurred while fetching the links in OneIndia",
                      e, "url is ", url)
        return links

    def parse(self):
        url_count = 0
        links = []
        url = self.makeURL()
        while (url_count < len(url)):
            hrefs = self.get_links(url[url_count])
            links.extend(hrefs)
            url_count += 1
        # filter the links that ends with .cms
        return list(dict.fromkeys(links))


class DailyExpressCrawler():

    def __init__(self, interval):
        self.interval = interval

    def makeURL(self):
        url = []
        dateList = []
        dateList = self.date_dt()
        count_dt = 0
        while count_dt < len(dateList):
            url.append('https://www.express.co.uk/sitearchive/' +
                       dateList[count_dt])
            count_dt += 1
        return url

    def date_dt(self):
        dateList = []
        startYear = self.interval.get("startYear")
        startMonth = self.interval.get("startMonth")
        startDay = self.interval.get("startDay")
        endYear = self.interval.get("endYear")
        endMonth = self.interval.get("endMonth")
        endDay = self.interval.get("endDay")

        def daterange(date1, date2):
            for n in range(int((date2 - date1).days)+1):
                yield date1 + timedelta(n)
        start_dt = date(startYear, startMonth, startDay)
        end_dt = date(endYear, endMonth, endDay)
        for dt in daterange(start_dt, end_dt):
            dateList.append(dt.strftime("%Y/%m/%d/"))
        return dateList

    def get_links(self, url):
        links = []
        for i in range(10):
            page = CommonClass.get_page(url)
            try:
                soup = BeautifulSoup(page)
                mydivs = soup.findAll("ul", {"class": "section-list"})
                for page1 in mydivs:
                    href = page1.findAll('a')
                    for link in href:
                        links.append('https://www.express.co.uk/' +
                                     link.get('href'))
                break
            except Exception as e:
                send_email("Exception occurred while fetching the links in Daily Express" +
                           e + "url is " + url)
                print("Exception occurred while fetching the links in Daily Express",
                      e, "url is ", url)
        return links

    def parse(self):
        url_count = 0
        links = []
        url = self.makeURL()
        while (url_count < len(url)):
            hrefs = self.get_links(url[url_count])
            links.extend(hrefs)
            url_count += 1
        # filter the links that ends with .cms
        return list(dict.fromkeys(links))


class BusinessLineCrawler():

    def __init__(self, interval):
        self.interval = interval

    def makeURL(self):
        url = []
        dateList = []
        dateList = self.date_dt()
        count_dt = 0
        while count_dt < len(dateList):
            url.append('https://www.thehindubusinessline.com/archive/web/' +
                       dateList[count_dt])
            count_dt += 1
        return url

    def date_dt(self):
        dateList = []
        startYear = self.interval.get("startYear")
        startMonth = self.interval.get("startMonth")
        startDay = self.interval.get("startDay")
        endYear = self.interval.get("endYear")
        endMonth = self.interval.get("endMonth")
        endDay = self.interval.get("endDay")

        def daterange(date1, date2):
            for n in range(int((date2 - date1).days)+1):
                yield date1 + timedelta(n)
        start_dt = date(startYear, startMonth, startDay)
        end_dt = date(endYear, endMonth, endDay)
        for dt in daterange(start_dt, end_dt):
            dateList.append(dt.strftime("%Y/%m/%d/"))
        return dateList

    def get_links(self, url):
        links = []
        for i in range(10):
            page = CommonClass.get_page(url)
            try:
                soup = BeautifulSoup(page)
                mydivs = soup.findAll("ul", {"class": "archive-list"})
                for page1 in mydivs:
                    href = page1.findAll('a')
                    for link in href:
                        links.append(link.get('href'))
                break
            except Exception as e:
                send_email("Exception occurred while fetching the links in Business Line" +
                           e + "url is " + url)
                print("Exception occurred while fetching the links in Business Line",
                      e, "url is ", url)
        return links

    def parse(self):
        url_count = 0
        links = []
        url = self.makeURL()
        while (url_count < len(url)):
            hrefs = self.get_links(url[url_count])
            links.extend(hrefs)
            url_count += 1
        # filter the links that ends with .cms
        return list(dict.fromkeys(links))


class EuroNewsCrawler():

    def __init__(self, interval):
        self.interval = interval

    def makeURL(self):
        url = []
        dateList = []
        dateList = self.date_dt()
        count_dt = 0
        while count_dt < len(dateList):
            url.append('https://www.euronews.com/' +
                       dateList[count_dt])
            count_dt += 1
        return url

    def date_dt(self):
        dateList = []
        startYear = self.interval.get("startYear")
        startMonth = self.interval.get("startMonth")
        startDay = self.interval.get("startDay")
        endYear = self.interval.get("endYear")
        endMonth = self.interval.get("endMonth")
        endDay = self.interval.get("endDay")

        def daterange(date1, date2):
            for n in range(int((date2 - date1).days)+1):
                yield date1 + timedelta(n)
        start_dt = date(startYear, startMonth, startDay)
        end_dt = date(endYear, endMonth, endDay)
        for dt in daterange(start_dt, end_dt):
            dateList.append(dt.strftime("%Y/%m/%d/"))
        return dateList

    def get_links(self, url):
        links = []
        for i in range(10):
            page = CommonClass.get_page(url)
            try:
                soup = BeautifulSoup(page)
                mydivs = soup.findAll("div", {"class": "m-object__body"})
                for page1 in mydivs:
                    href = page1.findAll(
                        "a", {"class": "m-object__title__link"})
                    for link in href:
                        links.append(
                            'https://www.euronews.com/' + link.get('href'))
                break
            except Exception as e:
                send_email("Exception occurred while fetching the links in Euro News" +
                           e + "url is " + url)
                print("Exception occurred while fetching the links in Euro News",
                      e, "url is ", url)
        return links

    def parse(self):
        url_count = 0
        links = []
        url = self.makeURL()
        while (url_count < len(url)):
            hrefs = self.get_links(url[url_count])
            links.extend(hrefs)
            url_count += 1
        # filter the links that ends with .cms
        return list(dict.fromkeys(links))


class EBMNewsCrawler():
    def __init__(self, interval):
        self.interval = interval

    def makeURL(self):
        url = []
        dateList = []
        dateList = self.date_dt()
        count_dt = 0
        # ONLY EXTRACT OF THE YEAR OF STARTING DATE and year > 2005
        print("Starting")
        url.append('https://www.ebmnews.com/' + str(dateList[0].year))

        return url

    def date_dt(self):
        dateList = []
        startYear = self.interval.get("startYear")
        startMonth = self.interval.get("startMonth")
        startDay = self.interval.get("startDay")
        endYear = self.interval.get("endYear")
        endMonth = self.interval.get("endMonth")
        endDay = self.interval.get("endDay")

        def daterange(date1, date2):
            for n in range(int((date2 - date1).days)+1):
                yield date1 + timedelta(n)
        start_dt = date(startYear, startMonth, startDay)
        end_dt = date(endYear, endMonth, endDay)
        for dt in daterange(start_dt, end_dt):
            dateList.append(dt)
        return dateList

    def get_links(self, url):
        links = []
        for i in range(10):
            for pageno in range(1000):
                length = len(links)
                page = CommonClass.get_page(url + '/page/' + str(pageno + 1))
                try:
                    print("Try: ", i)
                    soup = BeautifulSoup(page)
                    mydivs = soup.findAll(
                        "div", {"class": "item-inner clearfix"})
                    for division in mydivs:
                        href = division.find('a')
                        links.append(href.get('href'))
                    if(len(links) == length):
                        return links
                except Exception as e:
                    send_email("Exception occurred while fetching the links in EBM News" +
                               e + "url is " + url)
                    print("Exception occurred while fetching the links in EBM NEWS",
                          e, "url is ", url)
        return links

    def parse(self):
        print("started")
        url_count = 0
        links = []
        url = self.makeURL()
        while (url_count < len(url)):
            hrefs = self.get_links(url[url_count])
            links.extend(hrefs)
            url_count += 1
        # filter the links that ends with .cms
        return links


class ABCNewsCrawler():
    def __init__(self, interval):
        self.interval = interval

    def makeURL(self):
        url = []
        dateList = []
        dateList = self.date_dt()
        count_dt = 0
        while count_dt < len(dateList):
            a = dateList[count_dt]
            url.append('https://www.abc.net.au/news/archive/?date=' + a)
            count_dt += 1
        return url

    def date_dt(self):
        dateList = []
        startYear = self.interval.get("startYear")
        startMonth = self.interval.get("startMonth")
        startDay = self.interval.get("startDay")
        endYear = self.interval.get("endYear")
        endMonth = self.interval.get("endMonth")
        endDay = self.interval.get("endDay")

        def daterange(date1, date2):
            for n in range(int((date2 - date1).days)+1):
                yield date1 + timedelta(n)
        start_dt = date(startYear, startMonth, startDay)
        end_dt = date(endYear, endMonth, endDay)
        for dt in daterange(start_dt, end_dt):
            dateList.append(dt.strftime("%Y-%m-%d"))
        return dateList

    def get_links(self, url):
        links = []
        for i in range(10):
            for pageno in range(1000):
                length = len(links)
                page = CommonClass.get_page(url + '&page=' + str(pageno))
                try:
                    print("Try: ", i)
                    soup = BeautifulSoup(page)
                    mydivs = soup.findAll(
                        "div", {"class": "description col-xs-12 col-sm-8description col-xs-12"})
                    for division in mydivs:
                        href = division.find('a')
                        links.append('https://www.abc.net.au' +
                                     href.get('href'))
                    if(len(links) == length):
                        return links
                except Exception as e:
                    send_email("Exception occurred while fetching the links in ABC News" +
                               e + "url is " + url)
                    print("Exception occurred while fetching the links in ABC News",
                          e, "url is ", url)
        return links

    def parse(self):
        url_count = 0
        links = []
        url = self.makeURL()
        while (url_count < len(url)):
            hrefs = self.get_links(url[url_count])
            links.extend(hrefs)
            url_count += 1
        # filter the links that ends with .cms
        return links


class ScrollNewsCrawler():
    def __init__(self, interval):
        self.interval = interval

    def makeURL(self):
        url = []
        dateList = []
        dateList = self.date_dt()
        count_dt = 0
        while count_dt < len(dateList):
            a = dateList[count_dt]
            url.append('https://scroll.in/archives/' + a)
            count_dt += 1
        return url

    def date_dt(self):
        dateList = []
        startYear = self.interval.get("startYear")
        startMonth = self.interval.get("startMonth")
        startDay = self.interval.get("startDay")
        endYear = self.interval.get("endYear")
        endMonth = self.interval.get("endMonth")
        endDay = self.interval.get("endDay")

        def daterange(date1, date2):
            for n in range(int((date2 - date1).days)+1):
                yield date1 + timedelta(n)
        start_dt = date(startYear, startMonth, startDay)
        end_dt = date(endYear, endMonth, endDay)
        for dt in daterange(start_dt, end_dt):
            dateList.append(dt.strftime("%Y/%m/%d"))
        return dateList

    def get_links(self, url):
        links = []
        for i in range(10):
            for pageno in range(1000):
                length = len(links)
                page = CommonClass.get_page(url + '/page/' + str(pageno))
                try:
                    print("Try: ", i)
                    soup = BeautifulSoup(page)
                    mydivs = soup.findAll("li", {"class": "row-story"})
                    for division in mydivs:
                        href = division.find('a')
                        links.append(href.get('href'))
                    if(len(links) == length):
                        return links
                except Exception as e:
                    send_email("Exception occurred while fetching the links in Scroll News" +
                               e + "url is " + url)
                    print("Exception occurred while fetching the links in ScrollNews",
                          e, "url is ", url)
        return links

    def parse(self):
        url_count = 0
        links = []
        url = self.makeURL()
        while (url_count < len(url)):
            hrefs = self.get_links(url[url_count])
            links.extend(hrefs)
            url_count += 1
        # filter the links that ends with .cms
        return links


class OutlookCrawler():
    def __init__(self, interval):
        self.interval = interval

    def makeURL(self):
        url = []
        # ONE TIME RUN ONLY
        url.append('https://www.outlookindia.com/magazine/archive/all/')
        return url

    def date_dt(self):
        dateList = []
        startYear = self.interval.get("startYear")
        startMonth = self.interval.get("startMonth")
        startDay = self.interval.get("startDay")
        endYear = self.interval.get("endYear")
        endMonth = self.interval.get("endMonth")
        endDay = self.interval.get("endDay")

        def daterange(date1, date2):
            for n in range(int((date2 - date1).days)+1):
                yield date1 + timedelta(n)
        start_dt = date(startYear, startMonth, startDay)
        end_dt = date(endYear, endMonth, endDay)
        for dt in daterange(start_dt, end_dt):
            dateList.append(dt.strftime("%Y/%m/%d"))
        return dateList

    def get_links(self, url):
        links = []
        for i in range(10):
            for pageno in range(1000):
                length = len(links)
                page = CommonClass.get_page(url + str(pageno))
                try:
                    print("Try: ", i)
                    page = response.text
                    soup = BeautifulSoup(page)
                    mydivs = soup.findAll("div", {"class": "archive_wrp"})
                    mydivs = mydivs[0].findAll("li")

                    for page1 in mydivs:
                        href = page1.find('a')
                        response = requests.get(href.get('href'))
                        article = response.text
                        article = BeautifulSoup(article, 'lxml')
                        mydivs2 = article.findAll(
                            "div", {"class": "cont_head"})
                        for page2 in mydivs2:
                            href = page2.find('a')
                            links.append(
                                'https://www.outlookindia.com' + href.get('href'))
                    if(len(links) == length):
                        return links
                except Exception as e:
                    send_email("Exception occurred while fetching the links in OutLook" +
                               e + "url is " + url)
                    print("Exception occurred while fetching the links in Outlook",
                          e, "url is ", url)
        return links

    def parse(self):
        url_count = 0
        links = []
        url = self.makeURL()
        while (url_count < len(url)):
            hrefs = self.get_links(url[url_count])
            links.extend(hrefs)
            url_count += 1
        # filter the links that ends with .cms
        return links
