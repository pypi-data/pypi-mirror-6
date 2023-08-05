Installation Notes
******************

Install via Pip
===============
g2g is written in Python.  The best way to install g2g is via pip.
::

    pip install grinder_to_graphite 

You may need the python development libraries in place for
pyyaml support.  On debian-based systems, they can be installed
like this.
::

    sudo apt-get apt-get install python-dev

On Red-Hat based systems, you can get it like this.
::

    yum install python-devel


Virtualenv
==========
Using virtualenv is not required.  You can easily install g2g into
your core Python environment.  However, you will likely need to be
an admin user to to this, or you will need to preface the pip
command with *sudo*

However, there are many advantages to using virtualenv, and installing
g2g into its own environment is the recommended way to proceed.


Pypi
====
g2g runs more than twice as fast on pypy as it does on standard cpython.
If you will regularly be ingesting large amounts of data, consider
installing pypy.

http://pypy.org/download.html


Generate Configuration File
=========================== 
Once pip has installed g2g, you will need to generate a
g2g config file, and edit it to be suitable for your own
environment.  g2g comes with a command-line option to
generate a sample config file
::

    g2g -e


This will generate a file named 'g2g.sample.yaml'
in the current directory which you can use as the basis for 
creating your own configuration.


Graphite
========
There must be a running installation of Graphite on your
network for g2g to forward data to.  See the Graphite web site for
details on setting up and configuring Graphite

http://graphite.wikidot.com/

