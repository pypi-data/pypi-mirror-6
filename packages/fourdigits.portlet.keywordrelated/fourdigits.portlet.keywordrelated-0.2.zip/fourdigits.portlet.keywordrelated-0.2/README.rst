.. image:: https://travis-ci.org/collective/fourdigits.portlet.keywordrelated.png
  :target: https://travis-ci.org/collective/fourdigits.portlet.keywordrelated

.. image:: https://coveralls.io/repos/collective/fourdigits.portlet.keywordrelated/badge.png
  :target: https://coveralls.io/r/collective/fourdigits.portlet.keywordrelated

.. contents::

Introduction
============

This product gives you a new portlet: The KeywordRelatedPortlet.
It shows other content in the site that has the same tags
(aka. keywords, aka. Subject) as the current page.


Installation
============

In a buildout, add ``fourdigits.portlet.keywordrelated`` to the eggs and
re-run buildout.

After restarting your site, got to Site setup, and install the products
through the Add-on products form.


Configuration
=============

Currently the only configuration option is the number of items to show.


Compatibility
=============

The add-on was tested on Plone 4.1.
It should work on any Plone version, from Plone 3 upwards.


Future features
===============

In the future, this portlet should allow:
* filtering items on content type
* influencing the sorting mechanism

Pull requests are most welcome.


Issues
======

Please file any issues with this product at
https://github.com/collective/fourdigits.portlet.keywordrelated/issues
