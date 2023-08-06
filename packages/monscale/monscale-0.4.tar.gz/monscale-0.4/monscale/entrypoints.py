#!/usr/bin/env python
import os, logging, sys, subprocess
#from django.core.management import call_command

SETTINGS = """
import logging
REDIS_DB = 0
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_ACTION_LIST = "monscale_actions"
ACTION_WORKER_SLEEP_SECS = 10
MONITOR_WORKER_SLEEP_SECS = 10
LOG_LEVEL = logging.DEBUG

INSTALLED_APPS += ('monscale', )
"""


def deploy(*args, **kwargs): 
    """
    Deploys the Django project and configures it
    """
    logging.basicConfig(level=logging.INFO)
    subprocess.call(["django-admin.py", "startproject", sys.argv[1]])
    os.chdir(sys.argv[1])
    
    with open(os.path.join(sys.argv[1], "settings.py"), "a") as fw: fw.write(SETTINGS)
    #os.environ.setdefault("DJANGO_SETTINGS_MODULE", "%s.settings" % sys.argv[1])
    logging.info("[monscale_deploy] Django project %s successfuly created at ./%s" % (sys.argv[1], sys.argv[1]))
    
def evaluate_context(*args, **kwargs):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "monscale.settings")

    print os.environ
    call_command("evaluate_context", sys.argv)