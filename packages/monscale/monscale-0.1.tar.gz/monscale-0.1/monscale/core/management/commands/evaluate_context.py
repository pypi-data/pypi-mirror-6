import logging
from django.core.management.base import BaseCommand, CommandError
from core.rules import evaluate 

class Command(BaseCommand):
    args = ''
    help = 'Parse de date stats file to retrieve the statistics aggregation for the last N minutes.'



    def handle(self, *args, **options):
#        logging.basicConfig(level=logging.DEBUG)
        
        evaluate()
            
