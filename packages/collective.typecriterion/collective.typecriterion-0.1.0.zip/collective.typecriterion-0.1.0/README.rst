Introduction
============

This product will add to your Plone control panel a new entry: "*Type criterion settings*".

From this panel you can add a set of definition about general content types, which are defined using
a group of existing Plone native types.

.. image:: http://keul.it/images/blog/2014-04/typecriterion-controlpanel.png
   :alt: Type criterion settings

For example: you can define a new general type called "Textual contents" that is defined by grouping
Pages, News and Events.

All those definitions can be used in Plone collections by using the new "*General type*" criteria.

.. image:: http://keul.it/images/blog/2014-04/collection-search-generaltype.png
   :alt: General type criterion in action

In brief: searching for new general types defined means take a search onto all grouped native types.

Motivation
==========

I found a lot of Plone users that hardly learn the difference between content types.
For example: the difference between a Page and a File is often too tiny in the mind of the site contributor.
In other situations a grouping feature (like: "look for all multimedia type") can be useful.

With this approach users can only care about some general family on types that a power user defined.

Finally 3rd party products could extend an existing list on types, and when a content type change (because it
has been replaced by another, better product) you only care about reconfiguring the general type, not all
the collections in the site.

Compatibility
=============

This product has been tested on Plone 4.3.2, but required `plone.app.querystring 1.2`__ or better.

__ https://pypi.python.org/pypi/plone.app.querystring/1.2.0

If you have problems installing this add-on, try to pin plone.app.querystring to version 1.2::

    [buildout]
    ...
    versions=versions
    ...
    [versions]
    plone.app.querystring = 1.2.0
    ...

TODO
====

A Generic Setup import step for configuring types.
