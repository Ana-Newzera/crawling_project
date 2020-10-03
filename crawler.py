import json
import boto3
import botocore
import os
import sys
import requests
import re
from botocore.exceptions import ClientError
import datetime
from requests.utils import requote_uri
import hashlib
import mariadb
from simplecrawler.simple_crawler import SimpleCrawler
from extractor import extract_information

def sql_connection():
    try:
        # con = sqlite3.connect('Crawler_extractor.db')
        # return con
        con = mariadb.connect(
        user="admin",
        password="admin",
        host="127.0.0.1",
        port=3306,
        database="archivecrawler")
        return con
    except Error:
        print(Error)

def update_third(urlHash,date):
    con = sql_connection()
    cursorObj = con.cursor()
    query = "UPDATE `article-state-"+ date[5:7]+ "` SET state='extracted' where url_hash='" + str(urlHash)+"'"
    cursorObj.execute(query)
    con.commit()
    con.close()


def write_to_file(html, url, publisher, file_name, type_of_url):
    file_pointer = open(file_name, "w")
    print("hi")
    diction = {
        "publisher": publisher,
        "url": url,
        "html": html,
        "type": type_of_url
    }
    result = extract_information(diction)
    print(result)
    diction1 = {
        'url': url,
        'Maintext': result.maintext,
        'author': result.authors,
        'description': result.description,
        'publish_date': str(result.date_publish),
        'image_url': result.image_url,
        'publisher_category': result.category,
        'title': result.title
    }
    json.dump(diction1, file_pointer)
    file_pointer.close()


def add_first(urlHash, url, publisher, date):
    url = requote_uri(url)
    con = sql_connection()
    cursorObj = con.cursor()
    query = "INSERT INTO `article-state-"+ date[5:7]+ "`(url_hash, url, publisher, publish_date) values( '" + str(urlHash)+ "' , '"+url+"','"+publisher+"', '"+date+"')"
    cursorObj.execute(query)
    con.commit()
    
    con.close()


def update_second(urlHash,date):
    con = sql_connection()
    cursorObj = con.cursor()
    query = "UPDATE `article-state-"+ date[5:7]+ "` SET state='crawled' where url_hash='" + str(urlHash)+"'"
    cursorObj.execute(query)
    con.commit()
    con.close()


def check_exist(urlHash,date):
    con = sql_connection()
    cursorObj = con.cursor()
    print(urlHash)
    query = "select state from `article-state-"+ date[5:7]+ "` where url_hash='" + str(urlHash)+"'"
    cursorObj.execute(query)
    record = cursorObj.fetchall()
    con.commit()
    con.close()
    return record

def archives(url,publisher,date):
    
    urlHash = hashlib.md5(url.encode()).hexdigest()

    check = check_exist(urlHash,date)
    if len(check) > 0:
        value = check[0][0]
        if value == "extracted":
            # print("Already successfully extracted ", url)
            return
        elif value == "crawled":
            print(
                "Successfullly crawled, updating the html file in the s3 bucket for ", url)
        else:
            print("Already in is_crawling state, continuing for url ", url)
    else:
        add_first(urlHash, url, publisher, date)

    a = re.sub('[\W_]+', '-', url)

    #file_name = "/tmp/output.json"
    key_folder = "html_files/" + publisher + "/" + date
    try:
        os.mkdir("html_files/" + publisher)
    except Exception as e:
        print("")
    try:
        os.mkdir(key_folder)
    except Exception as e:
        print("")


    key_file = key_folder + "/" + a + ".json"
    try:
        html = SimpleCrawler.fetch_url(url, crawl_type="Archives")
        try:
            os.mkdir(key_folder)
        except Exception as e:
            print(e)
            print("folder already there")
        update_second(urlHash,date)
        write_to_file(html, url, publisher, key_file, "archives")
        update_third(urlHash,date)
    except Exception as e:
        print(
            "[Error]Exception occurred while getting the html for the article \n", e)


def get_html(url,publisher,date):
    archives(url,publisher,date)

