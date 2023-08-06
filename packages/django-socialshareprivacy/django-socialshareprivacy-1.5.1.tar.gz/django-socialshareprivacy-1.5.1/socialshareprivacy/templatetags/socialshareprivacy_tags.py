from django import template
from django.conf import settings

register = template.Library()


@register.inclusion_tag('socialshareprivacy/socialshareprivacy.html')
def socialshareprivacy(selector='#socialshareprivacy'):
    return {'selector': selector, 'STATIC_URL' : settings.STATIC_URL }