from rest_framework.views import APIView
from rest_framework.response import Response

from . import serializers


class LogListView(APIView):

    def get(self, request, username):
        return Response(serializers.logs_for_user(username))


class FlagGameView(APIView):

    def get(self, request):
        serializer = serializers.FlagSerializer()
        return Response(serializer.data)
