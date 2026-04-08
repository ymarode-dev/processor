from datetime import datetime
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from connections.redis import RedisClient
from .models import Room
from .schemas import RoomCreate, RoomUpdate, RoomRead
from utils.service import BaseService
from typing import List, Optional

class RoomService:
    def __init__(self):
        self.base: BaseService = BaseService(Room)

    async def get_rooms(self, session: AsyncSession, filters: dict, redis_client: RedisClient) -> List[RoomRead]:
        return await self.base.get(session, filters, redis_client)

    async def create_room(self, session: AsyncSession, room_data: List[RoomCreate], redis_client: RedisClient) -> List[RoomRead]:
        data = []

        for room in room_data:
            d = room.model_dump()
            d['ROOM_ID'] = f"ID{uuid.uuid4()}"
            d['TARGET'] = f"/{d['TARGET']}/{d['ROOM_ID']}"
            data.append(d)

        return await self.base.create(session, data, redis_client)

    async def update_room(self, session: AsyncSession, filters: dict, room_data: RoomUpdate, redis_client: RedisClient) -> List[RoomRead] | None:
        updated_count = await self.base.update(
            session,
            filters,
            room_data.model_dump(exclude_unset=True)
        )

        if updated_count == 0:
            return None

        return await self.base.get(session, filters, redis_client)

    async def delete_room(self, session: AsyncSession, filters: dict, redis_client: RedisClient) -> List[RoomRead] | None:
        rooms = await self.base.get(session, filters, redis_client)

        if not rooms:
            return None

        await self.base.delete(session, filters, redis_client)
        return rooms