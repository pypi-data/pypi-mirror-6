===================
Grinder to Graphite
===================

Overview
========

Grinder to Graphite (g2g) is a tool that analyzes the logs from
your Grinder load tests, and sends the data into Graphite where it
can be visualized in a variety of ways.

Realtime test data may be sent to Graphite while your Grinder run
is in progress, or it may be sent to Graphite after your test is
completed.

Once the data is in Graphite you have a great amount of flexibility
in the types of reports and visualizations you want to generate.


Who should use g2g?
===================

g2g may be a good match for you if any of the following are 
true:

 * You have access to a Graphite setup already, or you don't
   mind installing it.

 * You sometimes do long-duration Grinder runs and you don't
   want to wait for the run to complete before you can see
   charts of the incoming data.

 * You want to integrate data from The Grinder with data from a 
   variety of other sources.  (OS metrics like CPU use, application
   metrics like DB lookups per second, etc.)


Documentation
=============
Complete documentation and example graphs can be found at

https://grinder_to_graphite.readthedocs.org/en/latest/


Installation
============
g2g is installed from the command line.  Get pip, then run

    pip install grinder_to_graphite


Source
======
The Grinder to Graphite sources are hosted on bitbucket.

https://bitbucket.org/travis_bear/grinder_to_graphite

