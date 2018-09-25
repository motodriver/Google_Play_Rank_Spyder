#! /usr/bin/env python
# -*- coding:utf-8 -*-

import urllib
from HTMLParser import HTMLParser
import re
import json
import logging


class GooglePlayDetailParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.data = []
        self.start_detail = False
        self.start_appname = False
        self.start_developer = False
        self.start_script = False
        self.model = {}
        self.re_nbp = re.compile(r"var nbp='(.*)\\n';var")
        self.nbp = None
        self.last_data = None

    def get_data(self):
        return self.data

    def get_nbp(self):
        # print "Get Nbp", self.nbp
        logging.info("GooglePlayDetailParser:get_nbp:[%s]" % self.nbp)
        return self.nbp

    def reset_nbp(self):
        self.nbp = None

    def handle_starttag(self, tag, attrs):
        attrs = self.attrs_to_dict(attrs)
        class_name = attrs.get("class", "")
        self.last_data = ""
        if tag == "div" and class_name == "details":
            self.start_detail = True
            self.model = {}

        if self.start_detail and class_name == "title" and tag == "a":
            self.start_appname = True
            href = attrs.get("href", "")
            if href != "":
                pre, suf = href.split("?id=", 1)
                package = urllib.unquote_plus(suf)
                self.model["package"] = package
                # print "package", package
            title = attrs.get("title", "")
            if title != "":
                self.model["appname"] = title

        if self.start_detail and class_name == "subtitle" and tag == "a":
            self.start_developer = True
            href = attrs.get("href", "")
            title = attrs.get("title", "").strip()
            # developer = None
            # if not href == "":
            pre, suf = href.split("?id=", 1)
            developer = urllib.unquote_plus(suf)
            developer_name = title
            self.model["developer"] = developer
            self.model["developer_name"] = developer_name

        if tag == "script":
            self.start_script = True

    def handle_endtag(self, tag):
        _text = ""
        if isinstance(self.last_data, (str, unicode)):
            _text = self.last_data.strip()
        if tag == "script":
            self.start_script = False
        if tag == "a" and self.start_appname:
            if len(_text) > len(self.model.get('appname', '')):
                self.model['appname'] = _text

            self.start_appname = False
        if tag == "a" and self.start_developer:
            if len(_text) > len(self.model.get('developer', '')):
                self.model['developer'] = _text
            # end
            self.data.append(self.model)
            self.start_detail = False
            self.start_developer = False

        self.last_data = ""

    def handle_data(self, data):
        if self.start_script:
            try:
                m = self.re_nbp.search(data)
                if m:
                    nbp_text = m.group(1)
                    nbp_value = json.loads(nbp_text.decode("unicode-escape"))
                    self.nbp = nbp_value[1]
            except Exception as e:
                logging.exception("GooglePlayDetailParser:handle_data:Exception:%s" % e)
            finally:
                return
        else:
            if not isinstance(self.last_data, (str, unicode)):
                self.last_data = ""
            self.last_data += data

    def handle_charref(self, ref):  # No changes here
        self.handle_entityref('#' + ref)

    def handle_entityref(self, ref):  # No changes here either
        self.handle_data(self.unescape("&%s;" % ref))

    @staticmethod
    def attrs_to_dict(attrs):
        map = {}
        for attr in attrs:
            key, val = attr
            map[key] = val
        return map
