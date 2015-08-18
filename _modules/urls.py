#!/usr/bin/env python3
import requests
import bs4 
import re


class UrlTitle(object):
    session = requests.Session()
    validator = re.compile(r'^https?://'  # http:// or https://
                           r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
                           r'localhost|'  # localhost...
                           r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
                           r'(?::\d+)?'  # optional port
                           r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    def __init__(self, bot, config):
        self.bot = bot
        self.bot.subscribe(publisher=self.bot.PUBLISHERS["FULL_MESSAGE"],
                           handler=self.find_urls)

    def find_urls(self, sender, message):
        msg = self.bot.get_message("urltitle")
        for url in self.validator.findall(message):
            title = self.get_title(url)
            if title is not None:
                self.bot.send_action(msg.format(title=title))
            
    @classmethod
    def get_title(cls, url):
        req = cls.session.get(url, timeout=5)
        if req.ok:
            soup = bs4.BeautifulSoup(req.text)
            return soup.title.text

