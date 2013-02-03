# -*- encoding: utf-8 -*-

from django.db.models.loading import cache
from django.core import serializers
from django.http import HttpResponse
from django.utils import simplejson

def manage_json(request, model_name=None):
    if model_name:
        model = cache.app_models['Dynamic'][model_name]
        result = serializers.serialize("json", model.objects.all())
    else:
        payload = {'success': True, 'models': cache.app_models['Dynamic'].keys()}
        result = simplejson.dumps(payload)
    return HttpResponse(result, content_type='application/json')
