import json
from django.http import HttpResponse
from models import ProductsPermissions

def index(request):

    result = {
        'msg': 'hi there!',
    }
    return HttpResponse(json.dumps(result), status=200)


def rows(request):
    all_permissions = ProductsPermissions.objects.all().values()

    result = {
        'rows': [dict(p) for p in all_permissions],
    }
    return HttpResponse(json.dumps(result), status=200)
