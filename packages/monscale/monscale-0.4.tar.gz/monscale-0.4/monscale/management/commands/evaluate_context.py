import logging, time
from django.core.management.base import BaseCommand, CommandError
from monscale.rules import evaluate 
from django.conf import settings


class Command(BaseCommand):
    args = ''
    help = 'Parse de date stats file to retrieve the statistics aggregation for the last N minutes.'



    def handle(self, *args, **options):
#        logging.basicConfig(level=logging.DEBUG)
        
        while True:
            logging.debug("[monitor_worker] starting loop ...")
            evaluate()
            logging.debug("[monitor_worker] sleeping for %ss" % settings.MONITOR_WORKER_SLEEP_SECS)
            time.sleep(settings.MONITOR_WORKER_SLEEP_SECS)
            

