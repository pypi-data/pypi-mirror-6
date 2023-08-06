from django_thermostat.models import Context, Thermometer
from django.shortcuts import render_to_response, redirect
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseServerError
from settings import HEATER_INCREMENT, LIST_THERMOMETERS_API
from django.core.urlresolvers import reverse
from django_thermostat.mappings import get_mappings
from django_thermometer.temperature import read_temperatures
import simplejson, logging
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist


def set_internal_reference(request, tid):

    try:
        therm = Thermometer.objects.get(is_internal_reference=True)
        if therm.tid == tid or therm.caption == tid:
            return HttpResponse("")
        therm.is_internal_reference = None
        therm.save()
    except ObjectDoesNotExist:
	#no previously selected thermostat
	pass
    except Exception, err:
        logging.error("set_internal_reference: %s" % err)

    try:
        therm = Thermometer.objects.get(Q(tid=tid) | Q(caption=tid))
        therm.is_internal_reference = True
        therm.save()
        return HttpResponse("OK")
    except ObjectDoesNotExist:
        return HttpResponseBadRequest("Thermostats %s not found" % tid)
    except Exception, ex:
        logging.error("set_internal_reference: %s" % ex)
        return HttpResponseServerError(ex)


def home(request):
    context = Context.objects.get_or_create(pk=1)

    return render_to_response(
        "therm/home.html",
        {"context": context, },
    )


def temperatures(request):
    therms = read_temperatures()
    known_therms = {}
    for x in Thermometer.objects.all():
        known_therms[x.tid] = [x.caption, x.is_internal_reference]
    out = {}
    for tid, data in therms.items():
        try:
            out[known_therms[tid][0]] = [data, known_therms[tid][1]]
        except KeyError:
            out[tid] = [data, False]

    response = HttpResponse(
        content=simplejson.dumps(out),
        content_type="application/json")
    response['Cache-Control'] = 'no-cache'
    return response


def dim_temp(request, temp):
    context = Context.objects.get()
    if temp == "confort":
        context.confort_temperature = float(context.confort_temperature) - float(HEATER_INCREMENT)
    if temp == "economic":
        context.economic_temperature = float(context.economic_temperature) - float(HEATER_INCREMENT)
    context.save()
    return redirect(reverse("read_heat_status"))


def bri_temp(request, temp):
    context = Context.objects.get()
    if temp == "confort":
        context.confort_temperature = float(context.confort_temperature) + float(HEATER_INCREMENT)
    if temp == "economic":
        context.economic_temperature = float(context.economic_temperature) + float(HEATER_INCREMENT)
    context.save()
    return redirect(reverse("read_heat_status"))


def toggle_heat_manual(request):
    context = Context.objects.get()
    context.manual = not context.manual
    context.save()
    return redirect(reverse("read_heat_status"))


def toggle_heat_status(request):
    context = Context.objects.get()
    context.heat_on = not context.heat_on
    context.save()

    return HttpResponse("")


def read_heat_status(request):
    response = render_to_response(
        "therm/context.json",
        {"data": Context.objects.get().to_json()},
        content_type="application/json",
    )
    response['Cache-Control'] = 'no-cache'
    return response


def context_js(request):
    return render_to_response(
        "context.js",
        {"temperatures_uri": LIST_THERMOMETERS_API, },
        content_type="application/javascript")
