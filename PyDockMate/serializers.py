from rest_framework import serializers

from .models import Agent, Host, Container


class HostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Host
        fields = ["uuid", "hostname", "os", "docker_version"]
        read_only_fields = ["uuid"]


class HostWithAgentSerializer(serializers.ModelSerializer):
    class AgentSerializer(serializers.ModelSerializer):
        class Meta:
            model = Agent
            fields = ["version", "last_heartbeat"]
            read_only_fields = ["version", "last_heartbeat"]
    agent = AgentSerializer()

    class Meta:
        model = Host
        fields = [
            "uuid",
            "hostname",
            "os",
            "docker_version",
            "agent",
        ]
        read_only_fields = [
            "uuid",
            "hostname",
            "os",
            "docker_version",
            "agent",
        ]


class AgentSerializer(serializers.ModelSerializer):
    host = HostSerializer()

    class Meta:
        model = Agent
        fields = ["uuid", "version", "last_heartbeat", "host"]
        read_only_fields = ["uuid", "last_heartbeat"]

    def create(self, validated_data):
        if "host" not in validated_data:
            raise serializers.ValidationError({"host": "required"})
        host_data = validated_data.pop("host")
        host = Host.objects.create(**host_data)
        agent = Agent.objects.create(host=host, **validated_data)
        return agent

    def update(self, instance, validated_data):
        host_data = validated_data.pop("host", None)
        if host_data:
            host_serializer = HostSerializer(
                instance=instance.host, data=host_data, partial=True
            )
            host_serializer.is_valid(raise_exception=True)
            host_serializer.save()
        return super().update(instance, validated_data)

class ContainerSerializer(serializers.ModelSerializer):
     class Meta:
        model = Container
        fields = ["uuid", "id", "image", "command", "created", "ports", "name", "host"]
        read_only_fields = ["uuid", "host"]
