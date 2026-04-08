from sqlalchemy.ext.asyncio import AsyncSession
from .models import Devices
from .schemas import DeviceCreate, DeviceUpdate, DeviceRead
from typing import List
from utils.service import BaseService
from connections.redis import RedisClient
import uuid

class DeviceService:
    def __init__(self):
        self.base: BaseService = BaseService(Devices)

    async def get_devices(self, session: AsyncSession, filters: dict, redis_client: RedisClient) -> List[DeviceRead]:
        return await self.base.get(session, filters, redis_client)

    async def create_device(self, session: AsyncSession, device_data: List[DeviceCreate], redis_client: RedisClient) -> List[DeviceRead]:
        data = []

        for device in device_data:
            d = device.model_dump()  
            d['DEVICE_ID'] = f"ID{uuid.uuid4()}"  
            d['TARGET'] = f"/{d['TARGET']}/{d['DEVICE_ID']}" 
            data.append(d)

        return await self.base.create(session, data, redis_client)

    async def update_device(self, session: AsyncSession, filters: dict, device_data: DeviceUpdate, redis_client: RedisClient) -> List[DeviceRead] | None:
        updated_count = await self.base.update(
            session,
            filters,
            device_data.model_dump(exclude_unset=True)
        )

        if updated_count == 0:
            return None

        return await self.base.get(session, filters, redis_client)

    async def delete_device(self, session: AsyncSession, filters: dict, redis_client: RedisClient) -> List[DeviceRead] | None:
        devices = await self.base.get(session, filters, redis_client)

        if not devices:
            return None

        await self.base.delete(session, filters, redis_client)
        return devices