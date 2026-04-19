from time import time
from typing import List
from device.schemas import DeviceRead
from connections.mqtt import MqttClient


class DeviceConfiguration:
    async def create_device_config(self, devices: List[DeviceRead], hub_mqtt_client: MqttClient):
        await self.send_provision_request(devices, hub_mqtt_client)
        await self.add_device_to_control_cache(devices)
        await self.add_device_to_schedule_cache(devices, hub_mqtt_client)

    async def update_device_config(self, devices: List[DeviceRead], hub_mqtt_client: MqttClient):
        await self.send_update_request(devices, hub_mqtt_client)
        await self.update_device_in_control_cache(devices)
        await self.update_device_in_schedule_cache(devices, hub_mqtt_client)

    async def delete_device_config(self, devices: List[DeviceRead], hub_mqtt_client: MqttClient):
        await self.send_delete_request(devices, hub_mqtt_client)
        await self.delete_device_from_control_cache(devices)
        await self.delete_device_from_schedule_cache(devices, hub_mqtt_client)

    async def send_provision_request(self, devices: List[DeviceRead], hub_mqtt_client: MqttClient):
        response = {
            "data" : devices,
            "type" : "add_device",
            "communicationId" : "provision_device"+str(time.time()) ,
        }
        await hub_mqtt_client.publish('device/provision', response)

    async def send_update_request(self, devices: List[DeviceRead], hub_mqtt_client: MqttClient):
        response = {
            "data" : devices,
            "type" : "update_device",
            "communicationId" : "update_device"+str(time.time()) ,
        }
        await hub_mqtt_client.publish('device/update', response)

    async def send_delete_request(self, devices: List[DeviceRead], hub_mqtt_client: MqttClient):
        response = {
            "data" : devices,
            "type" : "delete_device",
            "communicationId" : "delete_device"+str(time.time()) ,
        }
        await hub_mqtt_client.publish('device/delete', response)

    async def add_device_to_control_cache(self, devices: List[DeviceRead]):
        pass

    async def update_device_in_control_cache(self, devices: List[DeviceRead]):
        pass

    async def delete_device_from_control_cache(self, devices: List[DeviceRead]):
        pass

    async def add_device_to_schedule_cache(self, devices: List[DeviceRead], hub_mqtt_client: MqttClient):
        pass

    async def update_device_in_schedule_cache(self, devices: List[DeviceRead], hub_mqtt_client: MqttClient):
        pass

    async def delete_device_from_schedule_cache(self, devices: List[DeviceRead], hub_mqtt_client: MqttClient):
        pass