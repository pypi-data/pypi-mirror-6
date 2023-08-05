Introduction
============

fourdigits.portlet.twitter is a twitter portlet for Plone.
It contains some nice features such as:

- show tweets of a certain twitter user(name)

- search on multiple hastags or strings (e.g. show the tweets of #plone and #zope in one portlet)

- combine searched tweets and tweets based on username

- filter tweets on curse words

- configurable number of items to display based on the username

- configurable number of items to display based on the search(es)

- filter tweets by language (multiple supported, such as nl and en)

- user pictures from twitter

- user info from twitter

- multilanguage support

- twitter API version 1.1

Hope you like the product!

Heavily based on collective.twitterportlet and a modified version of python-twitter.
Thanks guys!


Usage
-----

- Install the product in the Add-ons control panel in Plone.

- Use the Twitter Portlet Settings control panel to setup caching and
  a point to a proxy server if wanted. Also, add several keys and
  secrets to be able to display tweets. To get those keys and
  secrets, you must register your website as an application on
  `dev.twitter.com`_.

- Use the 'Manage portlets' link to add a Twitter portlet.

.. _`dev.twitter.com`: https://dev.twitter.com/apps
