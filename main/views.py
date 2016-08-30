import json
from django.http import HttpResponse


def index(request):
    result = {
        'msg': 'hi there!',
    }
    return HttpResponse(json.dumps(result), status=200)