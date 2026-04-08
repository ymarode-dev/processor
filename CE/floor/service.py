from datetime import datetime
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from utils.service import BaseService
from connections.redis import RedisClient
from .models import Floor
from .schemas import FloorCreate, FloorUpdate, FloorRead
from sqlmodel import delete, select
from typing import List, Optional

class FloorService:
    def __init__(self):
        self.base: BaseService = BaseService(Floor)

    async def get_floors(self, session: AsyncSession, filters: dict, redis_client: RedisClient) -> List[FloorRead]:
        return await self.base.get(session, filters, redis_client)
    
    async def create_floor(self, session: AsyncSession, floor_data: List[FloorCreate], redis_client: RedisClient) -> List[FloorRead]:
        data = []

        for floor in floor_data:
            d = floor.model_dump()  
            d['FLOOR_ID'] = f"ID{uuid.uuid4()}"  
            d['TARGET'] = f"/{d['TARGET']}/{d['FLOOR_ID']}" 
            data.append(d)

        return await self.base.create(session, data, redis_client)
    
    async def update_floor(self, session: AsyncSession, filters: dict, floor_data: FloorUpdate, redis_client: RedisClient) -> List[FloorRead] | None:
        updated_count = await self.base.update(
            session,
            filters,
            floor_data.model_dump(exclude_unset=True)
        )

        if updated_count == 0:
            return None

        return await self.base.get(session, filters, redis_client)

    async def delete_floor(self, session: AsyncSession, filters: dict, redis_client: RedisClient) -> List[FloorRead] | None:
        floors = await self.base.get(session, filters, redis_client)

        if not floors:
            return None

        await self.base.delete(session, filters, redis_client)
        return floors