from django.views.generic import View
from django.http import HttpResponse
import json
import re

# Create your views here.

models_list = {}

class Dispatch(View):
    def get(self, *args, **kwargs):
        data = {'error': '','response': ''}
        if kwargs.get('model') in models_list:
            model = models_list[kwargs.get('model')]['model']
            if re.match("^\d+?\.\d+?$", kwargs.get('timestamp')):
                timestamp = float(kwargs.get('timestamp'))
                query = model.objects.get_all().filter(timestamp__gt=timestamp)
                data['response'] = [item.serialize() for item in query]
            else:
                data['error'] = 'invalid timestamp (cannot convert to float)'
        else:
            data['error'] = 'invalid model name'
        return HttpResponse(json.dumps(data))

    def post(self, *args, **kwargs):
        model = models_list[kwargs.get('model')]['model']
        if model:
            if model.to_obj:
                obj = model.to_obj(self.request.body)
                obj.save()
            else:
                serializer = model.serializer_class(data=json.loads(self.request.body))
                if serializer.is_valid():
                    serializer.object.save()
        return HttpResponse()
