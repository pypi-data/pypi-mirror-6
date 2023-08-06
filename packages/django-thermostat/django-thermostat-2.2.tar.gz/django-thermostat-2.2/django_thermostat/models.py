from django.db import models
import simplejson
from time import localtime, strftime
import re
from django_thermostat.utils import gen_comparing_time
from django_thermometer.temperature import read_temperatures


class Thermometer(models.Model):

    tid = models.CharField(max_length=30, unique=True)
    caption = models.CharField(max_length=30, null=True, blank=True, unique=True)
    is_internal_reference = models.NullBooleanField(unique=True)

    def __unicode__(self):
        return u"%s" % self.caption if self.caption is not None else self.tid

    def read(self, ):
        return read_temperatures(self.tid)[self.tid]["celsius"]


class Context(models.Model):
    confort_temperature = models.DecimalField(default=22, decimal_places=2, max_digits=4)
    economic_temperature = models.DecimalField(default=18, decimal_places=2, max_digits=4)
    tuned_temperature = models.DecimalField(null=True, blank=True, decimal_places=2, max_digits=4)

    heat_on = models.BooleanField(default=False)
    manual = models.BooleanField(default=True)
    flame = models.BooleanField(default=False)

    def to_json(self, ):

        return simplejson.dumps({
            "status": "ON" if self.heat_on else "OFF",
            "confort": self.confort_temperature,
            "economic": self.economic_temperature,
            "manual": self.manual,
            "flame": self.flame,
            "tuned": self.tuned_temperature,
            "time": "%s" % strftime("%H:%M:%S", localtime()),
        })


class Day(models.Model):
    name = models.CharField(max_length=10)
    value = models.CharField(max_length=3)

    def __unicode__(self, ):
        return u"%s" % self.name

    def to_pypelib(self, ):
        return u"(current_day_of_week = %s)" % self.value


class TimeRange(models.Model):
    start = models.TimeField()
    end = models.TimeField()

    def __unicode__(self, ):
        return u"%s - %s" % (self.start, self.end)

    def start_to_comparing(self, ):
        return u"%s" % gen_comparing_time(
            self.start.hour,
            self.start.minute,
            self.start.second,
        )

    def end_to_comparing(self, ):
        return u"%s" % gen_comparing_time(
            self.end.hour,
            self.end.minute,
            self.end.second,
        )

    def to_pypelib(self, ):
        #((current_time > %f) && (current_time < %f))
        return u"((current_time > %s ) && (current_time < %s))" % (
            self.start_to_comparing(),
            self.end_to_comparing())


TEMP_CHOICES = (
    ("tune_to_confort", "Confort"),
    ("tune_to_economic", "Economic"),

    ("salon_on", "Subir salon"),
    ("salon_off", "Bajar salon"),

    ("pasillo_off", "Bajar pasillo"),
    ("pasillo_on", "Subir pasillo"),

    ("cuarto_oeste_off", "Bajar pasillo oeste"),
    ("cuarto_oeste_on", "Subir pasillo oeste"),

    ("cuarto_este_off", "Bajar pasillo este"),
    ("cuarto_este_on", "Bajar pasillo este"),
    ("a_lights_on", "Subir grupo A"),
    ("a_lights_off", "Bajar grupo A"),
    ("set_heater_off", "Apagar caldera"),
    ("set_heater_on", "Encender caldera"),
)


COND_CHOICES = (
    ("is_at_night", "Is at night"),
)

class Conditional(models.Model):
    statement = models.CharField(max_length=60,choices=COND_CHOICES)
    ocurred = models.BooleanField(default=False)
    
    def __unicode__(self):
        return u"%s" % self.statement
    
    def to_pypelib(self):
        return u"(%s = 1)" % self.statement


class Rule(models.Model):

    days = models.ManyToManyField(Day, null=True, blank=True)
    ranges = models.ManyToManyField(TimeRange, null=True, blank=True)
    conditionals = models.ManyToManyField(Conditional, null=True, blank=True)
    action = models.CharField(max_length=25, choices=TEMP_CHOICES, default="economic_temperature")
    active = models.BooleanField(default=True)
    thermostat = models.BooleanField(default=False)

    def __unicode__(self, ):
        return "[%s] therm: %s; days: %s; time ranges: %s; conditionals: %s; action: %s" % (
            self.active,
            self.thermostat,
            self.days.all(),
            self.ranges.all(),
            self.conditionals.all(),
            self.action,
        )

    def to_pypelib(self, ):
        if self.thermostat:
            out = "if (heater_manual = 0 ) && "
        else:
            out = "if "
        days = self.days.all()
        ranges = self.ranges.all()
        conds = self.conditionals.all()
        
        if days.count():
            out = "%s (" % out
            for day in days:
                out = "%s %s || " % (out, day.to_pypelib())
            out = re.sub("\|\|\s$", " ) &&", out)

        if ranges.count():
            out = "%s (" % out
            for trang in ranges.all():
                out = "%s %s || " % (out,  trang.to_pypelib())

            out = re.sub("\|\|\s$", ") &&", out)
        
        if conds.count():
            out = "%s (" % out
            for c in conds:
                out = "%s %s || " % (out, c.to_pypelib())
                
            out = re.sub("\|\|\s$", ") &&", out)
        out = re.sub("&&$", "", out)    
        if ranges.count() == 0 and days.count() == 0 and conds.count() == 0:
            out = "%s 1 = 1 " % out
        
        return "%s then accept do %s" % (out, self.action)
