Introduction
============

Buildout recipe for installing Celery for use with Zope's ZCA and configuring
it using an ini file.

This recipe was originally based on collective.recipe.celery,
but differs greatly so that it now has become its own package. This recipe
defines a custom loader that can read celery configuration from an ini file.
This allows you to generate the configuration by using a template for
example, using collective.recipe.template. The custom loader also bootstraps
the ZCA automatically when a worker initializes.

You can use it in a part like this::

    [celery]
    recipe = md.recipe.celery
    eggs =
      ${buildout:eggs}
      celery[redis]
    celery_conf = etc/celery.ini
    logging_conf = etc/logging.ini
    zope_conf = etc/zope.conf


Supported options
=================

General options
---------------

eggs
    A list of additional eggs you want to make available to Celery. Use this to
    add additional dependencies such as ``kombu-sqlalchemy`` or the module(s)
    containing your task definitions.

celery_conf
    Location of the Celery configuration .ini file.

logging_conf
    Location of the file containing the python logging setup

zope_conf
    Location of the zope configuration file.


Configuration
=============

Example of an ini file that could be used by this recipe::

    [celery]
    BROKER_URL = sqlite:///celery_broker.db
    CELERY_IMPORTS = myapp.tasks,otherapp.tasks
    CELERY_RESULT_BACKEND = sqlite:///celery_results.db
    CELERY_RESULT_SERIALIZER = json

    [celerybeat:task1]
    # Execute every hour
    task = myapp.tasks.Task1
    type = crontab
    schedule = {"minute": 0}

    [celerybeat:task2]
    # Execute every 30 seconds
    task = myapp.tasks.Task2
    type = timedelta
    schedule = {"seconds": 30}

    [celerybeat:task3]
    # Execute at midnight
    task = otherapp.tasks.Task3
    type = crontab
    schedule = {"hour": 0, "minute": 0}

The [celery] section defines all the celery options. Every [celerybeat]
section defines an individual task.
