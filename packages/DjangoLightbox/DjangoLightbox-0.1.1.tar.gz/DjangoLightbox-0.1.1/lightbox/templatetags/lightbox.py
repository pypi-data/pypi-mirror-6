from django import template
import base64

register = template.Library()

@register.simple_tag
def decode(value):
	return base64.b64decode(value)
    

# http://stackoverflow.com/questions/4698220/django-template-convert-python-list-into-a-javascript-object    
from django.core.serializers import serialize
from django.db.models.query import QuerySet
try:
    from django.utils import simplejson as json
except:
    import json
from django.utils.safestring import mark_safe

def jsonify(object):
    if isinstance(object, QuerySet):
        return mark_safe(serialize('json', object))
    return mark_safe(json.dumps(object))

register.filter('jsonify', jsonify)
jsonify.is_safe = True  
