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

class Container(models.Model):
    uuid = models.UUIDField(
        default=uuid.uuid7, primary_key=True
    )
    id = models.CharField(max_length=64)
    image = models.CharField()
    command = models.CharField()
    created = models.DateTimeField()
    ports = models.CharField()
    name = models.CharField()
    host = models.ForeignKey(Host, on_delete=models.CASCADE)

class ContainerStat(models.Model):
    status = models.CharField()
    timestamp = models.DateTimeField()
    container = models.ForeignKey(Container, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['container', 'timestamp'], name='container_timestamp_index')
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['container', 'timestamp'],
                name='unique_container_timestamp'
            )
        ]
