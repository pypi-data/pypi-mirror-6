from datetime import date

from django import template
from django.conf import settings

register = template.Library()

@register.simple_tag(name="generate_months")
def generate_months():
    months = ["%02d" % (month,) for month in xrange(1, 13)]
    html = ""
    for month in months:
        html += "<option value='{0}'>{0}</option>\n".format(month)
    return html

@register.simple_tag(name="generate_years")
def generate_years():
    year = int(date.today().year)
    html = ""
    for year in xrange(year, year+10):
        html += "<option value='{0}'>{0}</option>\n".format(year)
    return html

@register.simple_tag(name="stripe_publishable_key")
def stripe_publishable_key():
    return settings.STRIPE_API_KEY_PUBLISHABLE