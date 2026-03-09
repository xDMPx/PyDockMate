from dataclasses import dataclass
from datetime import datetime
from django.db import IntegrityError
from django.utils import timezone
from decimal import Decimal
import json
from uuid import UUID
from django.core.management.base import BaseCommand
from PyDockMate.models import Host
from PyDockMate.models import ContainerStat as ContainerStatModel
from PyDockMate.models import Container as ContainerModel
import asyncio
from dotenv import load_dotenv
import os

from rstream import (
    AMQPMessage,
    Consumer,
    ConsumerOffsetSpecification,
    MessageContext,
    OffsetNotFound,
    OffsetType,
)
# 5GB
STREAM_RETENTION = 5000000000
load_dotenv(".env")
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_USERNAME = os.getenv("RABBITMQ_USERNAME", "admin")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "password")

@dataclass
class ContainerStat:
    container_uuid: str
    status: str
    cpu: float | None
    memory: float | None
    timestamp: float

def parse_container_stat_json(json: dict[str,str]) -> ContainerStat:
    cpu = None
    memory = None
    try:
        cpu = float(json["cpu"])
        memory = float(json["memory"])
    except: pass
    return ContainerStat(
        container_uuid = json["container_uuid"],
        status = json["status"],
        cpu = cpu,
        memory = memory,
        timestamp = float(Decimal(json["timestamp"])),
    ) 

async def consumer(stream_name: str):
    async with Consumer(host=RABBITMQ_HOST, username=RABBITMQ_USERNAME, password=RABBITMQ_PASSWORD) as consumer:
        await consumer.create_stream(stream_name, exists_ok=True, arguments={"max-length-bytes": STREAM_RETENTION})

        async def on_message(msg: AMQPMessage, message_context: MessageContext):
            print("Got message: {} from stream {}".format(msg, message_context.stream))
            msg_str = msg.__bytes__().decode()
            container_stat = parse_container_stat_json(json.loads(msg_str))
            container = await ContainerModel.objects.aget(uuid=container_stat.container_uuid)
            stat = ContainerStatModel(status=container_stat.status, cpu=container_stat.cpu, memory=container_stat.memory, timestamp=timezone.make_aware(datetime.fromtimestamp(container_stat.timestamp)), container=container)
            try:
                await stat.asave()
            except IntegrityError as e:
                print("skipped")
                pass
            offset = message_context.offset
            if message_context.subscriber_name is not None:
                await consumer.store_offset(stream=stream_name,offset=offset,subscriber_name=message_context.subscriber_name)

        stored_offset = 0
        try:
            stored_offset = await consumer.query_offset(stream=stream_name, subscriber_name="subscriber_1")
            print(f"Reusing offset: {stored_offset}")
        except OffsetNotFound as offset_exception:
            print(f"Offset not previously stored. {offset_exception}")

        await consumer.start()
        await consumer.subscribe(
            stream=stream_name,
            subscriber_name="subscriber_1",
            callback=on_message,
            offset_specification=ConsumerOffsetSpecification(OffsetType.OFFSET, stored_offset),
        )
        await consumer.run()

async def main(uuids: list[UUID]):
    consumer_tasks = [consumer(str(uuid)) for uuid in uuids]
    await asyncio.gather(*consumer_tasks)

class Command(BaseCommand):
    def handle(self, *args, **options):
        hosts_uuid = Host.objects.values_list("uuid", flat=True)
        uuids: list[UUID] = [uuid for uuid in hosts_uuid]
        print(f"hosts: {uuids}")
        with asyncio.Runner() as runner:
            runner.run(main(uuids))
