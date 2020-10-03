import json
import os
from botocore.exceptions import ClientError
import logging
import boto3
import datetime
from datetime import date, timedelta
import sys
import mariadb
from custom_crawler import OutlookCrawler, ScrollNewsCrawler, ABCNewsCrawler, EBMNewsCrawler, EuroNewsCrawler, BusinessLineCrawler, DailyExpressCrawler, IndiaTodayCrawler, TheHinduCrawler, EconomicTimesCrawler, TimesOfIndiaCrawler, IndianExpressCrawler, NDTVCrawler, OneIndiaCrawler, DailyMailCrawler
from crawler import get_html, sql_connection

from crawler import sql_connection
def send_email(records):
    urls = ""
    for url in records['failed']:
        urls += str(url)
        urls += "<br />"
    # Both the ids must be verified via aws sns
    SENDER = "vipul@newzera.com"
    RECIPIENT = "vipul@newzera.com"

    #CONFIGURATION_SET = "ConfigSet"
    AWS_REGION = "ap-south-1"

    SUBJECT = "Articles extracted"

    BODY_TEXT = ("Data Report:")

    BODY_HTML = """<html>
    <head></head>
    <body>
    <h1></h1>
    <Table>
        <tr>
            <th> Status</th>
            <th> Status</th>
        </tr>
        <tr>
            <th> Extracted</th>
            <th> Crawled</th>
        </tr>
        <tr>
            <th> """+str(records['records'])+"""</th>
            <th>  """+str(len(records['failed']))+"""</th>
        </tr>
        
    <p>""" + "Number of articles extracted for publisher:"+publisher + " are:  " + str(records['records']) +"""</p><br />
    <p>""" + "Number of articles Crawled for publisher:"+publisher + " are:  " + str(len(records['failed'])) +"""</p><br />
    List Of Failed Urls:<br />
    """ +urls+"""
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


def handler(publisher, interval):

    if publisher == "TheHindu":
        crawler = TheHinduCrawler(interval)
        urls = crawler.parse()
        return urls

    elif publisher == "EconomicTimes":
        crawler = EconomicTimesCrawler(interval)
        urls = crawler.parse()
        return urls

    elif publisher == "TimesofIndia":
        crawler = TimesOfIndiaCrawler(interval)
        urls = crawler.parse()
        return urls

    elif publisher == "TheIndianExpress":
        crawler = IndianExpressCrawler(interval)
        urls = crawler.parse()
        return urls

    elif publisher == "NDTV":
        crawler = NDTVCrawler(interval)
        urls = crawler.parse()
        return urls

    elif publisher == "OneIndia":
        crawler = OneIndiaCrawler(interval)
        urls = crawler.parse()
        return urls

    elif publisher == "DailyMail":
        crawler = DailyMailCrawler(interval)
        urls = crawler.parse()
        return urls

    elif publisher == "IndiaToday":
        crawler = IndiaTodayCrawler(interval)
        urls = crawler.parse()
        return urls

    elif publisher == "DailyExpress":
        crawler = DailyExpressCrawler(interval)
        urls = crawler.parse()
        return urls

    elif publisher == "BusinessLine":
        crawler = BusinessLineCrawler(interval)
        urls = crawler.parse()
        return urls

    elif publisher == "EuroNews":
        crawler = EuroNewsCrawler(interval)
        urls = crawler.parse()
        return urls

    elif publisher == "EBMNews":
        crawler = EBMNewsCrawler(interval)
        urls = crawler.parse()
        return urls

    elif publisher == "ABCNews":
        crawler = ABCNewsCrawler(interval)
        urls = crawler.parse()
        return urls

    elif publisher == "ScrollNews":
        crawler = ScrollNewsCrawler(interval)
        urls = crawler.parse()
        return urls

    elif publisher == "Outlook":
        crawler = OutlookCrawler(interval)
        urls = crawler.parse()
        return urls

def find_no(publisher,date):
    con = sql_connection()
    cursorObj = con.cursor()
    date = date.strftime("%Y-%m-%d")
    query = "select state from `article-state-"+ date[5:7]+ "` where publisher='" + str(publisher)+"' and publish_date='" + str(date) +"' and state='extracted'"
    cursorObj.execute(query)
    record = cursorObj.fetchall()
    con.commit()
    con.close()
    return len(record)
def lambda_handler(publisher,start_date,end_date):
    records = 0
    failed_urls = []

    delta = timedelta(days=1)
    while start_date <= end_date:

        interval = {
            "startYear": start_date.year,
            "startMonth": start_date.month,
            "startDay": start_date.day,
            "endYear": start_date.year,
            "endMonth": start_date.month,
            "endDay": start_date.day
        }
        str_date = start_date.strftime("%Y-%m-%d")
        
        con = sql_connection()
        cursorObj = con.cursor()
        date = start_date.strftime("%Y-%m-%d")
        query = "select * from `article-state-"+ date[5:7]+ "` where publisher='" + str(publisher)+"' and publish_date='" + str(date) +"' and state<>'extracted'"
        cursorObj.execute(query)
        record = cursorObj.fetchall()
        query_publish = "select * from `article-state-"+ date[5:7]+ "` where publisher='" + str(publisher)+"' and publish_date='" + str(date) +"'"
        cursorObj.execute(query_publish)
        record_publish = cursorObj.fetchall()
        con.close()
        if len(record_publish) != 0:
            if len(record) == 0:
                start_date +=delta
                continue
        start_urls = handler(publisher, interval)
        for index, i in enumerate(start_urls):
            get_html(i,publisher,str_date)
        records += find_no(publisher,start_date)
        con = sql_connection()
        cursorObj = con.cursor()
        date = start_date.strftime("%Y-%m-%d")
        query = "select url from `article-state-"+ date[5:7]+ "` where publisher='" + str(publisher)+"' and publish_date='" + str(date) +"' and state='crawled'"
        cursorObj.execute(query)
        record = cursorObj.fetchall()
        print(record)
        for ur in record:
            failed_urls.append(ur)
        con.commit()
        con.close()
        start_date += delta
    
    ret_dict = {
        'records':records,
        'failed' :failed_urls
    }
    return ret_dict


publisher = sys.argv[1]
start_date = sys.argv[2]
end_date = sys.argv[3]

start_date = start_date.split('-')

s_day = start_date[0]
s_month = start_date[1]
s_year = start_date[2]

end_date = end_date.split('-')

e_day = end_date[0]
e_month = end_date[1]
e_year = end_date[2]

s = date(int(s_year),int(s_month),int(s_day))
e = date(int(e_year),int(e_month),int(e_day))


records = lambda_handler(publisher,s,e)
send_email(records)
