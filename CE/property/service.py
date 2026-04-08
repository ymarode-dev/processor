from datetime import datetime
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from connections.redis import RedisClient
from utils.service import BaseService
from .models import Property
from .schemas import PropertyCreate, PropertyUpdate, PropertyRead
from typing import List

class PropertyService:
    def __init__(self):
        self.base: BaseService = BaseService(Property)

    async def get_property(self, session: AsyncSession, filters: dict, redis_client: RedisClient) -> List[PropertyRead]:
        return await self.base.get(session, filters, redis_client)
    
    async def create_property(self, session: AsyncSession, property_data: List[PropertyCreate], redis_client: RedisClient) -> List[PropertyRead]:
        data = []

        for property in property_data:
            d = property.model_dump()  
            d['PROPERTY_ID'] = f"ID{uuid.uuid4()}"  
            d['TARGET'] = f"/{d['PROPERTY_ID']}" 
            data.append(d)

        return await self.base.create(session, data, redis_client)

    async def update_property(self, session: AsyncSession, filters: dict, property_data: PropertyUpdate, redis_client: RedisClient) -> List[PropertyRead] | None:
        updated_count = await self.base.update(
            session,
            filters,
            property_data.model_dump(exclude_unset=True)
        )

        if updated_count == 0:
            return None

        return await self.base.get(session, filters, redis_client)

    async def delete_property(self, session: AsyncSession, filters: dict, redis_client: RedisClient) -> List[PropertyRead] | None:
        properties = await self.base.get(session, filters, redis_client)

        if not properties:
            return None

        await self.base.delete(session, filters, redis_client)
        return properties