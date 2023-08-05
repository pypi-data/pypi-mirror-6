Grinder To Graphite
*******************


Overview
========

Grinder to Graphite (g2g) is a tool that analyzes the logs from
your Grinder tests, and sends the data into Graphite where it
can be visualized in a variety of ways.

Realtime test data may be sent to Graphite while your Grinder run
is in progress, or it may be sent to Graphite after your test is
completed.

Once the data is in Graphite you have a great amount of flexibility
in the types of reports and visualizations you want to generate.

*Example Graph*

.. image:: images/all_tps_stacked.png


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


Who should use Grinder Analyzer instead of g2g?
===============================================

If you just want to get some fast, simple graphs from your Grinder
run, without a lot of setup hassle, Grinder Analyzer is probably
a better bet for you than g2g.  See:

http://track.sourceforge.net


Source Code
===========

g2g code is hosted on Bitbucket.  See

https://bitbucket.org/travis_bear/grinder_to_graphite


Contents
========

.. toctree::
   :maxdepth: 1
   
   Quickstart <quickstart>
   Compatibility <compatibility>
   Installation Notes <installing>
   Configuring <configuring>
   Using Grinder to Graphite <using>
   Results <results>
   Gallery <gallery>
   Best Practices <best_practice>
   Additional Resources <resources>
