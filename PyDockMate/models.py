from django.db import models
import uuid

class Host(models.Model):
    uuid = models.UUIDField(
        default=uuid.uuid7, primary_key=True
    )
    hostname = models.CharField(max_length=255)
    os = models.CharField(max_length=255)
    docker_version = models.CharField(max_length=255)

class Agent(models.Model):
    uuid = models.UUIDField(
        default=uuid.uuid7, primary_key=True
    )
    version = models.CharField(max_length=12)
    last_heartbeat = models.DateTimeField(auto_now_add=True)
    host = models.OneToOneField(
        Host,
        on_delete=models.CASCADE,
    )
