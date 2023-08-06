=========
farm-news
=========

Overview
========

A django application which provides news articles and related views.

Installation
============

* Install with ``pip install farm-news``.
* Add ``news`` to your installed apps.
* Set ``NUM_LATEST_ARTICLES`` in your settings, default is 3.
* Add ``news.context_processors.latest_articles`` to your ``TEMPLATE_CONTEXT_PROCESSORS``.
* Run ``manage.py syncdb``.
* Run ``manage.py migrate news``.

Usage
=====
First you will need to add at least one ``Article`` in the admin.

Then override the templates by creating new ones in your own app's template directory
* Article list found at /news/ ``news/article_list.html``
* Article detail found at /news/<slug> ``news/article_detail.html``

You can also include the following template like this:
* Article list (useful for including in a sidebar) ``{% include 'news/article_list.html' %}``

Or create your own.

License
=======
Imperavi Redactor is licensed under Creative Commons Attribution-NonCommercial 3.0 license.

For commercial use please buy license here: http://redactorjs.com/download/ or use earlier version.

Contact
=======
jon@wearefarm.com
