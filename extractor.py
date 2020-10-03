from dotmap import DotMap
from pipeline.extractor import article_extractor
from pipeline.pipelines import ExtractedInformationStorage
import json
import urllib
import datetime
import hashlib
import boto3
import os


def from_html(html, publisher=None, url=None, download_date=None):
    """
    Extracts relevant information from an HTML page given as a string. This function does not invoke scrapy but only
    uses the article extractor. If you have the original URL make sure to provide it as this helps NewsPlease
    to extract the publishing date and title.
    :param html:
    :param url:
    :return:
    """
    extractor = article_extractor.Extractor([
        'newspaper_extractor', 'readability_extractor', 'date_extractor',
        'lang_detect_extractor', 'xpath_extractor'
    ])

    title_encoded = ''.encode()
    if not url:
        url = ''

    filename = urllib.parse.quote_plus(url) + '.json'

    item = {}
    item['spider_response'] = DotMap()
    item['spider_response'].body = html
    item['url'] = url
    item['source_domain'] = urllib.parse.urlparse(
        url).hostname.encode() if url != '' else ''.encode()
    item['html_title'] = title_encoded
    item['rss_title'] = title_encoded
    item['local_path'] = None
    item['filename'] = filename
    item['download_date'] = download_date
    item['modified_date'] = None
    item = extractor.extract(item, publisher)

    tmp_article = ExtractedInformationStorage.extract_relevant_info(item)
    final_article = ExtractedInformationStorage.convert_to_class(
        tmp_article)
    return final_article


def write_to_file(result, url, file_name):
    file_pointer = open(file_name, "w")

    diction = {
        'url': url,
        'Maintext': result.maintext,
        'author': result.authors,
        'description': result.description,
        'publish_date': str(result.date_publish),
        'image_url': result.image_url,
        'publisher_category': result.category,
        'title': result.title
    }

    json.dump(diction, file_pointer)
    file_pointer.write("\n")
    file_pointer.close()


def extract_information(data ):
    html = data['html']
    url = data['url']
    publisher = data['publisher']
    url = url.replace('"', '')
    download_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    result = from_html(html, publisher, url, download_date)

    return result
