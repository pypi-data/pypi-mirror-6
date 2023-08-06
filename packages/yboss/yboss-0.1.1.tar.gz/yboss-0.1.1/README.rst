===============================
Ybosspy
===============================

.. image:: https://badge.fury.io/py/yboss.png
    :target: http://badge.fury.io/py/yboss

.. image:: https://pypip.in/d/yboss/badge.png
	:target: https://crate.io/packages/yboss?version=latest


Python wrapper for Yahoo Boss API

* Free software: BSD license
* Documentation: http://yboss.rtfd.org.

Install
-------
::

    pip install yboss

Usage
-----
::

    from yboss import YBoss 
    boss = YBoss(key=key, secret=secret)  
    results = boss.search("Solar Filter")  
    for result in results:  
	print result  

    {u"abstract": "...long text...",
     u"clickurl":"http://...",
     u"clickurl":"http://...",
     u"date": "",
     u"title": u"Solar Filter page etc..",
     u"url": "http://....."}

    print result.url
    u"http://....."


Features
--------

- Authenticate and search in YBoss API


