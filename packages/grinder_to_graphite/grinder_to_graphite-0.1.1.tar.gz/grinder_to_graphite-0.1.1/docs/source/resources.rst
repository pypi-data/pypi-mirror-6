Additional Resources
********************

Getting your Grinder data into Graphite is just one part of the
bigger picture.  Ideally, you want all your stuff -- application
data, OS-level performance metrics, Grinder data, deployment
timestamps -- to feed into a common location where it can all
be integrated.  These tools can help.

Exposing Application Data
=========================

Coda Hale Metrics
-----------------

This library makes it easy for Java-based servers to expose performance data
to JMX:

http://metrics.codahale.com/

It can optionally forward it to Graphite as well.


Statsd
------

A network daemon that listens for statistics,
like counters and timers, sent over UDP and sends aggregates to one or more
pluggable backend services (e.g., Graphite).

https://github.com/etsy/statsd/
http://codeascraft.com/2011/02/15/measure-anything-measure-everything/

Jmxtrans
--------

Java/JMX counters and application-level metrics can be fed to
Graphite using the JMXTrans tool:

https://github.com/jmxtrans/jmxtrans


Exposing OS-level data
======================

quickstatd
----------

OS-level metrics (CPU, mem, etc.) can be fed to Graphite via
quickstatd or collectd (with graphite plugin)

https://bitbucket.org/travis_bear/quickstatd

collectd
--------

Another good tool for collecting OS-level performance data and forwardng it to
Graphite:

http://collectd.org/



Keeping an eye on your data
===========================

If you have a bazillion metrics in your Graphite, it can be hard to keep an
eye on all of them, or notice when something interesting happens. The Kale
tools can help.

Kale has two parts: Skyline, and Oculus.

 * https://github.com/etsy/skyline
 * https://github.com/etsy/oculus
