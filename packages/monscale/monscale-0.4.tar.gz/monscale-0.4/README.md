monscale
========

Daemond that monitor services and acts on them based on rules. Monscale is a Django app.


The app resides mainly in two commands, the monitor and the actions executor. Also it's got
a web interface to manage its configuration.
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

The Django app can be installed just by issuing the following command, which installs every dependency

```
pip install monscale
```

Once installation is finished it's time to create the Django project under which the app will run. It
is recomended to do this by issuing the following command, as it not only creates the project, but
it also adapts its settings.py file with the configuration needed by the app.

```
monscale_deploy
```

Note that monscale uses Redis list to store some of its operational data, therefore either
install Redis and get it running, or use a predeployed Redis server. 

You'll find the settings needed to connect to the Redis server at the project 
settins.py file.

Don't forget to set the SQL DB and other configurations of your choice.

Finally populate the DB (from project's dir):

```
./manage.py syncdb
```

Usage
-----

To start the monitor daemon just issue the following command at the project's dir:

```
./manage.py evaluate_context
```

To start the actions daemon issue the following command at the project's dir:

```
./manage.py action_worker
```

To start the development web management interface (from project's dir):

```
./manage.py runserver
```

