from django.core.management.base import BaseCommand, CommandError
from django_thermostat.rules import evaluate
from time import localtime, strftime, sleep
import threading, logging

class Command(BaseCommand):
    args = '<sleep_time>'

    help = 'Evaluate rules realted to heater status. The result will start or stop the heater. It will loop and sleep for sleep_time seconds'

    
    def handle(self, *args, **options):
        try:
            if len(args) != 1:
                raise ValueError("Missing sleep_time")
            while(True):
                logging.debug("Starting at %s" % strftime("%d.%m.%Y %H:%M:%S", localtime()))
                thread = threading.Thread(target=evaluate)
                thread.start()
                thread.join()
                logging.debug("Child thread finished, sleeping for the next %s seconds" % args[0])
                sleep(float(args[0]))

        except Exception, ex:
            self.stderr.write("ERROR: %s" % ex)

    

        