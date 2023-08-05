Where Is My Stuff?
******************
When everything is working properly, your metrics will appear in 
Graphite under the following namespace:

Non-Http Tests
==============
::

    <optional carbon prefix>
        <hostname>
            <optional carbon suffix>
                <test name>
                    per_second
                        tx_passed
                        tx_failed
                    latency
                        mean
                        percentile
                            <specific percentiles defined in config>
                        group
                            <response time groups defined in config>
                

Http Tests
==========
::

    <optional carbon prefix>
        <hostname>
            <optional carbon suffix>
                <test name>
                    per_second
                        bytes_downloaded
                        tx_passed
                        tx_failed
                        new_connections
                        http_status
                            rc_200
                            rc_302
                            rc_404
                            ...
                    latency
                        mean_time
                        percentile
                            <specific percentiles defined in config>
                        group
                            <response time groups defined in config>
                        http
                            resolve_host
                                mean_time
                            establish_connection
                                mean_time
                            first_byte
                                mean_time  


