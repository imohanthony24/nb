from django import template
from django.utils.html import mark_safe
# find out what mark_safe does


register = template.Library()

@register.simple_tag()
def get_model_doc(obj):
	return mark_safe(obj.__doc__)

@register.simple_tag()
def ref_numb(slug):
	return slug.split('-')[0].upper()