Quickstart
**********


Prerequisites
=============


Graphite
--------

If you don't already have a Graphite server running on your network, 
you will need to set one up. See the Graphite web site for
details on setting up and configuring Graphite

http://graphite.wikidot.com/

Pip
---

Pip is the best way to install python packages like Grinder to Graphite.
If you don't have pip, there are many easy ways to get it.  See

http://www.pip-installer.org/en/latest/installing.html


Grinder to Graphite
===================

Get it!
-------

Install it with pip

::

    pip install grinder_to_graphite 


Configure it!
-------------

g2g comes with a command-line option to generate a sample config file
::

    g2g -e

This will generate a file named 'g2g.sample.yaml'
which you can use as the basis for creating your own
configuration.


Run it!
-------

Once you have your Grinder logs in place that you want to ingest into
Graphite, invoke g2g
::

    g2g <config file>


View it!
--------

Your Grinder test data should now be visible in Graphite
