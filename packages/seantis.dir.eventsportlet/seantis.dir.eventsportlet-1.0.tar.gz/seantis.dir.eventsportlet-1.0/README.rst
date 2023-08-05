Seantis Events Portlet
======================

Portlet for displaying events.

The portlet (seantis.dir.eventsportlet) shows events coming from a directory of
events (seantis.dir.events).


Dependencies
------------

seantis.dir.eventsportlet relies on Plone 4.3+ with dexterity.


Installation
------------

1. Use Plone 4.3 or newer

::

    extends =
        http://dist.plone.org/release/4.3/versions.cfg

2. Add the module to your instance eggs

::

    [instance]
    eggs +=
        seantis.dir.eventsportlet


3. Ensure that the i18n files are compiled by adding

::

    [instance]
    ...
    environment-vars = 
        ...
        zope_i18n_compile_mo_files true


4. Install dexterity and seantis.dir.eventsportlet using portal_quickinstaller


Build Status
------------

.. image:: https://api.travis-ci.org/seantis/seantis.dir.eventsportlet.png?branch=master
  :target: https://travis-ci.org/seantis/seantis.dir.eventsportlet
  :alt: Build Status


Coverage
--------

.. image:: https://coveralls.io/repos/seantis/seantis.dir.eventsportlet/badge.png
  :target: https://coveralls.io/r/seantis/seantis.dir.eventsportlet
  :alt: Project Coverage


Latests PyPI Release
--------------------
.. image:: https://pypip.in/v/seantis.dir.eventsportlet/badge.png
  :target: https://crate.io/packages/seantis.dir.eventsportlet
  :alt: Latest PyPI Release


License
-------
seantis.dir.eventsportlet is released under GPL v2
