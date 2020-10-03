import random

class Headers():

    @staticmethod
    def get_user_agent():
        userAgentFilename = "useragents.txt"
        file_pointer = open(userAgentFilename, "r")
        data = file_pointer.read()
        userAgent_list = data.split("\n")
        userAgentDict = {
            'User-Agent': random.choice(userAgent_list)}
        return userAgentDict

    @staticmethod
    def get_proxy():
        ipProxyFilename = "proxy.txt"
        file_pointer = open(ipProxyFilename, "r")
        data = file_pointer.read()
        proxy_list = data.split("\n")
        proxyDict = {
            "https": "https://mrmomoeg-dest:9e7uun85ds2c@"+random.choice(proxy_list)}
        return proxyDict
