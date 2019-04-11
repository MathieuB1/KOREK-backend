from django.shortcuts import render
from django.utils.safestring import mark_safe
import json
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(('GET',))
def notification(request):
    if request.user.is_authenticated:
        return render(request, 'event/notification.html', {
            'user_json': mark_safe(json.dumps(request.user.id))
        })
    else:
        return Response(status=403)


@api_view(('GET',))
def notif(request):
    if request.user.is_authenticated:

        token = request.META.get('HTTP_AUTHORIZATION', None)
        key = ''
        if token:
            key = token.split('Bearer ')[1]

        return render(request, 'event/registerWS.js', {
            'user_json': mark_safe(json.dumps(request.user.id)),
            'token': mark_safe(json.dumps(key))
        })
    else:
        return Response(status=403)
