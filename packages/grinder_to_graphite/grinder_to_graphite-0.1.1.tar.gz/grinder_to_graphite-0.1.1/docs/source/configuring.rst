Configuring
***********

Sections
========

The g2g config file has these sections


   +-------------+-----------+------------------------------------------------------+
   | Section     | Required? |  Notes                                               |
   +=============+===========+======================================================+
   | g2g.carbon  | yes       | This section contains settings relevant to           |
   |             |           | your graphite installation.                          |
   +-------------+-----------+------------------------------------------------------+
   |g2g.data     | yes       | This section tells g2g about your local              |
   |             |           | Grinder log files.                                   |
   +-------------+-----------+------------------------------------------------------+
   |g2g.analysis | no        | Defines optional additional calculations to          |
   |             |           | generate percentile and response time group          |
   |             |           | statistics.                                          |
   +-------------+-----------+------------------------------------------------------+
   | g2g.run     | no        | Controls behavior when g2g is run against the        |
   |             |           | same log files multiple times.                       |
   +-------------+-----------+------------------------------------------------------+
   | logging     | yes       | Standard python logging configuration for            |
   |             |           | the g2g output.                                      |
   |             |           | See                                                  |
   |             |           | http://docs.python.org/2/library/logging.config.html |
   |             |           | for how to configure this section.  The settings     |
   |             |           | provided should be fine in most cases.               |
   +-------------+-----------+------------------------------------------------------+   


Individual Settings
===================

These are the individual settings


   +----------------------------------------+-----------+---------+---------------------------------------+
   | Setting                                | Required? | Default | Notes                                 |
   +========================================+===========+=========+=======================================+                          
   | g2g.carbon.host                        | yes       | none    | Hostname of the Graphite (carbon)     |
   |                                        |           |         | server fo g2g to send data to.        |
   +----------------------------------------+-----------+---------+---------------------------------------+
   | g2g.carbon.port                        | yes       | none    | Port the carbon server listens on.    |
   +----------------------------------------+-----------+---------+---------------------------------------+
   | g2g.carbon.prefix                      | yes       | none    | Can be empty string.  Prefix appears  |
   |                                        |           |         | before the host name in the Graphite  |
   |                                        |           |         | namespace.                            |
   +----------------------------------------+-----------+---------+---------------------------------------+
   | g2g.carbon.suffix                      | yes       | none    | Can be empty string.  Suffix appears  |
   |                                        |           |         | after the host name in the Graphite   |
   |                                        |           |         | namespace.                            |
   +----------------------------------------+-----------+---------+---------------------------------------+
   | g2g.carbon.interval_seconds            | yes       | none    | This should be set at or below the    |
   |                                        |           |         | carbon reporting interval defined on  |
   |                                        |           |         | your graphite server.                 |
   +----------------------------------------+-----------+---------+---------------------------------------+
   | g2g.data.log_file                      | yes       | none    | The path to the Grinder data file on  |
   |                                        |           |         | your local filesystem.  The data file |
   |                                        |           |         | normally has a name like              |
   |                                        |           |         | <hostname>-0-data.log                 |
   +----------------------------------------+-----------+---------+---------------------------------------+
   | g2g.data.mapping_file                  | yes       | none    | The path to the Grinder mapping file  |
   |                                        |           |         | on your local filesystem.  The        |
   |                                        |           |         | mapping file normally has a name like |
   |                                        |           |         | <hostname>-0.log.  The final lines    |
   |                                        |           |         | of a valid mapping file contain a     |
   |                                        |           |         | table summarizing the Grinder run.    |
   +----------------------------------------+-----------+---------+---------------------------------------+
   | g2g.analysis.response_time_percentiles | no        | [ ]     | If this setting is defined, g2g will  | 
   |                                        |           |         | calculate the response times          |
   |                                        |           |         | for the specified percentiles.        |
   |                                        |           |         | Percentile values must be expressed   |
   |                                        |           |         | as a list of numbers between 0.0 and  |
   |                                        |           |         | 1.0                                   |
   +----------------------------------------+-----------+---------+---------------------------------------+
   | g2g.analysis.time_group_milliseconds   | no        | [ ]     | If this setting is defined            |
   |                                        |           |         | g2g will calculate the                |
   |                                        |           |         | percentage of all                     |
   |                                        |           |         | requests that complete                |
   |                                        |           |         | within specified ranges of time.      |
   |                                        |           |         | Time groups must be expressed as a    |
   |                                        |           |         | list of millisecond values.           |
   +----------------------------------------+-----------+---------+---------------------------------------+
   | g2g.run.follow                         | no        | False   | Enable continually watching the       |
   |                                        |           |         | Grinder data file for new entries.    |
   |                                        |           |         | If true, g2g will run forever until   |
   |                                        |           |         | killed or interrupted with ^C.        |
   +----------------------------------------+-----------+---------+---------------------------------------+
   | g2g.run.follow_interval_seconds        | no        | 60      | Specifies how often g2g will report   |
   |                                        |           |         | new data back to Graphite when        |
   |                                        |           |         | follow mode has been enabled.  Should |
   |                                        |           |         | be a multiple of the                  |
   |                                        |           |         | carbon.interval_seconds setting.      |
   +----------------------------------------+-----------+---------+---------------------------------------+
   | g2g.run.resume                         | no        | False   | Read the Grinder data file from the   |
   |                                        |           |         | last read                             |
   |                                        |           |         | location instead of from the          |
   |                                        |           |         | beginning.  This setting is ignored   |
   |                                        |           |         | if follow is enabled.                 |
   +----------------------------------------+-----------+---------+---------------------------------------+



