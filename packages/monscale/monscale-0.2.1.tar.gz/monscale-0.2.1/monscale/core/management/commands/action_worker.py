import logging, redis, time
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from core.models import ScaleAction

class Command(BaseCommand):
    args = ''
    help = 'Retrieve queued actions and execute them.'



    def handle(self, *args, **options):
#        logging.basicConfig(level=logging.DEBUG)
        
        while True:
            logging.debug("[action_worker] starting loop ...")
            r = redis.StrictRedis(
                host=settings.REDIS_HOST, 
                port=settings.REDIS_PORT, 
                db=settings.REDIS_DB)
            
            while True:                
                action = r.rpop(settings.REDIS_ACTION_LIST)
                if action is None: break
                
                logging.debug("[action_worker] retrieved action: %s" % action)
                
                action = ScaleAction.from_redis(action)
                logging.debug("[action_worker] populated action: %s" % action)
            logging.debug("[action_worker] going to sleep for %ss" % settings.ACTION_WORKER_SLEEP_SECS)
            time.sleep(settings.ACTION_WORKER_SLEEP_SECS)
