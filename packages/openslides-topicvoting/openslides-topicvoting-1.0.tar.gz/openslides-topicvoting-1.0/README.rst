====================================
 Topic Voting Plugin for OpenSlides
====================================

Version 1.0 (2014-01-04)

Overview
========

This plugin for OpenSlides features a structured voting on topics using the
Sainte-Laguë method.


Requirements
============

OpenSlides 1.4.x (http://openslides.org/)


Install
=======

This is only an example instruction for install Topic Voting Plugin for
OpenSlides on GNU/Linux. It can also be installed as any other python
package and on other platforms, e. g. on Windows.

Change to a new directory::

    $ mkdir OpenSlides

    $ cd OpenSlides

Setup and activate a virtual environment and install OpenSlides and Topic
Voting Plugin for OpenSlides in it::

    $ virtualenv .virtualenv

    $ source .virtualenv/bin/activate

    $ pip install openslides-topicvoting==1.0

Start OpenSlides once to create its settings file if it does not exist yet::

    $ openslides

Stop OpenSlides::

    CTRL + C

Edit the settings.py file. You can find it in the directory openslides in
your user config path given in the environment variable $XDG_CONFIG_HOME.
Default is ``~/.config/openslides`` on GNU/Linux (and
``$HOME\AppData\Local\openslides`` on Windows). Insert the line
'openslides_topicvoting' into the INSTALLED_PLUGINS tuple::

    INSTALLED_PLUGINS = (
        'openslides_topicvoting',
    )

Synchronize the database to add the new tables::

    $ openslides --syncdb

Restart OpenSlides::

    $ openslides
