from headers import Headers
import requests
import time

class SimpleCrawler(object):
    _results = {}

    @staticmethod
    def fetch_url(url, timeout=None, crawl_type=None):
        """
        Crawls the html content of the parameter url and returns the html
        :param url:
        :param timeout: in seconds, if None, the urllib default is used
        :return:
        """
        return SimpleCrawler._fetch_url(url, False, timeout=timeout, crawl_type=crawl_type)

    @staticmethod
    def _fetch_url(url, is_threaded, timeout=None, crawl_type=None):
        """
        Crawls the html content of the parameter url and saves the html in _results
        :param url:
        :param is_threaded: If True, results will be stored for later processing by the fetch_urls method. Else not.
        :param timeout: in seconds, if None, the urllib default is used
        :return: html of the url
        """
        # print("----------------------------------------Entered _fetch_urls", url)
        html = ""
        response = None
        for i in range(10):
            retries = 1
            print("Try to fetch the html:", i, "url:", url)
            try:
                userAgentDict = Headers.get_user_agent()
                if crawl_type == "Archives":  # using proxy only for Archives
                    # print("It is inside")
                    proxyDict = Headers.get_proxy()
                    response = requests.get(
                        url, proxies=proxyDict, headers=userAgentDict, timeout=10)
                else:
                    response = requests.get(
                        url, headers=userAgentDict, timeout=10)
                status = response.status_code
                print(url, status)
                if status == 200:
                    print("[Successful]", url)
                    html = response.text
                    break
            except Exception as e:
                print(
                    "Exception occurred for this url while getting the html for this archive article", url)
                print("the error: ", e)
                wait = retries*2
                time.sleep(wait)
                retries += 1
        if html == "":
            if response == None:
                raise Exception(
                    "[Error]Could not get the html file for this article url: "+url)
            else:
                raise Exception("[Error]Got the status code : ", str(status) + "\n" +
                                "[Error]Could not get the html file for this article url: "+url, response.text)
        if is_threaded:
            SimpleCrawler._results[url] = html
        # print(html)
        return html
