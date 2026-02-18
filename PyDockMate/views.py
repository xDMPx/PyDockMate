from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Agent, Host
from .serializers import AgentSerializer, HostWithAgentSerializer


class AgentRegisterView(APIView):
    def post(self, request, format=None):
        print(request.data)
        serializer = AgentSerializer(data=request.data)
        if serializer.is_valid():
            agent = serializer.save()
            return Response(AgentSerializer(agent).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HostListView(ListAPIView):
    queryset = Host.objects.select_related("agent")
    serializer_class = HostWithAgentSerializer
