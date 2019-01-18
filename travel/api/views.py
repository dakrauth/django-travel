from django.http import JsonResponse
from rest_framework.decorators  import api_view

from .serializers import logs_for_user


@api_view(['GET'])
def log_list(request, username):
    return JsonResponse(logs_for_user(username))

