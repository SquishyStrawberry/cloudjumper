#!/usr/bin/env python3
import bs4 
import re
import requests
import time


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
        # FIXME Handle other titling types
        # FIXME Provide variable iter_content size
        try:
            req = cls.session.get(url, stream=True, timeout=5)
        except TimeoutError:
            return
        if req.ok:
            chunk = next(req.iter_content(2048))
            soup = bs4.BeautifulSoup(chunk)
            if hasattr(soup.title, "text"):
                return soup.title.text
        req.close()
        
