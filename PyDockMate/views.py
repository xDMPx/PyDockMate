from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.generics import CreateAPIView, DestroyAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Agent, Container, Host
from .serializers import AgentSerializer, ContainerSerializer, HostWithAgentSerializer


class AgentRegisterView(APIView):
    def post(self, request, format=None):
        print(request.data)
        serializer = AgentSerializer(data=request.data)
        if serializer.is_valid():
            agent = serializer.save()
            return Response(AgentSerializer(agent).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AgentHeartbeatView(APIView):
    def put(self, request, agent_uuid, format=None):
        agent = get_object_or_404(Agent, uuid=agent_uuid)
        agent.last_heartbeat = timezone.now()
        agent.save(update_fields=["last_heartbeat"])
        return Response(AgentSerializer(agent).data, status=status.HTTP_200_OK)


class HostListView(ListAPIView):
    queryset = Host.objects.select_related("agent").prefetch_related("container_set")
    serializer_class = HostWithAgentSerializer

class ContainerRegisterView(CreateAPIView):
    serializer_class = ContainerSerializer

    def perform_create(self, serializer):
        host = get_object_or_404(Host, uuid=self.kwargs["host_uuid"]) 
        serializer.save(host=host)

class HostContainersListView(ListAPIView):
    serializer_class = ContainerSerializer

    def get_queryset(self):
        host = get_object_or_404(Host, uuid=self.kwargs["host_uuid"]) 
        return Container.objects.select_related("host").filter(host=host)

class ContainerDestroyView(DestroyAPIView):
    queryset = Container.objects.all()
    serializer = ContainerSerializer

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)

@api_view(["GET"])
def agent_host_uuid(request, agent_uuid):
    agent = get_object_or_404(Agent.objects.select_related("host"), uuid=agent_uuid)
    return Response({"host_uuid": agent.host.uuid})
