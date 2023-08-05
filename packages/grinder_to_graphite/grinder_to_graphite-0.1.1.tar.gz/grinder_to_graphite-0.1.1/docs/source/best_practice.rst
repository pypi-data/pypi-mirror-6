Best Practices
**************

Ease of Use
===========

Use virtualenv
--------------

It will make your life easier.


Set a default config file
-------------------------

It is pretty common to want to use the same g2g config file for many different
invocations of g2g.  If you set a default config file, your usage changes from
::

    g2g <config file>


becomes simply
::

    g2g



Choose prefix and suffix carefully
----------------------------------

These can help you effectively manage your Graphite namespace.  Divide
up your metrics by application, type, or any other criteria you can
imagine.

*Examples:*

   +---------------+------------------+
   | Carbon Prefix | Carbon Suffix    |
   +===============+==================+
   | <none>        | grinder          |
   +---------------+------------------+
   | <none>        | grinder.app_name |
   +---------------+------------------+
   | grinder       | <none>           |
   +---------------+------------------+


Performance
===========

Use pypy
--------

In many cases, g2g runs more than twice as fast on pypy as it does on cpython.
If you will regularly be ingesting large amounts of data, consider installing
pypy.


Be judicious when configuring response time metrics
---------------------------------------------------

Response time groups and percentiles can add numerous new metrics to Graphite.
Be sure you've selected the ones you need.  If you change these settings
frequently, you could wind up with many stale metrics in Graphite, making
it hard to see which ones currently apply.


Possible gotchas
----------------
g2g has to keep each grinder transaction in memory until it is flushed
to Graphite. It's possible
that very high TPS Grinder tests, coupled with very long graphite reporting 
intervals, could cause memory issues in g2g.  This has not been a problem
in any of the testing we've done so far.  However, if this happens you
can lower
the carbon_interval_seconds setting to reduce the amount of data g2g
has to keep in memory.  Because this approach will cause only a subset
of the available data to be retained by Graphite, it's best to only
use it if you are actually having g2g memory problems.

