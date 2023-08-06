#!/usr/bin/env python
# encoding: utf-8

import re
import json
import urllib2
from bs4 import BeautifulSoup


class OpenGraph(dict):
    required_attrs = ['title', 'url']
    all_attrs = required_attrs + ['type', 'image', 'description']

    def __init__(self, url=None, html=None, **kwargs):
        for k in kwargs.keys():
            self[k] = kwargs[k]
        dict.__init__(self)

        if url is not None:
            self.url = url
            self.fetch(url)

        if html is not None:
            self.parse(html)

    def __setattr__(self, name, val):
        self[name] = val

    def __getattr__(self, name):
        return self[name]

    def fetch(self, url):
        try:
            raw = urllib2.urlopen(url)
            html = raw.read()
            return self.parse(html)
        except urllib2.HTTPError, e:
            print e, e.__class__
        except urllib2.URLError, e:
            print e, e.__class__
        except ValueError, e:
            print e, e.__class__

    def parse(self, html):
        doc = BeautifulSoup(html)
        ogs = doc.html.head.findAll(property=re.compile(r'^og:'))
        for og in ogs:
            if og.has_attr(u'content'):
                self[og[u'property'][3:]] = og[u'content']

        for attr in self.all_attrs:
            if not hasattr(self, attr):
                try:
                    self[attr] = getattr(self, 'fetch_%s' % attr)(doc)
                except AttributeError:
                    print "Could not find attribute fetch_%s" % attr

    def is_valid(self):
        return all([hasattr(self, attr) for attr in self.required_attrs])

    def to_html(self):
        if not self.is_valid():
            return u"<meta property=\"og:error\" content=\"og metadata is not valid\" />"

        meta = u""
        for key, value in self.iteritems():
            meta += u"\n<meta property=\"og:%s\" content=\"%s\" />" % (key, value)
        meta += u"\n"
        return meta

    def to_json(self):
        # TODO: force unicode
        if not self.is_valid():
            return json.dumps({'error': 'og metadata is not valid'})
        return json.dumps(self)

    def fetch_image(self, doc):
        images = [dict(img.attrs) for img in doc.html.body.findAll('img')]
        if images:
            return images[0]['src']
        return u''

    def fetch_title(self, doc):
        return doc.html.head.title.text

    def fetch_description(self, doc):
        return doc.html.head.description.text

    def fetch_type(self, doc):
        return 'other'

    def fetch_url(self, doc):
        return self.url