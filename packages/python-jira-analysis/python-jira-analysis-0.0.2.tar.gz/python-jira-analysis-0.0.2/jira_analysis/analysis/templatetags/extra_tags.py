from django import template

register = template.Library()

def key(d, key_name):
    try:
        value = d[key_name]
    except KeyError:
        from django.conf import settings
        value = settings.TEMPLATE_STRING_IF_INVALID
    return value
key = register.filter('key', key)

def days(sec):
    try:
    	days = sec/86400.0
    	hours = (days - int(days)) * 24.0
    	mins = (hours - int(hours)) * 60.0
    	return "{}d {}h {}m".format(int(days), int(hours), int(mins))
    except:
        return "NaN"
days = register.filter('days', days)

def percent_of(value, total_value):
    try:
        percent = 100.0*value/total_value
    except:
        from django.conf import settings
        percent = settings.TEMPLATE_STRING_IF_INVALID
    return percent
percent_of = register.filter('percent_of', percent_of)
