#! /usr/bin/env python
# -*- coding:utf-8 -*-


import requests
import urllib
import logging
from GooglePlayDetailParser import GooglePlayDetailParser


class GooglePlaySearchAPI(object):
    def __init__(self, proxies=None):
        self.proxies = proxies
        self.parser = GooglePlayDetailParser()
        self.debug_msg = []

    def search(self, search, lang="en", country=None):
        if isinstance(search, unicode):
            search = search.encode('utf-8')
        self.debug_msg = [[search, lang]]
        logging.info("GooglePlaySearchAPI:search:[%s]" % self.debug_msg)
        html = self.net_get(search, lang, country)
        if not html:
            logging.error("[FAIL]GooglePlaySearchAPI(%s):Get[%s]" % (self.debug_msg, html))
            return None
        else:
            logging.info("[SUCCESS]GooglePlaySearchAPI:search:Get(%s):[size:%s]" % (self.debug_msg, [len(html)]))
        try:
            self.parser.reset_nbp()
            self.parser.feed(html)
            # print html
            nbp = self.parser.get_nbp()
            while nbp:
                html = self.net_get_nbp(search, lang, nbp, country)
                if not html:
                    break
                self.parser.reset_nbp()
                self.parser.feed(html)
                nbp = self.parser.get_nbp()
        except Exception as e:
            logging.info("GooglePlaySearchAPI:search:Exception:%s" % [self.debug_msg, e])
        finally:
            rest = self.parser.get_data()
            if rest:
                logging.info("[SUCCESS]:GooglePlaySearchAPI:search:return:[%s]:[%s]" % (self.debug_msg, rest))
            else:
                logging.error("[FAIL]:GooglePlaySearchAPI:search:return:[%s][%s]" % (self.debug_msg, rest))
            return self.parser.get_data()

    def net_get(self, search, lang="en", country=None):
        if isinstance(search, unicode):
            search = search.encode('utf-8')
        url = "https://play.google.com/store/search?&c=apps&q={search}&hl={lang}".format(
            search=urllib.quote_plus(search), lang=lang)
        if country:
            url += '&gl=%s' % country
        headers = {
            "origin": "https://play.google.com",
            "content-type": "application/x-www-form-urlencoded;charset=UTF-8",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "accept-language": "{lang},{lang_short};q=1.0".format(lang=lang, lang_short=lang[:2]),
            "cache-control": "no-cache",
            "authority": "play.google.com",
            "pragma": "no-cache",
            "x-chrome-uma-enabled": "1",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/55.0.2883.87 Safari/537.36",
            "referer": "https://play.google.com/store/search?q={search}&hl={lang}".format(
                search=urllib.quote_plus(search), lang=lang)
        }
        logging.info("%s\nGooglePlaySearchAPI[%s]:net_get:url:%s\n%s" % ('=' * 20, self.debug_msg, url, headers))
        # print headers
        text = None
        try:
            resp = requests.get(url, headers=headers, proxies=self.proxies,
                                verify=False)
            if not resp:
                logging.error("[FAIL]GooglePlaySearchAPI[%s]:net_get():get(%s):[%s]" % (self.debug_msg, url, resp))
            text = resp.text
        except Exception as e:
            logging.exception("GooglePlaySearchAPI[%s]:net_get:[%s]" % (self.debug_msg, e))
        finally:
            return text

    def net_get_nbp(self, search, lang="en", nbp=None, country=None):
        if not nbp:
            return None
        url = "https://play.google.com/store/search?q={search}&c=apps&authuser=0&hl={lang}".format(
            search=urllib.quote_plus(search), lang=lang)
        if country:
            url += '&gl=%s' % country
        data = "start=0&num=0&numChildren=0&pagTok={nbp}&pagtt=1&cctcss=square-cover&cllayout=NORMAL&ipf=1&xhr=1".format(
            nbp=nbp)
        headers = {
            "origin": "https://play.google.com",
            "content-type": "application/x-www-form-urlencoded;charset=UTF-8",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "accept-language": "{lang},{lang_short};q=1.0".format(lang=lang, lang_short=lang[:2]),
            "cache-control": "no-cache",
            "authority": "play.google.com",
            "pragma": "no-cache",
            "x-chrome-uma-enabled": "1",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/55.0.2883.87 Safari/537.36",
            "referer": "https://play.google.com/store/search?q={search}".format(search=urllib.quote_plus(search))
        }
        text = None
        try:
            resp = requests.post(url, headers=headers, data=data, proxies=self.proxies,
                                 verify="/etc/pki/ca-trust/extracted/openssl/ca-bundle.trust.crt")
            text = resp.text
        except Exception as e:
            logging.exception("GooglePlaySearchAPI:net_get_nbp:Exception:%s" % e)
        finally:
            return text


# --------- test ---------


if __name__ == "__main__":
    import json
    import utils
    from GooglePlayDetailParser import GooglePlayDetailParser

    p = GooglePlayDetailParser()
    utils.init_log("main.log", True)

    proxies = {
        "https": "http://127.0.0.1:8118",
        "http": "http://127.0.0.1:8118",
    }
    api = GooglePlaySearchAPI(proxies=proxies)
    data = api.search("locker", "en", 'US')
    # html = api.net_get("Погода", "ru-RU")
    # print html
    # p.feed(html)
    # data = p.get_data()
    # print len(data)
    with open("search.json", 'w') as f:
        f.write(json.dumps(data, indent=4, sort_keys=True, ensure_ascii=False).encode('utf-8'))
