#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import requests
import urllib
from oauthlib import oauth1


class YBossResult(dict):
    """
    A dictionary that answers to attribute lookups
    result["url"] returns the same as result.url
    """

    def __getattr__(self, name):
        return self[name]


class YBossResponse(object):
    """
    Aggregates a list of YBossResult
    """

    def __init__(self, result=None, service="limitedweb"):
        result = result or {}
        self.results = []
        self.bossresponse = result.get('bossresponse', {})
        self.responsecode = self.bossresponse.get('responsecode')
        self.web = self.bossresponse.get(service, {})

        for k, v in self.web.iteritems():
            setattr(self, k, v)

    def __iter__(self):
        for result in self.results:
            yield YBossResult(result)

    def next(self):
        if not self.results:
            raise StopIteration
        return YBossResult(self.results.pop())

    def __len__(self):
        return len(self.results)

    def __getitem__(self, index):
        return YBossResult(self.results[index])

    def objects(self):
        return [YBossResult(result) for result in self.results]


class YBoss(object):
    """
    .: methods.
        __init__
        .: params
            key
            secret
            service = "limitedweb, web"
        search
        .: params.
            q = "string term"
            abstract = "long"
            style = "raw"
            type = "html, text"
            title = "some title"

    >>> from yboss import YBoss
    >>> boss = YBoss(key=key, secret=secret)
    >>> results = boss.search("Solar Filter")
    >>> for result in results:
    ...     print result
    {u"abstract": "...long text...",
     u"clickurl":"http://...",
     u"clickurl":"http://...",
     u"date": "",
     u"title": u"Solar Filter page etc..",
     u"url": "http://....."}
    >>> print result.url
    u"http://....."

    """

    def __init__(self, key, secret, service="limitedweb"):
        """
        Register on Yahoo Boss API to get key and secret
        """
        self.key = key
        self.secret = secret
        self.service = service
        self.base_url = 'http://yboss.yahooapis.com/ysearch/'

    def authenticate(self, url):
        """
        Each url call must be authenticated individually
        """
        client = oauth1.Client(self.key, client_secret=self.secret)
        self.uri, self.headers, self.body = client.sign(url)
        return self.headers

    def search(self, q, **kwargs):
        """
        Any keyed argument passed to .search is directly
        converted to querystring parameters in YBoss API
        Search filters must be passed together with search query (q)
        look: http://www.searchengineshowdown.com/features/yahoo/
        """
        if isinstance(q, unicode):
            q = q.encode("utf-8")

        params = {"q": q}
        params.update(kwargs)
        url = "{base_url}{service}?{params}".format(
            base_url=self.base_url,
            service=self.service,
            params=urllib.urlencode(params)
        ).replace("+", "%20")
        # Yboss API does not allow the use of + in urls
        response = requests.get(
            url,
            headers=self.authenticate(url)
        )

        if response.status_code >= 400:
            return YBossResponse(
                {
                    "error": True,
                    "status_code": response.status_code,
                    "content": response.content
                },
                service=self.service
            )

        return YBossResponse(
            json.loads(response.content),
            service=self.service
        )
