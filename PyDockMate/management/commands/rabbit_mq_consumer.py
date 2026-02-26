from dataclasses import dataclass
from datetime import datetime
from django.utils import timezone
from decimal import Decimal
import json
from uuid import UUID
from django.core.management.base import BaseCommand
from PyDockMate.models import Host
from PyDockMate.models import ContainerStat as ContainerStatModel
from PyDockMate.models import Container as ContainerModel
import asyncio

from rstream import (
    AMQPMessage,
    Consumer,
    ConsumerOffsetSpecification,
    MessageContext,
    OffsetType,
)
# 5GB
STREAM_RETENTION = 5000000000

@dataclass
class ContainerStat:
    container_uuid: str
    status: str
    timestamp: float

def parse_container_stat_json(json: dict[str,str]) -> ContainerStat:
    return ContainerStat(
        container_uuid = json["container_uuid"],
        status = json["status"],
        timestamp = float(Decimal(json["timestamp"])),
    ) 

async def consumer(stream_name: str):
    async with Consumer(host="localhost", username="admin", password="password") as consumer:
        await consumer.create_stream(stream_name, exists_ok=True, arguments={"max-length-bytes": STREAM_RETENTION})

        async def on_message(msg: AMQPMessage, message_context: MessageContext):
            print("Got message: {} from stream {}".format(msg, message_context.stream))
            msg_str = msg.__bytes__().decode()
            container_stat = parse_container_stat_json(json.loads(msg_str))
            container = await ContainerModel.objects.aget(uuid=container_stat.container_uuid)
            stat = ContainerStatModel(status=container_stat.status, timestamp=timezone.make_aware(datetime.fromtimestamp(container_stat.timestamp)), container=container)
            await stat.asave()

        await consumer.start()
        await consumer.subscribe(
            stream=stream_name,
            callback=on_message,
            offset_specification=ConsumerOffsetSpecification(OffsetType.LAST, None),
        )
        await consumer.run()

async def main(uuids: list[UUID]):
    for uuid in uuids:
        await consumer(str(uuid))
        
class Command(BaseCommand):
    def handle(self, *args, **options):
        hosts_uuid = Host.objects.values_list("uuid", flat=True)
        uuids: list[UUID] = [uuid for uuid in hosts_uuid]
        with asyncio.Runner() as runner:
            runner.run(main(uuids))
