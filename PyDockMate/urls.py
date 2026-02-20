"""
URL configuration for PyDockMate project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path

from .views import (
    AgentHeartbeatView,
    AgentRegisterView,
    ContainerDestroyView,
    ContainerRegisterView,
    HostContainersListView,
    HostListView,
    agent_host_uuid,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    path("api/agent/register", AgentRegisterView.as_view()),
    path("api/agent/<uuid:agent_uuid>/heartbeat/", AgentHeartbeatView.as_view()),
    path("api/agent/<uuid:agent_uuid>/host", agent_host_uuid),
    path("api/hosts/", HostListView.as_view()),
    path("api/host/<uuid:host_uuid>/container/register", ContainerRegisterView.as_view()),
    path("api/host/<uuid:host_uuid>/container/<uuid:pk>/destroy", ContainerDestroyView.as_view()),
    path("api/host/<uuid:host_uuid>/containers", HostContainersListView.as_view()),
]
