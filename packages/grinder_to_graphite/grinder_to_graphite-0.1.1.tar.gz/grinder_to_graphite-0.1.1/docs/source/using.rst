Usage
*****

Running
=======
'g2g' is the Grinder to Graphite executable.  Normal usage (after 
adjusting the values in your sample config file to be appropriate 
for your environment) looks like this:
::

    g2g  <config_file>
    
Once you have established a useful g2g configuration file, it is common
to use it over and over.  You can set a default config file like this:
::

    g2g -s <g2g config_file>
    

or 

::

    g2g --set-config-file=<g2g config_file>
    

After you have set a default config file, g2g can then be optionally
invoked without specifying any other configuration.
::

    g2g
    


Modes
=====

There are three primary ways to use g2g:

Grinder Run Completed: Default Mode
-----------------------------------

The most common use of grinder to graphite is the case where
you have completed a Grinder run and you want to send the 
results to Graphite. This is the default usage, which is 
described above.  No
special options are required.


Grinder Run In Progress: Follow Mode
------------------------------------

If you have a long-duration Grinder run in progress, you might
not want to wait for it to finish before you begin forwarding
results to Graphite.  g2g supports this via a follow (tailing)
mode, where new results are continually forwarded to graphite.

For follow mode to work, you will first need to do a 
quick run with your grinder script to generate a valid mapping 
file.  A mapping file is a grinder log file that most likely has a 
name like <hostname>-0.log.  Once a valid mapping
file is in place, you can do realtime reporting for your Grinder
script as many times as you want.

Tailing mode can be enabled in the config file by setting
*follow* to True.  It can also be enabled on the command
line using either of these options:
::

    g2g -f

or

::

    g2g --follow=True


Grinder Run In Progress: Resume Mode
------------------------------------

For long-running Grinder tests, there is an alternate to follow
mode.  It is possible to re-run g2g manually on a Grinder log
that is still being written, and process only at the data that is
new since the last time g2g has been run.  This avoids re-processing
potentially large amounts of data while giving you control over
when g2g runs.


Resuming log processing can be enabled in the config by setting *resume* to
True.  It can also be specified on the command line using either of
these options
::

    g2g -r

or

::

    g2g --resume=True


Options
=======

Many of the settings in the g2g config file can be overridden
on the command line.  To see a full list of available options:
::

    g2g --help


Getting Help
============

Questions about g2g can be asked on the grinder-use mailing list.
To subscribe, see

http://sourceforge.net/p/grinder/mailman/

Bugs can be reported to the project site on Bitbucket.

https://bitbucket.org/travis_bear/grinder_to_graphite/issues