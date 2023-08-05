from django_thermostat.mappings import get_mappings
from pypelib.RuleTable import RuleTable
from django_thermostat.mappings import get_mappings
from django_thermostat.utils import gen_comparing_time
from django_thermostat.models import Rule
import logging
from django.conf import settings

def evaluate_non_themp():
    mappings = get_mappings()
    table = RuleTable(
        "Non thermostat rules",
        mappings,
        "RegexParser",
        #rawfile,
        "RAWFile",
        None)
    table.setPolicy(False)
    for rule in Rule.objects.filter(active=True, thermostat=False).order_by("pk"):
        table.addRule(rule.to_pypelib())
    table.dump()
    try:
        table.evaluate({})
    except Exception, ex:
        print "ERROR: %s" % ex
        pass



def evaluate():

    mappings = get_mappings()
    table = RuleTable(
        "Decide tunned temp",
        mappings,
        "RegexParser",
        #rawfile,
        "RAWFile",
        None)

    logging.debug("current time: %s " % mappings["current_time"]())
    logging.debug("current day of week: %s" % mappings["current_day_of_week"]())
    logging.debug("current temp %s" % mappings["current_internal_temperature"]())
    logging.debug("economic %s" % mappings["economic_temperature"]())
    logging.debug("confort %s" % mappings["confort_temperature"]())
    logging.debug("tuned %s" % mappings["tuned_temperature"]())
    logging.debug("flame %s" % mappings["flame_on"]())
    logging.debug("heat on %s" % mappings["heater_on"]())

    table.setPolicy(False)

    table.addRule("if heater_manual = 1  then accept do tune_to_confort")

    for rule in Rule.objects.filter(active=True, thermostat=True).order_by("pk"):
        table.addRule(rule.to_pypelib())

    if settings.DEBUG:
        table.dump()

    metaObj = {}

    try:
        table.evaluate(metaObj)
    except Exception:
        mappings["tune_to_economic"]()

    table1 = RuleTable(
        "Decide flame status",
        mappings,
        "RegexParser",
        #rawfile,
        "RAWFile",
        None)
    table1.addRule("if heater_on = 0 then deny")
    table1.addRule("if current_internal_temperature < tuned_temperature then accept")
    if settings.DEBUG:
        table1.dump()
        
    try:
        table1.evaluate(metaObj)
        try:
            mappings["start_flame"]()
        except Exception, ex:
            logging.error("ERROR: Cant start flame: %s" % ex)
    except Exception as e:
        try:
            mappings["stop_flame"]()
        except Exception, ex:
            logging.error("ERROR: Cant stop flame: %s" % ex)

