from django import template
from django.contrib.humanize.templatetags.humanize import intcomma

register = template.Library()

def currency(amount):
    dollars = round(float(amount), 2)
    return "%s%s" % (intcomma(int(amount)), ("%0.2f" % amount)[-3:])

register.filter('currency', currency)
