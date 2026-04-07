import json
import asyncio
import logging
from aiomqtt import Client, MqttError, Will
from typing import List
from datetime import datetime
from config import settings
from mqtt_invoker import MqttInvoker

class MqttClient:
    _logger = logging.getLogger("MqttClient")

    def __init__(
        self,
        broker: str,
        port: int,
        username: str = None,
        password: str = None,
        client_id: str = "MqttClient",
        topics: List[str] = None,
    ):
        self.broker = broker
        self.port = port
        self.username = username
        self.password = password
        self.client_id = client_id
        self.topics = topics or []
        self.retry_delay = 2

        self.client: Client | None = None
        self.connected = asyncio.Event()
        self._stop = False

    async def connect_mqtt(self):
        while not self._stop:
            try:
                client = Client(
                    hostname=self.broker,
                    port=self.port,
                    identifier=self.client_id,
                    username=self.username,
                    password=self.password,
                    keepalive=120,
                    will=Will(
                        "process/status/edgeprocessor",
                        json.dumps({
                            "action": "disconnected",
                            "ts": int(datetime.now().timestamp() * 1000),
                        }).encode(),
                        qos=1,
                    ),
                )

                async with client:
                    self.client = client
                    self.connected.set()
                    self._logger.info(f"MQTT client {self.client_id} connected to {self.broker}:{self.port}")

                    if self.topics:
                        await client.subscribe(self.topics)
                        self._logger.info(f"Subscribed: {self.topics}")

                    async for message in client.messages:
                        asyncio.create_task(self.handle_message(message))

            except MqttError as e:
                self._logger.error(f"MQTT error: {e}", exc_info=True)

            finally:
                self.connected.clear()
                self.client = None
                await asyncio.sleep(self.retry_delay)

    async def handle_message(self, message):
        try:
            payload = json.loads(message.payload.decode())
            topic = str(message.topic)

            self._logger.debug(f"{topic} -> {payload}")
            await MqttInvoker(self.client).process_message(topic, payload)
        except Exception as e:
            self._logger.error(f"Message handling failed: {e}", exc_info=True)

    async def publish(self, topic: str, payload: dict, qos=1, retain=False):
        await self.connected.wait()

        try:
            await self.client.publish(topic, json.dumps(payload), qos=qos, retain=retain)
        except Exception as e:
            self._logger.error(f"Publish failed: {e}", exc_info=True)

    async def stop(self):
        self._stop = True


class MqttClientRegistry:
    hub: MqttClient = None
    control: MqttClient = None

    @classmethod
    def set_hub(cls, client: MqttClient):
        cls.hub = client

    @classmethod
    def set_control(cls, client: MqttClient):
        cls.control = client

    @classmethod
    def get_hub(cls) -> MqttClient:
        if not cls.hub:
            raise RuntimeError("Hub MQTT not initialized")
        return cls.hub

    @classmethod
    def get_control(cls) -> MqttClient:
        if not cls.control:
            raise RuntimeError("Control MQTT not initialized")
        return cls.control


class MqttPublisher:

    @staticmethod
    async def send_process_percentage(perc: int):
        client = MqttClientRegistry.get_hub()

        payload = {
            "type": "send_percentage",
            "data": {
                "percentage": perc,
                "ts": int(datetime.now().timestamp() * 1000),
            }
        }

        await client.publish("percentage/send", payload)

    @staticmethod
    async def send_process_status(status: str):
        client = MqttClientRegistry.get_control()

        payload = {
            "type": "mqtt_connection_status",
            "action": status,
            "ts": int(datetime.now().timestamp() * 1000),
        }

        await client.publish("process/status/devicecontroller", payload)


async def init_mqtt():
    hub = MqttClient(
        broker=settings.MQTT_HOST,
        port=settings.MQTT_PORT,
        username=settings.MQTT_USERNAME,
        password=settings.MQTT_PASSWORD,
        client_id="edgeProcessorHub",
        topics=[
            ("processor/health/hub", 1),
        ],
    )

    control = MqttClient(
        broker=settings.MQTT_HOST,
        port=settings.MQTT_PORT,
        username=settings.MQTT_USERNAME,
        password=settings.MQTT_PASSWORD,
        client_id="edgeProcessorControl",
        topics=[
            ("processor/health/control", 1),
            ],
    )

    MqttClientRegistry.set_hub(hub)
    MqttClientRegistry.set_control(control)

    asyncio.create_task(hub.connect_mqtt())
    asyncio.create_task(control.connect_mqtt())

    await hub.connected.wait()
    await MqttPublisher.send_process_percentage(100)

    await control.connected.wait()
    await MqttPublisher.send_process_status("running")