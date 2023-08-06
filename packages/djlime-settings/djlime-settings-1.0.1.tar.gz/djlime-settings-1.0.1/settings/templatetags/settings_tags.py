from django import template
from django.utils.html import mark_safe

from settings.models import Setting


register = template.Library()


@register.simple_tag
def get_config(key):
    try:
        return Setting.objects.get(key=key).value
    except Setting.DoesNotExist:
        return ''


@register.assignment_tag
def get_configs():
    return dict((setting.key, mark_safe(setting.value))
                for setting in Setting.objects.only('key', 'value'))