from sqlalchemy.ext.asyncio import AsyncSession
from connections.mqtt import MqttClient
from .models import Devices
from .schemas import DeviceCreate, DeviceUpdate, DeviceRead
from .device_configuration import DeviceConfiguration
from typing import List
from utils.service import BaseService
from connections.redis import RedisClient
import uuid

class DeviceService:
    def __init__(self):
        self.base: BaseService = BaseService(Devices)
        self.config: DeviceConfiguration = DeviceConfiguration()

    async def get_devices(self, session: AsyncSession, filters: dict, redis_client: RedisClient) -> List[DeviceRead]:
        return await self.base.get(session, filters, redis_client)

    async def create_device(self, session: AsyncSession, device_data: List[DeviceCreate], redis_client: RedisClient, hub_mqtt_client: MqttClient) -> List[DeviceRead]:
        data = []

        for device in device_data:
            d = device.model_dump()  
            d['DEVICE_ID'] = f"ID{uuid.uuid4()}"  
            d['TARGET'] = f"/{d['TARGET']}/{d['DEVICE_ID']}" 
            data.append(d)

        result = await self.base.create(session, data, redis_client)

        if result:
            await self.config.create_device_config(result, hub_mqtt_client)
        return result

    async def update_device(self, session: AsyncSession, filters: dict, device_data: DeviceUpdate, redis_client: RedisClient, hub_mqtt_client: MqttClient) -> List[DeviceRead] | None:
        updated_count = await self.base.update(
            session,
            filters,
            device_data.model_dump(exclude_unset=True)
        )

        if updated_count == 0:
            return None

        result = await self.base.get(session, filters, redis_client)

        if result:
            await self.config.update_device_config(result, hub_mqtt_client)
        return result


    async def delete_device(self, session: AsyncSession, filters: dict, redis_client: RedisClient, hub_mqtt_client: MqttClient) -> List[DeviceRead] | None:
        devices = await self.base.get(session, filters, redis_client)

        if not devices:
            return None

        await self.base.delete(session, filters, redis_client)
        
        await self.config.delete_device_config(devices, hub_mqtt_client)
        return devices

    async def get_device_by_id(self, session: AsyncSession, device_id: str, redis_client: RedisClient) -> DeviceRead | None:
        filters = {"DEVICE_ID": device_id}
        devices = await self.base.get(session, filters, redis_client)
        return devices[0] if devices else None