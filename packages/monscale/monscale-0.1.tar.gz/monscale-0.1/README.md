monscale
========

Daemond that monitor services and acts on them based on rules


The project resides mainly in two commands, the monitor and the actions executor.
The monitor is a loop that retrieves from the DB the info about the MonitoredServices.

Each MonitoredService is the relation of:

    - A metric.
    - A condition for that metric
    - A time the condition must be True
    - An action must be triggered if the condition was True more seconds than the 
    shown by the threshold.
    
When an action is triggered, its queued in a Redis list.

The Action Executor is a daemon that collects the actions queued at the Redis list 
and executes them.


Installation
------------


    