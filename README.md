django-fulltextfeed
===================

Parses remote Atom/RSS feeds and replaces their articles with full-text versions.

Why?
----

Some websites only offer spoiler versions of articles in their Atom/RSS feeds. This tool enables you to convert these feeds into full-text Atom feeds, which you may read in your favorite Atom/RSS reader without actually having to visit the website.

How does it work?
-----------------

Whenenver you (or your feed reader) accesses a feed through *django-fulltextfeed*, your server downloads and parses the actual Atom/RSS feed of the source site. It then follows the links in the feed and downloads the entire article from the site. For each feed a **XPath** expression can be configured to extract only the article from the site, without any site layout. When all articles have been downloaded, a full-text Atom feed is returned to your browser or feed reader.

For faster loading and reduced load on the websites the full-text articles are cached in a database.

Requirements
------------

* Django 1.4 or greater
* python-lxml
* python-feedparser

Installation
------------

1. Place the *fulltextfeed* package in your Django project
2. Add *fulltextfeed* to `INSTALLED_APPS` in your settings file
3. Include `fulltextfeed.urls` in your URL config
4. Run `syncdb`
5. Open Django's built-in admin site and configure your feeds
