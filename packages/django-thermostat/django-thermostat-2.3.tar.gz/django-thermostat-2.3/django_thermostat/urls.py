from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
#from django.contrib import admin
#admin.autodiscover()

urlpatterns = patterns('',
    
    url(r'^js/context.js$', "django_thermostat.views.context_js", name="context_js"),
    url(r'^read_heat_status$', "django_thermostat.views.read_heat_status", name="read_heat_status"),
    url(r'^toggle_heat_status$', "django_thermostat.views.toggle_heat_status", name="toggle_heat_status"),
    url(r'^bri_temp/(\w+)?$', "django_thermostat.views.bri_temp", name="bri_temp"),
    url(r'^dim_temp/(\w+)?$', "django_thermostat.views.dim_temp", name="dim_temp"),
    url(r'^toggle_heat_manual', "django_thermostat.views.toggle_heat_manual", name="toggle_heat_manual"),
    url(r'^temperatures', "django_thermostat.views.temperatures", name="temperatures"),
    url(r'^set_internal_reference/([\s\d\w\-]+)?/?$', "django_thermostat.views.set_internal_reference", name="set_internal_reference"),
    url(r'^$', "django_thermostat.views.home", name="home"),
)
